import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("CSV Log Analyzer PRO")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.dataframe(df.head())

    columns = df.columns.tolist()
    time_column = st.selectbox("Select time column", columns)

    st.markdown("---")

    st.subheader("Global Range Control")

    min_x = float(df[time_column].min())
    max_x = float(df[time_column].max())

    x_range = st.slider(
        "Select time range",
        min_value=min_x,
        max_value=max_x,
        value=(min_x, max_x)
    )

    filtered_df = df[(df[time_column] >= x_range[0]) & (df[time_column] <= x_range[1])]

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

        if left_cols or right_cols:
            fig = go.Figure()

            for col in left_cols:
                fig.add_trace(go.Scatter(
                    x=filtered_df[time_column],
                    y=filtered_df[col],
                    mode="lines",
                    name=col,
                    yaxis="y1"
                ))

            for col in right_cols:
                fig.add_trace(go.Scatter(
                    x=filtered_df[time_column],
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
                    title=time_column,
                    rangeslider=dict(visible=True), 
                    showspikes=True,  
                    spikemode="across",
                    spikesnap="cursor",
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
                use_container_width=True,
                config={"scrollZoom": True} 
            )
