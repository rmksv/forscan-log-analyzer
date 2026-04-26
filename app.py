import streamlit as st
import pandas as pd
import plotly.graph_objects as go

MAX_FILE_SIZE_MB = 200
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

    x_column = "time(ms)"

    if x_column not in df.columns:
        st.error("Column 'time(ms)' not found in CSV")
        st.stop()

    df[x_column] = pd.to_numeric(df[x_column], errors="coerce")
    df = df.dropna(subset=[x_column])

    columns = df.columns.tolist()

    # --- STATE ---
    if "graphs" not in st.session_state:
        st.session_state.graphs = [{
            "left": [],
            "right": [],
            "name": "Graph 1"
        }]

    if st.button("Add new graph"):
        st.session_state.graphs.append({
            "left": [],
            "right": [],
            "name": f"Graph {len(st.session_state.graphs)+1}"
        })

    # --- LOOP GRAPHS ---
    for i, graph in enumerate(st.session_state.graphs):

        st.markdown(f"---")

        col_title, col_delete = st.columns([4, 1])

        with col_title:
            graph_name = st.text_input(
                "Graph name",
                value=graph.get("name", f"Graph {i+1}"),
                key=f"name_{i}"
            )
            st.session_state.graphs[i]["name"] = graph_name

        # --- TIME SLIDER PER GRAPH ---
        min_time = int(df[x_column].min())
        max_time = int(df[x_column].max())

        start, end = st.slider(
            f"Time range (ms) - {graph_name}",
            min_value=min_time,
            max_value=max_time,
            value=(min_time, max_time),
            key=f"slider_{i}"
        )

        filtered_df = df[
            (df[x_column] >= start) &
            (df[x_column] <= end)
        ]

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

        col_export, col_delete = st.columns([2, 1])

        with col_delete:
            st.write("")  # трохи "відпускає" кнопку
            if st.button("🗑 Delete Graph", key=f"delete_{i}"):
                st.session_state.graphs.pop(i)
                st.rerun()

        selected_cols = []
        for col in [x_column] + left_cols + right_cols:
            if col not in selected_cols:
                selected_cols.append(col)

        # --- EXPORT ---
        if not filtered_df.empty and (left_cols or right_cols):

            export_df = filtered_df[selected_cols].copy()
            csv_data = export_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label=f"⬇ Export CSV ({graph_name})",
                data=csv_data,
                file_name=f"{graph_name}.csv",
                mime="text/csv",
                key=f"download_{i}"
            )

        # --- GRAPH ---
        if left_cols or right_cols:

            fig = go.Figure()

            # LEFT
            for col in left_cols:
                fig.add_trace(
                    go.Scatter(
                        x=pd.to_datetime(filtered_df[x_column], unit="ms"),
                        y=filtered_df[col],
                        mode="lines",
                        name=col,
                        yaxis="y1",
                        line=dict(width=2),
                        hovertemplate=col + ": %{y}<extra></extra>"
                    )
                )

            # RIGHT
            for col in right_cols:
                fig.add_trace(
                    go.Scatter(
                        x=pd.to_datetime(filtered_df[x_column], unit="ms"),
                        y=filtered_df[col],
                        mode="lines",
                        name=col,
                        yaxis="y2",
                        line=dict(width=2, dash="dash"),
                        hovertemplate=col + ": %{y}<extra></extra>"
                    )
                )

            fig.update_layout(
                title=graph_name,
                height=400,
                hovermode="x unified",
                plot_bgcolor="black",
                paper_bgcolor="black",
                xaxis=dict(
                    title="Time",
                    type="date",
                    showspikes=True,
                    spikemode="across",
                    spikesnap="cursor",
                    spikethickness=1,
                    spikecolor="white",
                    tickformat="%H:%M:%S",
                    showline=True
                ),
                yaxis=dict(title="Left"),
                yaxis2=dict(
                    title="Right",
                    overlaying="y",
                    side="right"
                ),
                legend=dict(orientation="h"),
                margin=dict(l=40, r=40, t=40, b=40)
            )

            st.plotly_chart(
                fig,
                width="stretch",
                config={
                    "scrollZoom": False,
                    "displayModeBar": True
                }
            )

        else:
            st.info("Select parameters to display graph")
