import streamlit as st
import pages.upload_datafiles
import pages.show_table
from functools import partial

st.set_page_config(
    page_title='Running Dinner constraint check',
    layout='wide',
    menu_items={'About': '''Original application written Manuel Bastin


Refactoring and Streamlit version by S. van der Wulp (FHENG - Applied Mathematics)'''
    }
)

data_uploaded = 'data_uploaded' in st.session_state

available_pages = {  ## pages while uploading data
    'Upload data': partial(pages.upload_datafiles.render_page),
    



}
if data_uploaded:
    transformed_data = st.session_state.transformed_data
    available_pages = {  ## pages after uploading data
        'Show summary table': partial(
            pages.show_table.render_page,
            transformed_data.table_KPI, 'Quality of Running Dinner schedule'),

    }
previous_page_selected = st.session_state.get('previous_page_selected', None)

st.sidebar.title("Navigation")
page_selected = st.sidebar.radio(
    "Go to",
    list(available_pages.keys())
)
if data_uploaded:
    if st.sidebar.button('Reset uploads'):
        del st.session_state['oplossing_df']
        del st.session_state['schedule_data_filename']
        del st.session_state['bewoners_df']
        del st.session_state['adressen_df']
        del st.session_state['bijelkaar_df']
        del st.session_state['buren_df']
        del st.session_state['gang_vorigjaar_df']
        del st.session_state['tafelgenoot_vorigjaar_df']
        del st.session_state['rd_data_filename']
        del st.session_state['transformed_data']
        del st.session_state['data_uploaded']
        st.experimental_rerun()

available_pages[page_selected]()  ## call dict-value function
