from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
from io import StringIO
import base64
import matplotlib.dates as mdates
import pandas as pd
import pylab as plt

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

#plotting the disease trajectory
def plot(np_array_date_codes):
    #separate dates and codes for easier plotting
    dates=[]
    codes=[]
    for pair in np_array_date_codes:
        dates.append(pair[0])
        codes.append(pair[1])
    #initialise the figure
    fig, ax = plt.subplots(figsize=(10, 7), layout="constrained")
    #ax.set(title="Disease trajectory")
    #ax.set_title("Disease trajectory", pad=1)
    # Plot vertical lines at each x from ymin to ymax
    ax.vlines(dates, 0, set_plots_levels([-12, 12, -10, 10, -8, 8, -6, 6, -4, 4, -2, 2], dates), color="r", linewidth=1.5)  
    # Plot disease codes with red diamonds
    ax.plot(dates, np.zeros_like(dates), "-dk", linewidth=0, markerfacecolor="r") 
    # Annotate lines
    #trying to measure distance between dates to see were to position disease codes
    previous_date=dates[0]
    days_interval = timedelta(days=150)
    for date, level, codes in zip(dates, set_plots_levels([-12, 12, -10, 10, -8, 8, -6, 6, -4, 4, -2, 2], dates), codes):
        label="\n".join(codes)
        delta=date - previous_date
        if delta<days_interval:
            plt.text(date, level, label, bbox=dict(facecolor='white', linewidth=0), horizontalalignment='left', verticalalignment="bottom")
        elif delta>=days_interval:
            plt.text(date, level, label, bbox=dict(facecolor='white', linewidth=0), horizontalalignment='center')
        previous_date=date
    #show only years on the bottom spines
    date_format = mdates.DateFormatter("%Y")
    ax.xaxis.set_major_formatter(date_format)
    #increase the length of the bottom spines tick associated with years
    plt.tick_params(axis='x', length=10)
    # remove y-axis and spines (borders around the figure) + move the bottom border with years to the middle of the plot
    ax.yaxis.set_visible(False)
    ax.spines[["left", "top", "right"]].set_visible(False)
    ax.spines[["bottom"]].set_position("center")
    ax.spines[["bottom"]].set_zorder(0)
    ax.margins(y=0.1)
    plt.show()


def main():
    #name_of_the_file='231017_002_ICD10dgncodes_dummy_MN.txt'
    # 231017_002_ICD10dgncodes_dummy_MN.txt
    path_of_the_file=input("enter file path: ")
    
    #path_of_the_file = '231017_002_ICD10dgncodes_dummy_MN.txt'
    
    dict_date_codes=get_array_for_a_plot(path_of_the_file)
    np_date_codes=dict_to_numpy(dict_date_codes)
    plot(np_date_codes)

if __name__ == '__main__':
    main()
