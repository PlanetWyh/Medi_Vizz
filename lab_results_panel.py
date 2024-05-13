from datetime import datetime, timedelta
#from disease_trajectory import *
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import base64
from io import StringIO

global test_type_colors
test_type_colors={"B-Hb":"#D62728","S,P-ALAT":"#1F77B4"}
global test_heights
test_heights=dict()
global test_types 
test_types=['B-Hb','S,P-ALAT']

#extract matrix of three columns: date of test, type of test, numerical result
def get_array_for_a_plot_lr(file):
    #decode the file received
    decoded = base64.b64decode(file[0])
    decoded_file=decoded.decode('unicode_escape')
    disease_history_df = pd.read_csv(StringIO(decoded_file), sep='\t', encoding= 'unicode_escape')
    # disease_history_df = pd.read_csv(file, sep='\t', encoding= 'unicode_escape')
    date_of_test=np.asarray(disease_history_df['MeasurementAssembled measurementDate'])
    measurment_type=np.asarray(disease_history_df['MeasurementAssembled measurementType'])
    measurment_numeric_result=np.asarray(disease_history_df['MeasurementAssembled measurementResultNumeric'])
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in date_of_test]
    df_dates_type_result=np.column_stack((dates, measurment_type, measurment_numeric_result))
    return df_dates_type_result

def get_dropdown_menu(data):
    unique_tests=np.unique(data)
    return unique_tests

#extract rows of specific result
def get_results_one_test(array, test_type):
    new_array=array[np.any(array == test_type, axis=1)]
    return new_array    

#calculate the period between dates of tests to prevent overlap
def calculate_min_distance(dates):
    date_intervals=[]
    previous_date=None
    for date in dates:
        if previous_date is not None:
            delta=date-previous_date
            date_intervals.append(delta)
        previous_date=date
    interval=min(date_intervals)-relativedelta(days=10)
    return interval

def plot_test_type(data,fig): #order of data: data type result
    global test_type_colors
    #define constants
    code_level=2
    scatter_levels=[]
    test_heights_color=[]
    #distance between boxes
    smallets_date_interval=calculate_min_distance(data[:,0])
    smal_date_interval_timedelta = datetime.now() - (datetime.now() + smallets_date_interval)
    if smal_date_interval_timedelta>timedelta(days=270):
        smal_date_interval_timedelta=relativedelta(months=9)
    #y-coordinates of boxes
    if len(test_heights)==0:
        code_level=0 #code_level=plot_levels[first_letter]
        # test_heights[data[0,1]]=code_level  
        test_heights_color.append([data[0,1],code_level])
    else:
        if data[0,1] in test_heights:
            index=find_element_index(test_heights_color, data[0,1])
            code_level=test_heights_color[index][1]
            # code_level=test_heights.get(data[0,1])
        elif data[0,1] not in test_heights:
            index=find_element_index(test_heights_color, data[0,1])
            code_level=len(test_heights_color)+1.5
            test_heights_color[index].append(code_level)
            # code_level=len(test_heights)+1.5 
            # test_heights[data[0,1]]=code_level

    for triplets in data:
        scatter_levels.append(code_level)
        fig.add_shape(
            type="line", x0=triplets[0], y0=code_level, x1=triplets[0], y1=code_level+1.2,
            line=dict(color=test_type_colors.get(triplets[1]),width=4),
            label=dict(text=triplets[2], textangle=0, textposition="top center", padding=35)
        )        
        
    fig.add_trace(go.Scatter(x=data[:,0], y=scatter_levels, mode="markers", 
                             marker=dict(color=test_type_colors.get(data[0,1]),size=3), 
                             showlegend=False))
    return fig

#convert dictionaty to numpy array for plotting
def dict_to_numpy(dictionary):
    keys = list(dictionary.keys())
    values = list(dictionary.values())
    array_from_dict = np.array(list(zip(keys, values)), dtype=[('key', 'U10'), ('value', object)])
    return array_from_dict

def get_terminal_dates_lp(path_of_the_file):
    np_date_codes=get_array_for_a_plot_lr(path_of_the_file)
    dates=[]
    for pair in np_date_codes:
        dates.append(pair[0])
    terminal_dates=[dates[0],dates[-1]]
    return terminal_dates

def make_title(test_types):
    test_types_string=", ".join(test_types)
    title="Results for {0}".format(test_types_string)
    return title

def get_test_heights():
    global test_heights
    # print(test_heights)
    return test_heights

def get_test_color():
    global test_type_colors
    # print(test_type_colors)
    return test_type_colors

def add_lab_panels(fig,terminal_points):
    global test_types
    test_heights_dict=get_test_heights()
    test_colors=get_test_color()
    for test in test_types:
        fig.add_shape(
            type="rect",
            x0=terminal_points[0],y0=test_heights_dict.get(test),
            x1=terminal_points[1],y1=test_heights_dict.get(test)+2,
            line_width=0,
            label=dict(text=test, textposition="middle left", font=dict(size=20)),
            fillcolor=test_colors.get(test),
            opacity=0.25,
        )
    return fig


def main():
    path_of_the_file="240202_labresults_002_forUscia_MN.txt"
    fig=lab_results_panel(path_of_the_file,test_types)
    fig.show()


if __name__ == '__main__':
    main()
