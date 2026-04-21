import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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

    x_column = "time(ms)"

    if x_column not in df.columns:
        st.error("Column 'time(ms)' not found in CSV")
        st.stop()

    df[x_column] = pd.to_numeric(df[x_column], errors="coerce")
    df = df.dropna(subset=[x_column])

    df["_time"] = pd.to_datetime(df[x_column], unit="ms")

    min_sec = 0
    max_sec = int((df[x_column].max() - df[x_column].min()) / 1000)

    if "start_sec" not in st.session_state:
        st.session_state.start_sec = min_sec

    if "end_sec" not in st.session_state:
        st.session_state.end_sec = max_sec

    col1, col2 = st.columns(2)

    with col1:
        start_sec = st.number_input(
            "Start (sec)",
            min_value=min_sec,
            max_value=max_sec,
            step=1,
            key="start_sec"
        )

    with col2:
        end_sec = st.number_input(
            "End (sec)",
            min_value=min_sec,
            max_value=max_sec,
            step=1,
            key="end_sec"
        )

    if start_sec >= end_sec:
        st.error("Start must be less than End")
        st.stop()

    base_time = df["_time"].min()

    start = base_time + pd.to_timedelta(start_sec, unit="s")
    end = base_time + pd.to_timedelta(end_sec, unit="s")

    duration = end - start

    st.write(
        f"{start.strftime('%H:%M:%S')} — {end.strftime('%H:%M:%S')} "
        f"(+{str(duration).split('.')[0]})"
    )

    filtered_df = df[
        (df["_time"] >= start) &
        (df["_time"] <= end)
    ]

    if "graphs" not in st.session_state:
        st.session_state.graphs = [{"left": [], "right": []}]

    if st.button("Add new graph"):
        st.session_state.graphs.append({"left": [], "right": []})

    for i, graph in enumerate(st.session_state.graphs):

        st.markdown(f"### Graph {i+1}")

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

            fig = go.Figure()

            for col in left_cols:
                fig.add_trace(
                    go.Scatter(
                        x=filtered_df["_time"],
                        y=filtered_df[col],
                        mode="lines",
                        name=col,
                        yaxis="y1",
                        line=dict(width=2),
                        hovertemplate=col + ": %{y}<extra></extra>"
                    )
                )

            for col in right_cols:
                fig.add_trace(
                    go.Scatter(
                        x=filtered_df["_time"],
                        y=filtered_df[col],
                        mode="lines",
                        name=col,
                        yaxis="y2",
                        line=dict(width=2, dash="dash"),
                        hovertemplate=col + ": %{y}<extra></extra>"
                    )
                )

            fig.update_layout(
            height=400,
            hovermode="x unified",
            plot_bgcolor="black",
            paper_bgcolor="black",
            xaxis=dict(
                title="Time",
                rangeslider=dict(visible=False),
                showspikes=True,
                spikemode="across",
                spikesnap="cursor",
                spikethickness=1,
                spikecolor="white",
                tickformat="%H:%M:%S",
                showline=True,
                range=[start, end]
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
