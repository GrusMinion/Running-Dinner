import streamlit as st
from file_validation import validate_schedule, validate_rd_data
from data_transformations import DataTransformer
from Running_Dinner import create_schedule

# Initialize session state variables
if 'master_data' not in st.session_state:
    st.session_state['master_data'] = None
if 'schedule' not in st.session_state:
    st.session_state['schedule'] = None
if 'transformed_data' not in st.session_state:
    st.session_state['transformed_data'] = None

# Page navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Create Schedule", "Validate Schedule"])


if page == "Validate Schedule":
    st.title("Validate Schedule")
elif page == "Create Schedule":
    st.title("Create a New Schedule")
    
# Upload and validate files
# st.sidebar.title("Upload Data")
master_data = st.file_uploader(
    'Upload Running Dinner Master Data (xlsx)',
    type='xlsx', 
    help='Upload the master data for the Running Dinner'
)

# Immediate validation of master data
if master_data:
    with st.spinner('Checking format of uploaded file...'):
        error_msgs, bewoners_df, adressen_df, bijelkaar_df, buren_df, \
            gang_vorigjaar_df, tafelgenoot_vorigjaar_df = validate_rd_data(master_data)
        if bewoners_df is None:
            st.error("Error in master data: " + ' '.join(error_msgs))
            st.session_state.master_data = None
        else:
            st.session_state.master_data = master_data
            st.session_state.bewoners_df = bewoners_df
            st.session_state.adressen_df = adressen_df
            st.session_state.bijelkaar_df = bijelkaar_df
            st.session_state.buren_df = buren_df
            st.session_state.gang_vorigjaar_df = gang_vorigjaar_df
            st.session_state.tafelgenoot_vorigjaar_df = tafelgenoot_vorigjaar_df
            st.success("Master data successfully validated!")

# Schedule upload and validation for the "Validate Schedule" page
if page == "Validate Schedule":
    schedule = st.file_uploader(
        'Upload Schedule to Validate (xlsx)', 
        type='xlsx', 
        help='Upload the schedule for validation'
    )
    
    if schedule:
        with st.spinner('Checking format of uploaded file...'):
            error_msgs, oplossing_df = validate_schedule(schedule)
            if oplossing_df is None:
                st.error("Error in schedule: " + ' '.join(error_msgs))
                st.session_state.schedule = None
            else:
                st.session_state.schedule = schedule
                st.session_state.oplossing_df = oplossing_df
                st.success("Schedule successfully validated!")

    # Only show button when both files are valid
    if st.session_state.master_data and st.session_state.schedule:
        if st.button("Validate Schedule"):
            # Create a DataTransformer object to hold all the validated dataframes
            st.session_state.transformed_data = DataTransformer(
                oplossing_df=st.session_state.oplossing_df,
                bewoners_df=st.session_state.bewoners_df,
                adressen_df=st.session_state.adressen_df,
                bijelkaar_df=st.session_state.bijelkaar_df,
                buren_df=st.session_state.buren_df,
                gang_vorigjaar_df=st.session_state.gang_vorigjaar_df,
                tafelgenoot_vorigjaar_df=st.session_state.tafelgenoot_vorigjaar_df
            )
            st.write("Schedule validation completed.")
            st.dataframe(st.session_state.transformed_data.table_KPI)

elif page == "Create Schedule":

    if st.session_state.master_data:
        # Handle button state outside the if block
        create_button_disabled = st.session_state.get("calculating", False)
        if st.button("Create Schedule", disabled=create_button_disabled):
            # Immediately update the state after clicking the button
            st.session_state.calculating = True

        # Only proceed if the calculation is not already running
        if st.session_state.get("calculating", False):
            with st.spinner("Creating schedule... This may take some time."):
                kpi_placeholder = st.empty()  # Placeholder for KPI

                # Create the DataTransformer object
                st.session_state.transformed_data = DataTransformer(
                    bewoners_df=st.session_state.bewoners_df,
                    adressen_df=st.session_state.adressen_df,
                    bijelkaar_df=st.session_state.bijelkaar_df,
                    buren_df=st.session_state.buren_df,
                    gang_vorigjaar_df=st.session_state.gang_vorigjaar_df,
                    tafelgenoot_vorigjaar_df=st.session_state.tafelgenoot_vorigjaar_df
                )

                # Define a callback to update KPI value
                def update_kpi(current_kpi):
                    kpi_placeholder.write(f"Current total KPI value is: {current_kpi}")

                # Generate the new schedule and update the KPI value during the process
                new_schedule = create_schedule(st.session_state.transformed_data, update_kpi)
                st.session_state.transformed_data.add_oplossing_df(new_schedule)

            # Calculation done, reset the flag
            st.session_state.calculating = False
            st.write("New Schedule Generated:")
            st.dataframe(new_schedule)

    else:
        st.info("Please upload and validate the master data before creating a schedule.")

