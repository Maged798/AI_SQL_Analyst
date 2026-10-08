"""Choose a useful Plotly chart from the agent's parsed chart suggestion."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def build_chart(frame: pd.DataFrame, chart_type: str, x_column: str | None,
                y_column: str | None) -> go.Figure | None:
    if frame.empty or len(frame.columns) < 2 or chart_type == "table":
        return None
    columns = list(frame.columns)
    x = x_column if x_column in columns else columns[0]
    y = y_column if y_column in columns else next((c for c in columns if c != x), None)
    if y is None:
        return None
    kind = chart_type.lower()
    try:
        if kind == "pie":
            return px.pie(frame, names=x, values=y, hole=0.48)
        if kind == "line":
            return px.line(frame, x=x, y=y, markers=True)
        if kind == "scatter":
            return px.scatter(frame, x=x, y=y)
        return px.bar(frame, x=x, y=y)
    except (ValueError, TypeError):
        return None
