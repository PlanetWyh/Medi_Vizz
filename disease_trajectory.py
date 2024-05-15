from datetime import datetime, timedelta
import numpy as np
from io import StringIO
import base64
import pandas as pd

def get_array_for_a_plot(file):
    #decode the file received
    decoded = base64.b64decode(file[0])
    decoded_file=decoded.decode('unicode_escape')
    disease_history_df = pd.read_csv(StringIO(decoded_file), sep='\t', encoding= 'unicode_escape')
    # disease_history_df = pd.read_csv(file, sep='\t', encoding= 'unicode_escape')
    # disease_history_df = pd.read_csv(file,sep='\t',encoding= 'unicode_escape')
    codes_array = np.asarray(disease_history_df['DiagnosisConsolidated icd10 code'])
    date_of_diagnosis_array = np.asarray(disease_history_df['DiagnosisConsolidated earliestDate'])
    # codes_array = np.asarray(disease_history_df[colmn_codes])
    # date_of_diagnosis_array = np.asarray(disease_history_df[colmn_dates])
     #convert string to time
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in date_of_diagnosis_array]
    # df_codes_years=np.array((codes_array, dates))
    df_codes_years=np.column_stack((dates, codes_array))
    #assigning multiple codes of diagnosis to one year
    grouped_codes_years={}
    for date, code in df_codes_years:
        if date in grouped_codes_years:
            grouped_codes_years[date].append(code)
        else:
            value=[]
            grouped_codes_years.setdefault(date, value)
            grouped_codes_years[date].append(code)
    return grouped_codes_years

def get_pairs_of_code_date(file):
    decoded = base64.b64decode(file[0])
    decoded_file=decoded.decode('unicode_escape')
    disease_history_df = pd.read_csv(StringIO(decoded_file), sep='\t', encoding= 'unicode_escape')
    # disease_history_df = pd.read_csv(file, sep='\t', encoding= 'unicode_escape')
    # disease_history_df = pd.read_csv(file,sep='\t',encoding= 'unicode_escape')
    codes_array = np.asarray(disease_history_df['DiagnosisConsolidated icd10 code'])
    date_of_diagnosis_array = np.asarray(disease_history_df['DiagnosisConsolidated earliestDate'])
     #convert string to time
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in date_of_diagnosis_array]
    # df_codes_years=np.array((codes_array, dates))
    df_codes_years=np.column_stack((dates, codes_array))
    return date_of_diagnosis_array, codes_array

def get_patient_code(file):
    disease_history_df = pd.read_csv(file, sep='\t', encoding= 'unicode_escape')
    patient_codes_array = np.asarray(disease_history_df['Person skood'])
    return str(patient_codes_array[0])


#convert dictionaty to numpy array for plotting
def dict_to_numpy(dict):
    result = dict.items()
    # Convert object to a list
    data = list(result)
    # Convert list to an array
    numpyArray = np.array(data)
    # print the numpy array
    return numpyArray

#changes the hights of the plots vertical lines
def set_plots_levels(list_levels, dates):
    reps=np.ceil(len(dates)/len(list_levels))
    levels=np.tile(list_levels,int(reps))[:len(dates)]
    return levels


def main():
    path_of_the_file=input("enter file path: ")
    dict_date_codes=get_array_for_a_plot(path_of_the_file)
    np_date_codes=dict_to_numpy(dict_date_codes)
    #plot(np_date_codes)

if __name__ == '__main__':
    main()
