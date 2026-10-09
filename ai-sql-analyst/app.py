from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from charts import build_chart
from db import inspect_schema, run_read_query
from seed_db import create_database
from sql_agent import analyze_results, generate_query

load_dotenv()

st.set_page_config(page_title="QueryPilot · AI SQL Analyst", page_icon="✳️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --ink: #17221f; --muted: #65736d; --mint: #b9f5cf; --line: #e5ebe7; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.035em; color: var(--ink); }
.stApp { background: #f8faf8; color: var(--ink); }
.block-container { max-width: 1220px; padding-top: 2rem; }
.hero { padding: 2rem 2.2rem; border: 1px solid var(--line); border-radius: 22px;
background: radial-gradient(circle at 88% 10%, #d9f8e4 0, transparent 29%), linear-gradient(115deg,#fff,#f6fbf7);
margin-bottom: 1.4rem; }
.eyebrow { font-size: .76rem; font-weight: 700; color: #308054; text-transform: uppercase; letter-spacing: .12em; }
.hero h1 { font-size: clamp(2rem,4vw,3rem); margin: .55rem 0; }
.hero p { color: #65736d; font-size: 1.02rem; margin: 0; max-width: 720px; }
div[data-testid="stMetric"] { background: white; color: #17221f !important; border: 1px solid var(--line); border-radius: 16px; padding: 1rem; }
div[data-testid="stMetric"] *, div[data-testid="stMetric"] [data-testid="stMetricLabel"],
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #17221f !important; opacity: 1 !important; }
.stButton button[kind="primary"] { border-radius: 12px; font-weight: 700; min-height: 3rem; }
div[data-testid="stForm"] { background: white; border: 1px solid var(--line); border-radius: 18px; padding: 1.2rem; }
</style>
<section class="hero"><div class="eyebrow">✳ QueryPilot · AI SQL Analyst</div>
<h1>Ask your data a better question.</h1>
<p>Explore your database in plain English. QueryPilot maps your schema, writes a read only SQL query, and turns the results into a clear answer.</p></section>
""", unsafe_allow_html=True)

default_db = os.getenv("SQLITE_DB_PATH", "data/sample_shop.db")
if default_db == "data/sample_shop.db" and not Path(default_db).exists():
    create_database(Path(default_db))

with st.sidebar:
    st.markdown("## Workspace")
    st.markdown("### AI provider")
    api_key = st.text_input("Provider API key", value="", type="password", help="Paste the secret API key from your AI provider. It is used for this session and is not saved by the app.")
    base_url = st.text_input(
        "API base URL",
        value=os.getenv("AI_BASE_URL", ""),
        placeholder="Required: enter the provider API URL",
        help="Enter the API base URL from your provider's documentation, not its website or key page.",
    )
    model_name = st.text_input(
        "Model name",
        value=os.getenv("AI_MODEL", ""),
        placeholder="Enter the model ID from your provider",
        help="Enter the model ID exactly as your provider documents it.",
    )
    db_path = st.text_input("SQLite database file", value=default_db, help="Path to a SQLite database this app can read.")
    st.caption("No model weights are downloaded. Connect a provider that supports this app's Chat Completions and JSON response format.")
    st.divider()
    st.markdown("### Connected schema")
    try:
        schema = inspect_schema(db_path)
        st.code(schema, language="text")
    except Exception as exc:
        schema = ""
        st.error(str(exc))
    with st.expander("Example questions"):
        st.markdown("• Show the best selling products\n\n• Which product category generated the most revenue?\n\n• Show monthly sales trends\n\n• Which region has the highest order value?")

st.markdown("### Start with a question")
with st.form("query_form", clear_on_submit=False):
    question = st.text_input("Your question", placeholder="Show the best selling products", label_visibility="collapsed")
    submitted = st.form_submit_button("✳  Analyze data", type="primary", use_container_width=True)

def _render_result(result: dict) -> None:
    frame = result["frame"]
    plan = result["plan"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows returned", f"{len(frame):,}")
    c2.metric("Columns", f"{len(frame.columns):,}")
    c3.metric("Visualization", plan.chart_type.title())
    left, right = st.columns([1.05, .95], gap="large")
    with left:
        st.markdown("#### Query result")
        st.dataframe(frame, use_container_width=True, hide_index=True)
        with st.expander("Generated SQL"):
            st.code(result["sql"], language="sql")
            st.caption(plan.explanation)
    with right:
        st.markdown("#### Visualization")
        figure = build_chart(frame, plan.chart_type, plan.x_column, plan.y_column)
        if figure is not None:
            figure.update_layout(
                template="plotly_white",
                margin=dict(l=18, r=16, t=24, b=18),
                font=dict(family="DM Sans", color="#24342D", size=13),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                legend=dict(font=dict(color="#53665B"), title_text=""),
            )
            if plan.chart_type.lower() != "pie":
                figure.update_xaxes(showgrid=False, linecolor="#DCE7E0", tickfont=dict(color="#53665B"))
                figure.update_yaxes(showgrid=True, gridcolor="#E8EFEA", zerolinecolor="#DCE7E0",
                                    tickfont=dict(color="#53665B"))
            st.plotly_chart(figure, use_container_width=True)
        else:
            st.info("This result is best viewed as a table.")
        st.markdown("#### Analysis")
        st.write(result["analysis"])


if "result" in st.session_state and not submitted:
    _render_result(st.session_state.result)


if submitted:
    st.session_state.pop("result", None)
    if not question.strip():
        st.warning("Enter a question to get started.")
    elif not schema:
        st.error("Connect a valid SQLite database before asking a question.")
    elif not model_name.strip():
        st.warning("Enter your provider's model ID in the sidebar.")
    elif not base_url.strip() and not os.getenv("AI_BASE_URL", "").strip():
        st.warning("Enter your provider's API base URL in the sidebar.")
    else:
        try:
            with st.status("Understanding your question and querying the database…", expanded=True) as status:
                st.write("Reading the database schema")
                plan = generate_query(
                    question.strip(), schema, api_key or None,
                    base_url or None, model_name or None,
                )
                st.write("Checking SQL safety and running the query")
                frame, safe_sql = run_read_query(db_path, plan.sql)
                st.write("Summarizing the returned data")
                try:
                    analysis = analyze_results(
                        question.strip(), plan.explanation, list(frame.columns),
                        frame.head(30).to_dict(orient="records"), api_key or None,
                        base_url or None, model_name or None,
                    )
                except Exception as summary_error:
                    analysis = f"{len(frame)} rows returned. Automatic summary unavailable: {summary_error}"
                status.update(label="Analysis complete", state="complete", expanded=False)
            st.session_state.result = {"frame": frame, "plan": plan, "sql": safe_sql, "analysis": analysis}
            _render_result(st.session_state.result)
        except Exception as exc:
            st.error(f"I couldn't complete that query: {exc}")

st.markdown("<div style='height:2rem'></div><hr><small style='color:#829089'>QueryPilot · Your database stays under your control. Queries are read only and limited to 500 rows.</small>", unsafe_allow_html=True)
