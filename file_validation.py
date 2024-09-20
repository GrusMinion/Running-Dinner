import numpy as np
import pandas as pd
# import datetime
from streamlit.runtime.uploaded_file_manager import UploadedFile


def validate_schedule(uploaded_file: UploadedFile) -> tuple[list[str], pd.DataFrame]:
    error_msgs = []
    filename = uploaded_file.name
    dot = filename.rindex('.')
    filename_end = filename[dot:]
    if filename_end == '.xlsx':
        error_msgs.append("Chosen file has the correct extension.")
    else:
        error_msgs.append(
            "ERROR: "
            "The chosen file is not an Microsoft Excel Worksheet (extension .xlsx) ERROR #0001"
        )
        return error_msgs, None
    
    data = pd.read_excel(uploaded_file)
    format_columns = ['Bewoner','Huisadres','Geslacht','Voor','Hoofd','Na','kookt','aantal']
    data_columns = list(data.columns)
    
    if data_columns == format_columns:
        error_msgs.append("Columns of chosen file have the correct format.")
    else:
        error_msgs.append(
            "ERROR: "
            'The data in the chosen file does not have the right format. ERROR #0002'
        )
        return error_msgs, None

    # if type(data.loc[0, 'startlocatie']) != str or data['startlocatie'].dtype != object:
    #     error_msgs.append(
    #         "ERROR: "
    #         'The data in column startlocatie in file omloopplanning does not have the right format (should be text). ERROR #1001'
    #     )
    #     return error_msgs, None

    # if type(data.loc[0, 'eindlocatie']) != str or data['eindlocatie'].dtype != object:
    #     error_msgs.append(
    #         "ERROR: "
    #         'The data in column eindlocatie in file omloopplanning does not have the right format (should be text). ERROR #1001'
    #     )
    #     return error_msgs, None

    # if type(data.loc[0, 'starttijd']) != str or data['starttijd'].dtype != object:
    #     error_msgs.append(
    #         "ERROR: "
    #         'The data in column starttijd in file omloopplanning does not have the right format (should be text). ERROR #1001'
    #     )
    #     return error_msgs, None
    
    # if type(data.loc[0, 'eindtijd']) != str or data['eindtijd'].dtype != object:
    #     error_msgs.append(
    #         "ERROR: "
    #         'The data in column eindtijd in file omloopplanning does not have the right format (should be text). ERROR #1001'
    #     )
    #     return error_msgs, None
        
    # try:
    #     data['starttijd'] = pd.to_datetime(data['starttijd'], format='%H:%M:%S') - pd.to_datetime(data['starttijd'], format='%H:%M:%S').dt.normalize()
    #     data['eindtijd'] = pd.to_datetime(data['eindtijd'], format='%H:%M:%S') - pd.to_datetime(data['eindtijd'], format='%H:%M:%S').dt.normalize()
    #     data['duur'] = data['eindtijd'] - data['starttijd']
    # except:
    #     error_msgs.append(
    #         "ERROR: "
    #         'The values in columns starttijd and eindtijd could not be converted to time values. Make sure they are in the format HH:MM:SS ERROR #0003'
    #     )
    #     return error_msgs, None
    
    # if sum(data['buslijn'].isna()) == 0:
    #     error_msgs.append(
    #         "ERROR: "
    #         'The cell in column buslijn should be empty if a bus is not following a line. ERROR #0004'
    #     )
    #     return error_msgs, None
    
    # try:
    #     data['buslijn'] = data['buslijn'].fillna(0)
    # except:
    #     error_msgs.append(
    #         "ERROR: "
    #         'The cell in column buslijn should be empty if a bus is not following a line. ERROR #0004'
    #     )
    #     return error_msgs, None
    
    # if type(data.loc[0, 'buslijn']) != np.float64 or data['buslijn'].dtype != np.float64:
    #     error_msgs.append(
    #         "ERROR: "
    #         'The data in column buslijn does not have the right format (should be numbers or empty cell\'s). ERROR #0004'
    #     )
    #     return error_msgs, None
    
    # if type(data.loc[0, 'energieverbruik']) != np.float64 or data['energieverbruik'].dtype != np.float64:
    #     error_msgs.append(
    #         "ERROR: "
    #         'The data in column energieverbruik does not have the right format (should be numbers, negative for charging). ERROR #0005'
    #     )
    #     return error_msgs, None
    
    # if type(data.loc[0, 'omloop nummer']) != np.int64 or data['omloop nummer'].dtype != np.int64:
    #     error_msgs.append(
    #         "ERROR: "
    #         'The data in column omloop nummer in file omloopplanning does not have the right format (should be integer). ERROR #1002'
    #     )
    #     return error_msgs, None
    
    # error_msgs.append("The data in the columns have the right format")
    return error_msgs, data


def validate_rd_data(uploaded_file: UploadedFile) -> tuple[list[str], pd.DataFrame, pd.DataFrame, \
                            pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    error_msgs = []
    filename = uploaded_file.name
    dot = filename.rindex('.')
    filename_end = filename[dot:]
    if filename_end == '.xlsx':
        error_msgs.append("Chosen file has the correct extension.")
    else:
        error_msgs.append(
            "ERROR: "
            "The chosen file is not an Microsoft Excel Worksheet (extension .xlsx) ERROR #0001"
        )
        return error_msgs, None, None, None, None, None, None
    
    try:
        bewoners_df = pd.read_excel (uploaded_file, sheet_name = 'Bewoners')
        adressen_df = pd.read_excel (uploaded_file, sheet_name = 'Adressen')
        bijelkaar_df = pd.read_excel (uploaded_file, sheet_name = 'Paar blijft bij elkaar',skiprows=1)
        buren_df = pd.read_excel (uploaded_file, sheet_name = 'Buren',skiprows=1)
        gang_vorigjaar_df = pd.read_excel (uploaded_file, sheet_name = 'Kookte vorig jaar',skiprows=1)
        tafelgenoot_vorigjaar_df = pd.read_excel (uploaded_file, sheet_name ='Tafelgenoot vorig jaar',skiprows=1)
        
        error_msgs.append("Chosen file has the correct sheet names.")
    except:
        error_msgs.append(
            "ERROR: "
            "The file does not have the correct sheet names (should be 'Bewoners', 'Adressen', 'Huisadres', 'Paar blijft bij elkaar', 'Buren', 'Kookte vorig jaar', 'Tafelgenoot vorig jaar') ERROR #0006"
        )
        return error_msgs, None, None, None, None, None, None
    
    
    format_columns_bewoners = ['Bewoner', 'Huisadres', 'Kookt niet', 'Geslacht']
    bewoners_data_columns = list(bewoners_df.columns)
    format_columns_adressen = ['Huisadres', 'Min groepsgrootte', 'Max groepsgrootte','Voorkeur gang']
    adressen_data_columns = list(adressen_df.columns)
    format_columns_paartjes = ['Bewoner1', 'Bewoner2']
    paartjes_data_columns = list(bijelkaar_df.columns)
    format_columns_buren = ['Bewoner1', 'Bewoner2']
    buren_data_columns = list(buren_df.columns)
    format_columns_gangvorigjaar = ['Huisadres', 'Gang']
    gangvorigjaar_data_columns = list(gang_vorigjaar_df.columns)
    format_columns_tafelgenoot = ['Bewoner1', 'Bewoner2']
    tafelgenoot_data_columns = list(tafelgenoot_vorigjaar_df.columns)
    
    if format_columns_bewoners != bewoners_data_columns:
        error_msgs.append(
            "ERROR: "
            "The columns of sheet 'Bewoners' are not in the correct format ERROR #0002"
        )
        return error_msgs, None, None, None, None, None, None
    elif format_columns_adressen != adressen_data_columns:
        error_msgs.append(
            "ERROR: "
            "The columns of sheet 'Adressen' are not in the correct format ERROR #0002"
        )
        return error_msgs, None, None, None, None, None, None
    elif format_columns_paartjes != paartjes_data_columns:
        error_msgs.append(
            "ERROR: "
            "The columns of sheet 'Paar blijft bij elkaar' are not in the correct format ERROR #0002"
        )
        return error_msgs, None, None, None, None, None, None
    elif format_columns_buren != buren_data_columns:
        error_msgs.append(
            "ERROR: "
            "The columns of sheet 'Buren' are not in the correct format ERROR #0002"
        )
        return error_msgs, None, None, None, None, None, None
    elif format_columns_gangvorigjaar != gangvorigjaar_data_columns:
        error_msgs.append(
            "ERROR: "
            "The columns of sheet 'Kookte vorig jaar' are not in the correct format ERROR #0002"
        )
        return error_msgs, None, None, None, None, None, None
    elif format_columns_tafelgenoot != tafelgenoot_data_columns:
        error_msgs.append(
            "ERROR: "
            "The columns of sheet 'Tafelgenoot vorig jaar' are not in the correct format ERROR #0002"
        )
        return error_msgs, None, None, None, None, None, None
    else:
        error_msgs.append("Columns of chosen file have the correct format.")
        return error_msgs, bewoners_df, adressen_df, bijelkaar_df, buren_df, gang_vorigjaar_df, tafelgenoot_vorigjaar_df
    
    # # DIENSTREGELING
    # if type(dienst_data.loc[0, 'startlocatie']) != str or dienst_data['startlocatie'].dtype != object:
    #     error_msgs.append(
    #         "ERROR: "
    #         "The data in column startlocatie in sheet 'Dienstregeling' in file connexxion data does not have the right format (should be text). ERROR #1001"
    #     )
    #     return error_msgs, None, None
    
    # if type(dienst_data.loc[0, 'eindlocatie']) != str or dienst_data['eindlocatie'].dtype != object:
    #     error_msgs.append(
    #         "ERROR: "
    #         "The data in column eindlocatie in sheet 'Dienstregeling' in file connexxion data does not have the right format (should be text). ERROR #1001"
    #     )
    #     return error_msgs, None, None
        
    # if type(dienst_data.loc[0, 'vertrektijd']) != datetime.time or dienst_data['vertrektijd'].dtype != object:
    #     error_msgs.append(
    #         "ERROR: "
    #         "The data in column vertrektijd in sheet 'Dienstregeling' in file connexxion data does not have the right format (should be time in format HH:SS). ERROR #0007"
    #     )
    #     return error_msgs, None, None

    # try:
    #     dienst_data['vertrektijd'] = (
    #         pd.to_datetime(dienst_data['vertrektijd'], format='%H:%M:%S') -
    #         pd.to_datetime(dienst_data['vertrektijd'], format='%H:%M:%S').dt.normalize()
    #     )
    # except:
    #     error_msgs.append(
    #         "ERROR: "
    #         "The data in column vertrektijd in sheet 'Dienstregeling' in file connexxion data does not have the right format (should be time in format HH:SS). ERROR #0007"
    #     )
    #     return error_msgs, None, None
    
    # if type(dienst_data.loc[0, 'buslijn']) != np.int64 or dienst_data['buslijn'].dtype != np.int64:
    #     error_msgs.append(
    #         "ERROR: "
    #         "The data in column buslijn in sheet 'Dienstregeling' in file connexxion data does not have the right format (should be integer). ERROR #1002"
    #     )
    #     return error_msgs, None, None
    
    
    # error_msgs.append("The data in the columns of worksheet 'Dienstregeling' of the chosen file have the right format.")
    
    # # AFSTAND MATRIX
    # if type(afstand_data.loc[0, 'startlocatie']) != str or afstand_data['startlocatie'].dtype != object:
    #     error_msgs.append(
    #         "ERROR: "
    #         "The data in column startlocatie in sheet 'Afstand matrix' in file connexxion data does not have the right format (should be text). ERROR #1001"
    #     )
    #     return error_msgs, None, None
    
    # if type(afstand_data.loc[0, 'eindlocatie']) != str or afstand_data['eindlocatie'].dtype != object:
    #     error_msgs.append(
    #         "ERROR: "
    #         "The data in column eindlocatie in sheet 'Afstand matrix' in file connexxion data does not have the right format (should be text). ERROR #1001"
    #     )
    #     return error_msgs, None, None
    
    # if type(afstand_data.loc[0, 'min reistijd in min']) != np.int64 or afstand_data['min reistijd in min'].dtype != np.int64:
    #     error_msgs.append(
    #         "ERROR: "
    #         "The data in column 'min reistijd in min' in sheet 'Afstand matrix' in file connexxion data does not have the right format (should be integer). ERROR #1002"
    #     )
    #     return error_msgs, None, None
    
    # if type(afstand_data.loc[0, 'max reistijd in min']) != np.int64 or afstand_data['max reistijd in min'].dtype != np.int64:
    #     error_msgs.append(
    #         "ERROR: "
    #         "The data in column 'max reistijd in min' in sheet 'Afstand matrix' in file connexxion data does not have the right format (should be integer). ERROR #1002"
    #     )
    #     return error_msgs, None, None
    
    # if type(afstand_data.loc[0, 'afstand in meters']) != np.int64 or afstand_data['afstand in meters'].dtype != np.int64:
    #     error_msgs.append(
    #         "ERROR: "
    #         "The data in column 'afstand in meters' in sheet 'Afstand matrix' in file connexxion data does not have the right format (should be integer). ERROR #1002"
    #     )
    #     return error_msgs, None, None
    
    # if type(afstand_data.loc[0, 'buslijn']) != np.float64 or afstand_data['buslijn'].dtype != np.float64:
    #     error_msgs.append(
    #         "ERROR: "
    #         "The data in column buslijn in sheet 'Afstand matrix' in file connexxion data does not have the right format (should be integer). ERROR #1002"
    #     )
    #     return error_msgs, None, None

    # error_msgs.append("The data in the column 'Afstand matrix' of the chosen file has the right format.")
    
    return error_msgs, bewoners_df, adressen_df, bijelkaar_df, buren_df, gang_vorigjaar_df, tafelgenoot_vorigjaar_df