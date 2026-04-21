import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

MAX_FILE_SIZE_MB = 50
MAX_ROWS = 200_000

st.set_page_config(layout="wide", page_title="CSV Analyzer")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:

    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"File too large (max {MAX_FILE_SIZE_MB} MB)")
        st.stop()

    try:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")
    except Exception:
        st.error("Invalid or corrupted CSV file")
        st.stop()

    if df.empty:
        st.error("CSV file is empty")
        st.stop()

    if len(df) > MAX_ROWS:
        df = df.head(MAX_ROWS)

    columns = df.columns.tolist()
    if len(columns) == 0:
        st.error("CSV has no columns")
        st.stop()

    x_column = st.selectbox("Select time column", columns)

    df[x_column] = pd.to_numeric(df[x_column], errors="coerce")

    if df[x_column].isnull().all():
        st.error("Selected column is not numeric")
        st.stop()

    df = df.dropna(subset=[x_column])

    df["_time"] = pd.to_datetime(df[x_column], unit="ms")

    signals = st.multiselect("Select signals", columns)

    if len(signals) == 0:
        st.stop()

    fig = make_subplots(
        rows=len(signals),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02
    )

    for i, col in enumerate(signals, start=1):
        fig.add_trace(
            go.Scatter(
                x=df["_time"],
                y=df[col],
                mode="lines",
                name=col,
                line=dict(width=1),
                hovertemplate="Time: %{x|%H:%M:%S}<br>" + col + ": %{y}<extra></extra>"
            ),
            row=i,
            col=1
        )

    fig.update_layout(
        height=250 * len(signals),
        hovermode="x unified",
        plot_bgcolor="black",
        paper_bgcolor="black",
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=40)
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#333",
        tickformat="%H:%M:%S",
        fixedrange=True,
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikecolor="white",
        spikethickness=1
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#333",
        fixedrange=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": False,
            "displayModeBar": False
        }
    )

    export_cols = [x_column] + signals
    export_df = df[export_cols].copy()
    csv_data = export_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Export CSV",
        data=csv_data,
        file_name="forscan_style_export.csv",
        mime="text/csv"
    )
