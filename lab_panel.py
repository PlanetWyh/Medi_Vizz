import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from disease_trajectory import *
from lab_results_panel import *
import pandas as pd
import numpy as np

global test_type_colors
test_type_colors={"B-Hb":"#D62728","S,P-ALAT":"#1F77B4"}
global test_heights_colors
test_heights_colors=dict()
global ribbon_width
ribbon_width=8
global colors
colors=px.colors.qualitative.Dark24
global test_level_color_lst
test_level_color_lst=[]
global constat_range, constat_range_assigned
constat_range=None
constat_range_assigned=None

def get_plot_range_labres(file):
    #extract dates from the lab results
    np_date_type_result=get_array_for_a_plot_lr(file)
    dates_lst_lr=list(np_date_type_result[:,0])
    dates_lst_lr.sort()
    lower_limit=dates_lst_lr[0]
    upper_limit=dates_lst_lr[-1]
    x1=lower_limit-relativedelta(years=1)
    x2=upper_limit+relativedelta(years=2)
    return [x1,x2]

def create_levels(data, result):
    if len(data[:,2])>1:
        min_result=min(data[:,2])
        max_result=max(data[:,2])
        old_range=(max_result-min_result)  
        new_range=4 #range of the spikes level of one lab result
        result_level=(((result-min_result)*new_range)/old_range)+2 #one is where the spikes will start from the bottom of the ribbon
    else:
        result_level=2
    return result_level

def heights_dict(test_sel):
    global test_level_color_lst
    # current_lst=get_test_heights_dict()
    items_to_delete=[]
    for test in test_level_color_lst:
        if test[0] not in test_sel:
            items_to_delete.append(test[0])
    for item in items_to_delete:
        i,j=find_element_index(test_level_color_lst, item)
        test_level_color_lst.pop(i)
    # Iterate over the keys and update their values
    for i,small_lst in enumerate(test_level_color_lst):
        small_lst[1]=i*10
        small_lst[2]=colors[i]

def find_element_index(lst_of_lsts, element):
    for i, sublist in enumerate(lst_of_lsts):
        if element in sublist:
            return i, sublist.index(element)
    return None

def check_presence(test,lst):
    presence=None
    tests=[]
    for small_lst in lst:
        tests.append(small_lst[0])
    if test in tests:
        presence=True
    else:
        presence=False
    return presence

def add_lab_res_panel(fig,data,xrange):
    global constat_range, constat_range_assigned
    if constat_range is None:
        constat_range=xrange
    if constat_range is not None:
        if xrange[0]<constat_range[0]:
            constat_range[0]=xrange[0]
        if xrange[1]>constat_range[1]:
            constat_range[1]=xrange[1]
    #define constants
    code_level=4
    scatter_levels=[]
    #y-coordinates of boxes
    if len(test_level_color_lst)==0:
        code_level=0 
        code_color=colors[0]
        test_level_color_lst.append([data[0,1],code_level,code_color])
    else:
        test_present=check_presence(data[0,1],test_level_color_lst)
        if test_present:
            i,j=find_element_index(test_level_color_lst, data[0,1])
            code_level=test_level_color_lst[i][1]
            code_color=test_level_color_lst[i][2] 
        else:
            code_level=len(test_level_color_lst)*(2+ribbon_width)
            code_color=colors[len(test_level_color_lst)]
            test_level_color_lst.append([data[0,1],code_level,code_color])

    for triplets in data:
        scatter_levels.append(code_level+create_levels(data, triplets[2]))
        fig.add_shape(
            dict(type="line", x0=triplets[0], x1=triplets[0], 
                 y0=code_level, y1=code_level+create_levels(data, triplets[2]), 
                 line_color=code_color, line_width=4,
                #label=dict(text=triplets[2], textangle=0, textposition="middle center", padding=20)# xanchor="center")
            ), 
            row=2, col=1
        )

    fig.append_trace(go.Scatter(x=data[:,0], y=scatter_levels, mode="markers", name="", hovertemplate = 'Date: %{x|%d-%b-%Y}<br>',
                            marker=dict(color=code_color,size=3), 
                            showlegend=False),row=2, col=1)
    
    # Add a scatter plot trace with adjusted y values
    formatted_results=[f'{num:.2f}' for num in data[:,2]]
    labels_levels=[level for level in scatter_levels]
    fig.add_trace(go.Scatter(x=data[:,0], y=labels_levels, text=formatted_results, 
                             textposition="top right", mode="text", showlegend=False,
                             hovertemplate = 'Date: %{x|%d-%b-%Y}<br>'),
                             row=2,col=1)
    print(constat_range)
    fig.add_shape(
        dict(type="rect", x0=constat_range[0]-timedelta(weeks=100), x1=constat_range[1]+timedelta(weeks=100), 
                y0=code_level, y1=code_level+ribbon_width, 
                line_color=code_color, line_width=0,
            fillcolor=code_color, opacity=0.25,
            # label=dict(text=data[0,1], textposition="middle left", textangle=0)
        ), 
        row=2, col=1
    )
    fig.update_layout(
        # autosize=True,
        # hovermode="x unified",
        minreducedwidth=500,
        minreducedheight=500,
        autosize=True,
        width=1150,
        height=650,
        margin=dict(
            l=0,
            r=0,
            b=50,
            t=0,
            pad=0
        ),
    )
    
    return fig

def get_test_heights_dict():
    global test_level_color_lst
    return test_level_color_lst

def main():
    lab_results_file="240202_labresults_002_forUscia_MN.txt"
    data_lab_res=get_array_for_a_plot_lr(lab_results_file)
    fig=make_subplots(rows=2, cols=1)
    test_results1=get_results_one_test(data_lab_res, 'B-Hb')
    fig=add_lab_res_panel(fig,test_results1)
    # fig.show()

if __name__=="__main__":
    main()