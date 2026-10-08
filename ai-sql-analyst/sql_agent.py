"""Natural-language SQL generation and result analysis using a hosted API."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

load_dotenv()


class QueryPlan(BaseModel):
    sql: str = Field(description="A single SQLite SELECT query")
    explanation: str = Field(description="Briefly explain what the query measures")
    chart_type: str = Field(description="bar, line, scatter, pie, or table")
    x_column: str | None = None
    y_column: str | None = None


def _client(api_key: str | None = None, base_url: str | None = None) -> OpenAI:
    key = api_key or os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("Add a provider API key in the sidebar or set AI_API_KEY in .env.")
    configured_url = os.getenv("AI_BASE_URL") or os.getenv("OPENAI_BASE_URL", "")
    resolved_base_url = (base_url if base_url is not None else configured_url).strip()
    # An empty base URL can be interpreted as a relative URL by the SDK.
    # Use the standard endpoint by default and honor only a nonempty override.
    return OpenAI(
        api_key=key,
        base_url=resolved_base_url or "https://api.openai.com/v1",
    )


def _model(model: str | None = None) -> str:
    configured_model = os.getenv("AI_MODEL") or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return (model or configured_model).strip()


def generate_query(
    question: str,
    schema: str,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
) -> QueryPlan:
    """Generate a schema-grounded query and parse it into a typed plan."""
    client = _client(api_key, base_url)
    response = client.chat.completions.create(
        model=_model(model),
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": (
                "You translate natural-language analytics questions into SQLite SELECT queries. "
                "Use only tables and columns in the supplied schema. Never write or modify data. "
                "Return JSON with keys sql, explanation, chart_type, x_column, y_column. "
                "chart_type must be bar, line, scatter, pie, or table. Choose table if charting is not useful. "
                "Use clear aliases for output columns. Do not include markdown."
            )},
            {"role": "user", "content": f"Schema:\n{schema}\n\nQuestion: {question}"},
        ],
    )
    content = response.choices[0].message.content or "{}"
    try:
        return QueryPlan.model_validate(json.loads(content))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError(f"Could not parse the model's structured query response: {exc}") from exc


def analyze_results(question: str, explanation: str, columns: list[str], rows: list[dict[str, Any]],
                    api_key: str | None = None, base_url: str | None = None,
                    model: str | None = None) -> str:
    """Summarize returned rows without requesting more database access."""
    if not rows:
        return "The query ran successfully but returned no matching rows."
    client = _client(api_key, base_url)
    response = client.chat.completions.create(
        model=_model(model),
        temperature=0.2,
        messages=[
            {"role": "system", "content": "Summarize SQL query results accurately in 2–4 concise sentences. Do not invent facts; mention if the result is truncated."},
            {"role": "user", "content": json.dumps({
                "question": question, "query_purpose": explanation,
                "columns": columns, "sample_rows": rows[:30],
            }, ensure_ascii=False, default=str)},
        ],
    )
    return response.choices[0].message.content or "Query completed; no summary was returned."
