import streamlit as st
import pandas as pd
import plotly.graph_objects as go

MAX_FILE_SIZE_MB = 50
MAX_ROWS = 200_000

st.set_page_config(layout="wide", page_title="CSV Analyzer")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:

    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"File too large (max {MAX_FILE_SIZE_MB} MB)")
        st.stop()

    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
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

    x_column = st.selectbox("Select X axis", columns)

    df[x_column] = pd.to_numeric(df[x_column], errors='coerce')

    if df[x_column].isnull().all():
        st.error("Selected X column is not numeric or empty")
        st.stop()

    df = df.dropna(subset=[x_column])

    st.markdown("---")
    st.subheader("Global Range Control")

    min_x = float(df[x_column].min())
    max_x = float(df[x_column].max())
    
    def format_time(ms):
        total_seconds = int(ms // 1000)
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        return f"{h:02}:{m:02}:{s:02}"
    
    x_range = st.slider(
        "Select X range (time)",
        min_value=min_x,
        max_value=max_x,
        value=(min_x, max_x),
        format="%d"
    )
    
    st.write(
        f"Selected: {format_time(x_range[0])} → {format_time(x_range[1])}"
    )

    filtered_df = df[(df[x_column] >= x_range[0]) & (df[x_column] <= x_range[1])]

    st.markdown("---")

    if "graphs" not in st.session_state:
        st.session_state.graphs = []

    if st.button("Add new graph"):
        st.session_state.graphs.append({"left": [], "right": []})

    for i, graph in enumerate(st.session_state.graphs):
        st.subheader(f"Graph {i+1}")

        col1, col2 = st.columns(2)

        with col1:
            left_cols = st.multiselect(
                "Left axis",
                columns,
                default=graph["left"],
                key=f"left_{i}"
            )

        with col2:
            right_cols = st.multiselect(
                "Right axis",
                columns,
                default=graph["right"],
                key=f"right_{i}"
            )

        st.session_state.graphs[i]["left"] = left_cols
        st.session_state.graphs[i]["right"] = right_cols

        selected_cols = []
        for col in [x_column] + left_cols + right_cols:
            if col not in selected_cols:
                selected_cols.append(col)
        
        if left_cols or right_cols:
            export_df = filtered_df[selected_cols].copy()
            csv_data = export_df.to_csv(index=False).encode("utf-8")
        
            st.download_button(
                label=f"⬇ Export CSV (Graph {i+1})",
                data=csv_data,
                file_name=f"graph_{i+1}.csv",
                mime="text/csv",
                key=f"download_{i}"
            )

        if left_cols or right_cols:
            fig = go.Figure()

            for col in left_cols:
                fig.add_trace(go.Scatter(
                    x=filtered_df[x_column],
                    y=filtered_df[col],
                    mode="lines",
                    name=col,
                    yaxis="y1"
                ))

            for col in right_cols:
                fig.add_trace(go.Scatter(
                    x=filtered_df[x_column],
                    y=filtered_df[col],
                    mode="lines",
                    name=col,
                    yaxis="y2",
                    line=dict(dash="dash")
                ))

            fig.update_layout(
                height=400,
                hovermode="x unified",
                xaxis=dict(
                    title=x_column,
                    rangeslider=dict(visible=False),
                    showspikes=True,
                    spikemode="across",
                    spikesnap="cursor",
                    spikethickness=1,
                    spikedash="solid",
                    spikecolor="white",
                    showline=True
                ),
                yaxis=dict(
                    title="Left",
                    showspikes=True,
                    spikemode="across",
                    spikesnap="cursor",
                    spikethickness=1,
                    spikedash="solid",
                    spikecolor="white"
                ),
                yaxis2=dict(
                    title="Right",
                    overlaying="y",
                    side="right",
                    showspikes=True,
                    spikemode="across",
                    spikesnap="cursor",
                    spikethickness=1,
                    spikedash="solid",
                    spikecolor="white"
                ),
                legend=dict(orientation="h"),
                margin=dict(l=40, r=40, t=40, b=40)
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"scrollZoom": False}
            )
