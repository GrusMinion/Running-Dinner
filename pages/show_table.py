import streamlit as st
import pandas as pd


def render_page(df: pd.DataFrame, title: str):
    st.title(title)
    st.dataframe(df)
