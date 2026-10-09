"""Choose a useful Plotly chart from the agent's parsed chart suggestion."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PALETTE = ["#16866A", "#57B894", "#9AD8B7", "#E5B755", "#E77D65", "#7187A8"]


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
            figure = px.pie(frame, names=x, values=y, hole=0.48, color_discrete_sequence=PALETTE)
            figure.update_traces(marker=dict(line=dict(color="#FFFFFF", width=2)),
                                 textfont=dict(color="#24342D"))
            return figure
        if kind == "line":
            figure = px.line(frame, x=x, y=y, markers=True)
            figure.update_traces(line=dict(color=PALETTE[0], width=3),
                                 marker=dict(color=PALETTE[0], size=8))
            return figure
        if kind == "scatter":
            figure = px.scatter(frame, x=x, y=y)
            figure.update_traces(marker=dict(color=PALETTE[0], size=11,
                                             line=dict(color="#FFFFFF", width=1)))
            return figure
        figure = px.bar(frame, x=x, y=y)
        figure.update_traces(marker_color=PALETTE[0])
        return figure
    except (ValueError, TypeError):
        return None
