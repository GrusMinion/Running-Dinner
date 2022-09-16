import streamlit as st
import file_validation
from data_transformations import DataTransformer


def render_page():
    st.header('Upload data files')
    st.markdown('''Select and upload two data files:  
- Schedule to be checked based on several constraints
- Dataset containing all information of participants of the Running Dinner  


After uploading both data files the results pages will be available for navigation.
''')

    col1, col2 = st.columns(2)

    with col1:
        schedule_file = st.file_uploader(
            'Schedule file',
            type='xlsx',
            help='Upload an Excel (xlsx) file with schedule for the Running Dinner'
        )
        schedule_file_upload_result = st.empty()
        if schedule_file is not None:
            with st.spinner('Validating uploaded file...'):
                error_msgs, oplossing_df = file_validation.validate_schedule(schedule_file)
                if oplossing_df is None:
                    schedule_file_upload_result.error('  \n'.join(error_msgs))
                    st.session_state.oplossing_df = None
                    st.session_state.schedule_data_filename = None
                else:
                    schedule_file_upload_result.success('  \n'.join(error_msgs))
                    st.session_state.oplossing_df = oplossing_df
                    st.session_state.schedule_data_filename = schedule_file.name
        # elif st.session_state.get('schedule_data_filename', None):
        #     st.info(f'Selected file for schedule data: {st.session_state.schedule_data_filename}')

    with col2:
        rd_data_file = st.file_uploader(
            'Running Dinner data file',
            type='xlsx',
            help='Upload an Excel (xlsx) file with Running Dinner data of participants'
        )
        rd_data_file_upload_result = st.empty()
        if rd_data_file is not None:
            with st.spinner('Validating uploaded file...'):
                error_msgs, bewoners_df, adressen_df, bijelkaar_df, buren_df, gang_vorigjaar_df, \
                    tafelgenoot_vorigjaar_df = file_validation.validate_rd_data(rd_data_file)
                if bewoners_df is None:
                    rd_data_file_upload_result.error('  \n'.join(error_msgs))
                    st.session_state.bewoners_df = None
                    st.session_state.adressen_df = None
                    st.session_state.bijelkaar_df = None
                    st.session_state.buren_df = None
                    st.session_state.gang_vorigjaar_df = None
                    st.session_state.tafelgenoot_vorigjaar_df = None
                    st.session_state.rd_data_filename = None
                else:
                    rd_data_file_upload_result.success('  \n'.join(error_msgs))
                    st.session_state.bewoners_df = bewoners_df
                    st.session_state.adressen_df = adressen_df
                    st.session_state.bijelkaar_df = bijelkaar_df
                    st.session_state.buren_df = buren_df
                    st.session_state.gang_vorigjaar_df = gang_vorigjaar_df
                    st.session_state.tafelgenoot_vorigjaar_df = tafelgenoot_vorigjaar_df
                    st.session_state.rd_data_filename = rd_data_file.name

        # elif st.session_state.get('rd_data_file', None):
        #     st.info(f'Selected file for schedule data: {st.session_state.rd_data_filename}')


    # print(f'schedule data filename in session state: {st.session_state.get("schedule_data_filename", None)}')
    # print(f'connexion data filename in session state: {st.session_state.get("connexion_data_filename", None)}')

    if st.session_state.get('rd_data_filename', None) and st.session_state.get('schedule_data_filename', None):
        # both files have been upload, move to next page
        if 'data_uploaded' not in st.session_state:
            schedule_file_upload_result.empty()
            rd_data_file_upload_result.empty()
            with st.spinner('File validated. checking schedule, this may take some time...'):
                # transformation can only be run once (it modifies the original dataframes)
                st.session_state.transformed_data = DataTransformer(
                    oplossing_df=st.session_state.oplossing_df,
                    bewoners_df=st.session_state.bewoners_df,
                    adressen_df=st.session_state.adressen_df,
                    bijelkaar_df=st.session_state.bijelkaar_df,
                    buren_df=st.session_state.buren_df,
                    gang_vorigjaar_df=st.session_state.gang_vorigjaar_df,
                    tafelgenoot_vorigjaar_df=st.session_state.tafelgenoot_vorigjaar_df,
                )
            st.session_state.data_uploaded = True
            st.experimental_rerun()
