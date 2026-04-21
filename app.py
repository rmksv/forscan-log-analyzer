import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

MAX_FILE_SIZE_MB = 50
MAX_ROWS = 200_000

st.set_page_config(layout="wide")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:

    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error("File too large")
        st.stop()

    try:
        df = pd.read_csv(uploaded_file, sep=None, engine="python")
    except Exception:
        st.error("Invalid CSV")
        st.stop()

    if df.empty:
        st.stop()

    if len(df) > MAX_ROWS:
        df = df.head(MAX_ROWS)

    columns = df.columns.tolist()

    x_column = st.selectbox("Select time column", columns)

    df[x_column] = pd.to_numeric(df[x_column], errors="coerce")
    df = df.dropna(subset=[x_column])

    df["_time"] = pd.to_datetime(df[x_column], unit="ms")

    signals = st.multiselect("Signals", columns)

    if len(signals) == 0:
        st.stop()

    min_time = df["_time"].min()
    max_time = df["_time"].max()

    if "global_range" not in st.session_state:
        st.session_state.global_range = (min_time, max_time)

    if "cursor_time" not in st.session_state:
        st.session_state.cursor_time = min_time

    col1, col2 = st.columns([3,1])

    with col1:
        selected_range = st.slider(
            "Time range",
            min_value=min_time.to_pydatetime(),
            max_value=max_time.to_pydatetime(),
            value=(
                st.session_state.global_range[0].to_pydatetime(),
                st.session_state.global_range[1].to_pydatetime()
            ),
            format="HH:mm:ss"
        )

        start, end = pd.to_datetime(selected_range[0]), pd.to_datetime(selected_range[1])
        st.session_state.global_range = (start, end)

    with col2:
        cursor = st.slider(
            "Cursor",
            min_value=min_time.to_pydatetime(),
            max_value=max_time.to_pydatetime(),
            value=st.session_state.cursor_time.to_pydatetime(),
            format="HH:mm:ss"
        )
        cursor_time = pd.to_datetime(cursor)
        st.session_state.cursor_time = cursor_time

    filtered_df = df[(df["_time"] >= start) & (df["_time"] <= end)]

    fig = make_subplots(
        rows=len(signals),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02
    )

    for i, col in enumerate(signals, start=1):
        fig.add_trace(
            go.Scatter(
                x=filtered_df["_time"],
                y=filtered_df[col],
                mode="lines",
                line=dict(width=1),
                name=col,
                hovertemplate="Time: %{x|%H:%M:%S}<br>" + col + ": %{y}<extra></extra>"
            ),
            row=i,
            col=1
        )

    fig.add_vline(
        x=cursor_time,
        line_width=1,
        line_color="white"
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
        range=[start, end]
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#333",
        fixedrange=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"scrollZoom": False, "displayModeBar": False}
    )

    st.markdown("### Cursor Values")

    nearest_idx = (df["_time"] - cursor_time).abs().idxmin()

    values = []
    for col in signals:
        values.append((col, df.loc[nearest_idx, col]))

    for name, val in values:
        st.write(f"{name}: {val}")

    export_cols = [x_column] + signals
    export_df = filtered_df[export_cols].copy()

    csv_data = export_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Export CSV",
        data=csv_data,
        file_name="forscan_style.csv",
        mime="text/csv"
    )
