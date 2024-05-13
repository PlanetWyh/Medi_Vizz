import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from disease_trajectory_type1_v2 import *
from lab_panel import *
import pandas as pd
import numpy as np
import os

global ribbon_width
ribbon_width=8
global test_type_colors
test_type_colors={"B-Hb":"#D62728","S,P-ALAT":"#1F77B4"}
global colors
colors=px.colors.qualitative.Dark24
global previous_terminal_points
previous_terminal_points=None
global test_heights
test_heights=None

def get_2plots_range(file_dt, file_lr):
    #extract dates from the disease trajectory file
    dict_date_codes_dt=get_array_for_a_plot(file_dt)
    dates_dt=list(dict_date_codes_dt.keys())
    #extract dates from the lab results
    np_date_type_result=get_array_for_a_plot_lr(file_lr)
    dates_lst_lr=list(np_date_type_result[:,0])
    dates_lst_lr.sort()
    lower_limit=[dates_lst_lr[0],dates_dt[0]]
    upper_limit=[dates_lst_lr[-1],dates_dt[-1]]
    x1=min(lower_limit)-relativedelta(years=1)
    x2=max(upper_limit)+relativedelta(years=2)
    return [x1,x2]

def get_plot_range_distraj(file):
    #extract dates from the disease trajectory file
    dict_date_codes_dt=get_array_for_a_plot(file)
    dates_dt=list(dict_date_codes_dt.keys())
    lower_limit=dates_dt[0]
    upper_limit=dates_dt[-1]
    x1=lower_limit-relativedelta(years=1)
    x2=upper_limit+relativedelta(years=2)
    return [x1,x2]

def get_data_disease_traj_type1(path_of_the_file):
    data=get_array_for_a_plot_type1_v2(path_of_the_file)
    # print(data)
    return data

def main_plot(data_dt, data_lab_res, shared_x_range_dates, test_types, font_size, letters):
    global test_heights
    fig=go.Figure()
    # test_heights=heights_dict(test_types)
    if data_dt is not None and data_lab_res is not None:
        heights_dict(test_types)
        if len(test_types)==0:
            shared_axis=False
            plots_ratio=[1, 0]
            vert_space=0.2
        else: 
            shared_axis=True
            plots_ratio=[0.6, 0.4]
            vert_space=0.02    
        fig = make_subplots(rows=2,cols=1,shared_xaxes=shared_axis,row_heights=plots_ratio,vertical_spacing=vert_space)
        fig.update_layout(xaxis=dict(range=shared_x_range_dates))
        for test in test_types:
            test_results=get_results_one_test(data_lab_res, test)
            fig=add_lab_res_panel(fig, test_results, shared_x_range_dates)
        fig=disease_trajectory_type1(fig, data_dt, shared_x_range_dates, font_size, letters)
        test_heights=get_test_heights_dict()
        if len(test_types)!=0:
            max_test_hight=find_ymax_lst(test_heights)
            min_test_hight=find_ymin_lst(test_heights)
            ymax=max_test_hight+ribbon_width
            fig['layout']['yaxis2'].update(range=[min_test_hight-1, ymax])
            # print([min_test_hight-1, ymax])
        fig['layout']['xaxis2'].update(range=shared_x_range_dates)
        fig['layout']['xaxis1'].update(range=shared_x_range_dates)
        if len(test_types)==0:
            fig.update_layout(plot_bgcolor = "white",
                    font = dict(family='AppleGothic', color = "black", size = 18),
                    title = None,
                    xaxis = dict(showticklabels=True, showline=True),
                    yaxis = dict(showticklabels=False, showline=True, zeroline=True, zerolinecolor='black', zerolinewidth=2)
                    )  
            # fig.update_xaxes(linecolor="black",showgrid=False, ticks="outside", tickson="boundaries", ticklen=11,title = "Years", tickfont = dict(size=18), tickwidth=3,row=2, col=1)
            fig.update_xaxes(showline = True, linecolor = 'black', linewidth = 3, mirror = False, row=1, col=1)
            fig.update_yaxes(showline = False, showticklabels=False, row=1, col=1)
            fig.update_xaxes(linecolor="black",showgrid=False, ticks="outside", tickson="boundaries", ticklen=11,title = "Years", tickfont = dict(size=18), tickwidth=3,row=1, col=1)
            fig.update_layout(margin=dict(b=50))
        else:
            fig.update_layout(plot_bgcolor = "white",
                        font = dict(family='AppleGothic', color = "black", size = 10),
                        title = None,
                        xaxis = dict(showticklabels=False, showline=False),
                        yaxis = dict(showticklabels=False, showline=False, zeroline=True, zerolinecolor='black', zerolinewidth=2)
                        )  
            fig.update_xaxes(linecolor="white",showgrid=False, ticks="outside", tickson="boundaries", ticklen=11,title = "Years", tickfont = dict(size=18), tickwidth=3,row=2, col=1)
            fig.update_xaxes(showline = True, linecolor = 'black', linewidth = 3, mirror = False, row=2, col=1)
            fig.update_yaxes(showline = False, showticklabels=True, row=2, col=1)
            custom_tickvals=[sublist[1]+4 for sublist in test_heights]
            custom_ticktext=[sublist[0] for sublist in test_heights]
            fig['layout']['yaxis2'].update(tickmode='array',tickvals=custom_tickvals, ticktext=custom_ticktext, tickfont=dict(size=16, family="AppleGothic",color='black'))
        
    elif data_dt is not None and data_lab_res is None:
        shared_x_range=pd.to_datetime(shared_x_range_dates, format='%Y')
        shared_axis=False
        plots_ratio=[1, 0]
        vert_space=0.2
        fig = make_subplots(rows=2,cols=1,shared_xaxes=shared_axis,row_heights=plots_ratio,vertical_spacing=vert_space)
        fig.update_layout(xaxis=dict(range=shared_x_range))
        fig=disease_trajectory_type1(fig, data_dt, shared_x_range_dates, font_size, letters)
        fig['layout']['xaxis1'].update(range=shared_x_range)
        fig.update_layout(plot_bgcolor = "white",
                    font = dict(family='AppleGothic', color = "black", size = 14),
                    title = None,
                    xaxis = dict(showticklabels=True, showline=True),
                    yaxis = dict(showticklabels=False, showline=True, zeroline=True, zerolinecolor='black', zerolinewidth=2)
                    )  
        # fig.update_xaxes(linecolor="black",showgrid=False, ticks="outside", tickson="boundaries", ticklen=11,title = "Years", tickfont = dict(size=18), tickwidth=3,row=2, col=1)
        fig.update_xaxes(showline = True, linecolor = 'black', linewidth = 3, mirror = False, row=1, col=1)
        fig.update_yaxes(showline = False, showticklabels=False, row=1, col=1)
        fig.update_xaxes(linecolor="black",showgrid=False, ticks="outside", tickson="boundaries", ticklen=11,title = "Years", tickfont = dict(size=18), tickwidth=3,row=1, col=1)
    elif data_dt is None and data_lab_res is not None: 
        # print(test_types)
        heights_dict(test_types)
        dates_lst_lr=list(data_lab_res[:,0])
        dates_lst_lr.sort()
        lower_limit=dates_lst_lr[0]
        upper_limit=dates_lst_lr[-1]
        x1=lower_limit-relativedelta(years=1)
        x2=upper_limit+relativedelta(years=2)
        shared_x_range=[x1,x2]
        shared_axis=False
        plots_ratio=[0, 1]
        vert_space=0.2
        fig = make_subplots(rows=2,cols=1,shared_xaxes=shared_axis,row_heights=plots_ratio,vertical_spacing=vert_space)
        fig.update_layout(xaxis=dict(range=shared_x_range))
        for test in test_types:
            test_results=get_results_one_test(data_lab_res, test)
            fig=add_lab_res_panel(fig, test_results,shared_x_range)
        test_heights=get_test_heights_dict()
        # print("subplots",test_heights)
        if len(test_types)!=0:
            # print('aaaa')
            max_test_hight=find_ymax_lst(test_heights) #
            min_test_hight=find_ymin_lst(test_heights) #
            ymax=max_test_hight+ribbon_width
            fig['layout']['yaxis2'].update(range=[min_test_hight-1, ymax])
        fig['layout']['xaxis2'].update(range=shared_x_range)
        fig.update_layout(plot_bgcolor = "white",
                    font = dict(family='AppleGothic', color = "black", size = 16),
                    title = None,
                    xaxis = dict(showticklabels=False, showline=False),
                    yaxis = dict(showticklabels=False, showline=False, zeroline=False, zerolinecolor='black', zerolinewidth=2)
                    )  
        fig.update_xaxes(linecolor="white",showgrid=False, ticks="outside", tickson="boundaries", ticklen=11,title = "Years", tickfont = dict(size=18), tickwidth=3,row=2, col=1)
        custom_tickvals=[sublist[1]+4 for sublist in test_heights]
        custom_ticktext=[sublist[0] for sublist in test_heights]
        fig['layout']['yaxis2'].update(tickmode='array',tickvals=custom_tickvals, ticktext=custom_ticktext, tickfont=dict(size=16, family="AppleGothic",color='black'))
        fig.update_xaxes(showline = True, linecolor = 'black', linewidth = 3, mirror = False, row=2, col=1)
        fig.update_yaxes(showline = False, showticklabels=True, row=2, col=1)
    else:
        fig.update_layout(plot_bgcolor = "white",
                    font = dict(family='AppleGothic', color = "black", size = 18),
                    title = None,
                    xaxis = dict(showticklabels=False, showline=False),
                    yaxis = dict(showticklabels=False, showline=False)
                    )  
        # print("upload some files")
    fig.update_layout(
        # autosize=True,
        # hovermode="x unified",
        minreducedwidth=500,
        minreducedheight=500,
        autosize=True,
        width=1150,
        height=640,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0
        ),
    )
    fig.update_layout(xaxis=dict(range=shared_x_range_dates))
    fig.update_layout(yaxis=dict(fixedrange=True))
    return fig

def find_ymax_lst(lst_tests):
    y_vals=[]
    for little_list in lst_tests:
        y_vals.append(little_list[1])
    return max(y_vals)

def find_ymin_lst(lst_tests):
    y_vals=[]
    for little_list in lst_tests:
        y_vals.append(little_list[1])
    return min(y_vals)

def extract_data_by_letters_for_saving(data_dt,letters):
    selected_rows=[]
    for row in data_dt:
        date=row[0]
        code=row[1]   
        if code[0] in letters:
            new_line=[date,code]
            # print(new_line)
            selected_rows.append(new_line)
    rows_in_range=np.array(selected_rows)
    # print('rows',rows_in_range[0],rows_in_range[-1])
    return rows_in_range

def plot_save(figure, file_name):
    if not os.path.exists("images"):
        os.mkdir("images")
    name='images/{0}.svg'.format(file_name)
    figure.write_image(name)
    # pio.to_image(figure, format="svg", width=800, height=600, scale=1.0, engine="kaleido")

def data_for_saving(file_dt, file_labres, xrange, tests, letters):
    start_date=np.datetime64(xrange[0])
    end_date=np.datetime64(xrange[1])
    selected_data_lr=None
    selected_data_dt=None
    if file_dt is not None and file_labres is None:
        #get array from ICD10 file
        dates_dt,codes_dt=get_pairs_of_code_date(file_dt)
        dates_dt_datetime = np.array([np.datetime64(date) for date in dates_dt])
        df_dates_codes_dt=np.column_stack((dates_dt_datetime, codes_dt))
        #boolean indexing to select the rows within the date range
        selected_rows = (dates_dt_datetime >= start_date) & (dates_dt_datetime <= end_date)
        #use boolean indexing to select the rows within the date range
        selected_data_dt = df_dates_codes_dt[selected_rows]
    elif file_labres is not None and file_dt is None:
        #get array from lab results file
        df_dates_types_codes_lr=get_array_for_a_plot_lr(file_labres)
        for test in tests:
            #boolean indexing to select the rows within the date range
            selected_rows = (df_dates_types_codes_lr[:,0] >= start_date) & (df_dates_types_codes_lr[:,0] <= end_date) & (df_dates_types_codes_lr[:,1] == test)
        #use boolean indexing to select the rows within the date range
            if selected_data_lr is None:
                selected_data_lr = df_dates_types_codes_lr[selected_rows]
            else:
                for row in df_dates_types_codes_lr[selected_rows]:
                    selected_data_lr = np.vstack([selected_data_lr, row])
    elif file_labres is not None and file_dt is not None:
        #get array from ICD10 file
        dates_dt,codes_dt=get_pairs_of_code_date(file_dt)
        dates_dt_datetime = np.array([np.datetime64(date) for date in dates_dt])
        df_dates_codes_dt=np.column_stack((dates_dt_datetime, codes_dt))
        #boolean indexing to select the rows within the date range
        selected_rows_dt = (dates_dt_datetime >= start_date) & (dates_dt_datetime <= end_date)
        #use boolean indexing to select the rows within the date range
        selected_data_dt = df_dates_codes_dt[selected_rows_dt]

        #get array from lab results file
        selected_data_lr=None
        df_dates_types_codes_lr=get_array_for_a_plot_lr(file_labres)
        for test in tests:
            #boolean indexing to select the rows within the date range
            selected_rows = (df_dates_types_codes_lr[:,0] >= start_date) & (df_dates_types_codes_lr[:,0] <= end_date) & (df_dates_types_codes_lr[:,1] == test)
        #use boolean indexing to select the rows within the date range
            if selected_data_lr is None:
                selected_data_lr = df_dates_types_codes_lr[selected_rows]
            else:
                for row in df_dates_types_codes_lr[selected_rows]:
                    selected_data_lr = np.vstack([selected_data_lr, row])
    else:
        selected_data_lr=None
        selected_data_dt=None
    if selected_data_dt is not None:
        selected_data_dt=extract_data_by_letters_for_saving(selected_data_dt,letters)
    return selected_data_dt, selected_data_lr

def main():
    icd10_codes_file="231017_002_ICD10dgncodes_dummy_MN.txt"
    lab_results_file="240202_labresults_002_forUscia_MN.txt"
    data_dt=get_data_disease_traj_type1(icd10_codes_file)
    data_lab_res=get_array_for_a_plot_lr(lab_results_file)
    # shared_x_range=get_plot_range(icd10_codes_file,lab_results_file)
    x=[2005, 2023]
    xx=pd.to_datetime(x, format='%Y')
    test_types=["B-Hb","S,P-ALAT","502","509"]
    fig=main_plot(data_dt, data_lab_res, xx, test_types, 12)
    fig.show()

if __name__=="__main__":
    main()