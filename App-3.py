import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from io import StringIO

def makeTreemap(labels, parents):
    data = go.Treemap(

    ids = labels,
    labels = labels,
    parents = parents,
    root_color = "lightgray"
)
    fig = go.Figure(data)
    return fig

def makeSunburst(labels, parents):
    data = go.Sunburst(

    ids = labels,
    labels = labels,
    parents = parents,
    root_color = "lightgray"
)
    fig = go.Figure(data)
    return fig

def makeIcicle(labels, parents):
    data = go.Icicle(

    ids = labels,
    labels = labels,
    parents = parents,
    root_color = "lightgray"
)
    fig = go.Figure(data)
    return fig

st.title("Data Charts")

filename = r"C:\Users\aleco\Python_Snowflake\employees_Streamlit.csv"
uploaded_file = st.file_uploader(
    "upload a csv file",type = ["csv"], accept_multiple_files = False)
if uploaded_file is not None:
    filename = StringIO(uploaded_file.getvalue().decode("utf-8"))

df_orig = pd.read_csv(filename, header=0).convert_dtypes()
cols = list(df_orig.columns)

df = pd.read_csv(r"C:\Users\aleco\Python_Snowflake\employees_Streamlit.csv")

labels, parents = df[df.columns[0]], df[df.columns[1]]

tabs = st.tabs(["Treemap","Icicle","Sunburst"])

with tabs[0]:
    fig = makeTreemap(labels, parents)
    st.plotly_chart(fig, use_container_width=True)
with st.expander("Icicle"):
    fig = makeIcicle(labels, parents)
    st.plotly_chart(fig, use_container_width=True)
with st.expander("Sunburst"):
    fig = makeSunburst(labels, parents)
    st.plotly_chart(fig, use_container_width=True)


