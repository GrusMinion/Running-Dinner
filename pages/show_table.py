import streamlit as st
import pandas as pd
from generate_visualizations_new import DataVisualizations


def render_page(df: pd.DataFrame, title: str):
    st.title(title)
    st.dataframe(df)
