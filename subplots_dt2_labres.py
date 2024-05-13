import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
# from disease_trajectory import *
from bubble_plot2 import *
from lab_panel import *
import pandas as pd
import numpy as np

global ribbon_width
ribbon_width=8
global test_type_colors
test_type_colors={"B-Hb":"#D62728","S,P-ALAT":"#1F77B4"}
global colors
colors=px.colors.qualitative.Dark24
global previous_terminal_points
previous_terminal_points=None
global test_heights, prev_x_range
test_heights=None
prev_x_range=None

def get_data_disease_traj_type2(path_of_the_file):
    if path_of_the_file is not None:
        # dict_date_codes=get_array_for_a_plot(path_of_the_file)
        decoded = base64.b64decode(path_of_the_file[0])
        decoded_file=decoded.decode('unicode_escape')
        disease_history_df = pd.read_csv(StringIO(decoded_file), sep='\t', encoding= 'unicode_escape')
        # disease_history_df = pd.read_csv(path_of_the_file,sep='\t',encoding= 'unicode_escape')
        codes_array = np.asarray(disease_history_df['DiagnosisConsolidated icd10 code'])
        date_of_diagnosis_array = np.asarray(disease_history_df['DiagnosisConsolidated earliestDate'])
        #convert string to time
        dates = [datetime.strptime(d, "%Y-%m-%d") for d in date_of_diagnosis_array]
        df_codes_years=np.column_stack((dates, codes_array))
        return df_codes_years

def extract_data_by_range(data_dt,xrange):
    date_start=xrange[0]
    date_end=xrange[1]
    selected_rows=[]
    for row in data_dt:
        date=row[0]   
        if date>date_start:
            if date<date_end:
                new_line=[date,row[1]]
                selected_rows.append(new_line)
    rows_in_range=np.array(selected_rows)
    return rows_in_range


def extract_data_by_letters(data_dt,letters):
    selected_rows=[]
    for row in data_dt:
        date=row[0]
        code=row[1]   
        if code[0] in letters:
            new_line=[date,code]
            selected_rows.append(new_line)
    rows_in_range=np.array(selected_rows)
    return rows_in_range

def main_plot_dt2_labpanel(data_dt, data_lab_res, shared_x_range_dates, test_types, font_size, letters):
    global test_heights, prev_x_range
    fig=go.Figure()
    if data_dt is not None:
        data_dt=extract_data_by_range(data_dt, shared_x_range_dates)
        data_dt=extract_data_by_letters(data_dt,letters)
    if len(letters)==0:
        data_dt=None
    fig.update_layout(xaxis=dict(range=shared_x_range_dates))
    shared_x_range_dates=shared_x_range_dates
    if data_dt is not None and data_lab_res is not None:
        arr1=append_y_coordinates(data_dt)
        np_arr1 = np.array(arr1)
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
        fig=bubble_plot2(fig,np_arr1,shared_x_range_dates, font_size) #should be normal array
        for test in test_types:
            test_results=get_results_one_test(data_lab_res, test)
            fig=add_lab_res_panel(fig, test_results, shared_x_range_dates)
        # fig=bubble_plot2(fig,np_arr1) #should be normal array
        test_heights=get_test_heights_dict()
        if len(test_types)!=0:
            max_test_hight=find_ymax_lst2(test_heights)
            min_test_hight=find_ymin_lst2(test_heights)
            ymax=max_test_hight+ribbon_width
            fig['layout']['yaxis2'].update(range=[min_test_hight-1, ymax])
        fig['layout']['xaxis2'].update(range=shared_x_range_dates)
        fig['layout']['xaxis1'].update(range=shared_x_range_dates)
        if len(test_types)==0:
            fig.update_layout(plot_bgcolor = "white",
                    font = dict(family='AppleGothic', color = "black"),
                    title = None,
                    xaxis = dict(showticklabels=True, showline=True, showgrid=False, titlefont=dict(size=14)),
                    yaxis = dict(showticklabels=False, showline=True, zeroline=True, zerolinecolor='black', zerolinewidth=2, showgrid=False)
                    )  
            # fig.update_xaxes(linecolor="black",showgrid=False, ticks="outside", tickson="boundaries", ticklen=11,title = "Years", tickfont = dict(size=18), tickwidth=3,row=2, col=1)
            fig.update_xaxes(showline = True, linecolor = 'black', linewidth = 3, mirror = False, row=1, col=1)
            fig.update_yaxes(showline = False, showticklabels=True, row=1, col=1)
            fig.update_xaxes(linecolor="black",showgrid=False, ticks="outside", tickson="boundaries", ticklen=11,title = "Years", tickfont = dict(size=18), tickwidth=3,row=1, col=1)
            fig.update_layout(margin=dict(b=50))
        else:
            fig.update_layout(plot_bgcolor = "white",
                        font = dict(family='AppleGothic', color = "black"),
                        title = None,
                        xaxis = dict(showticklabels=False, showline=False, showgrid=False, titlefont=dict(size=14)),
                        yaxis = dict(showticklabels=False, showline=False, zeroline=True, zerolinecolor='black', zerolinewidth=2, showgrid=False)
                        )  
            custom_tickvals=[sublist[1]+4 for sublist in test_heights]
            custom_ticktext=[sublist[0] for sublist in test_heights]
            fig['layout']['yaxis2'].update(tickmode='array',tickvals=custom_tickvals, ticktext=custom_ticktext, tickfont=dict(size=16, family="AppleGothic",color='black'))
            fig.update_yaxes(showline = False, showticklabels=True, row=1, col=1)
            fig.update_xaxes(linecolor="white",showgrid=False, ticks="outside", tickson="boundaries", ticklen=11,title = "Years", tickfont = dict(size=18), tickwidth=3,row=2, col=1)
            fig.update_xaxes(showline = True, linecolor = 'black', linewidth = 3, mirror = False, row=2, col=1)
            fig.update_yaxes(showline = False, showticklabels=True, row=2, col=1)

    elif data_dt is not None and data_lab_res is None:
        arr1=append_y_coordinates(data_dt)
        np_arr1 = np.array(arr1)
        shared_x_range=pd.to_datetime(shared_x_range_dates, format='%Y')
        shared_axis=False
        plots_ratio=[1, 0]
        vert_space=0.2
        fig = make_subplots(rows=2,cols=1,shared_xaxes=shared_axis,row_heights=plots_ratio,vertical_spacing=vert_space)
        # fig.update_layout(xaxis=dict(range=shared_x_range_dates))
        # Update layout with constant x-axis range
        fig.update_layout(xaxis=dict(range=shared_x_range_dates))
        fig['layout']['xaxis1'].update(range=shared_x_range_dates)
        fig=bubble_plot2(fig,np_arr1,shared_x_range, font_size)
        # fig['layout']['xaxis1'].update(range=shared_x_range_dates)

        fig.update_layout(plot_bgcolor = "white",
                    font = dict(family='AppleGothic', color = "black"),
                    title = None,
                    xaxis = dict(showticklabels=True, showline=True, showgrid=False, titlefont=dict(size=14)),
                    yaxis = dict(showticklabels=False, showline=True, zeroline=True, zerolinecolor='black', zerolinewidth=2, showgrid=False)
                    )  
        # fig.update_xaxes(linecolor="black",showgrid=False, ticks="outside", tickson="boundaries", ticklen=11,title = "Years", tickfont = dict(size=18), tickwidth=3,row=2, col=1)
        fig.update_xaxes(showline = True, linecolor = 'black', linewidth = 3, mirror = False, row=1, col=1)
        fig.update_yaxes(showline = False, showticklabels=True, row=1, col=1)
        fig.update_xaxes(linecolor="black",showgrid=False, ticks="outside", tickson="boundaries", ticklen=11,title = "Years", tickfont = dict(size=18), tickwidth=3,row=1, col=1)
        
    elif data_dt is None and data_lab_res is not None: 
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
        fig.update_layout(xaxis=dict(range=shared_x_range_dates))
        for test in test_types:
            test_results=get_results_one_test(data_lab_res, test)
            fig=add_lab_res_panel(fig, test_results,shared_x_range)
        test_heights=get_test_heights_dict()
        if len(test_types)!=0:
            max_test_hight=find_ymax_lst2(test_heights) #
            min_test_hight=find_ymin_lst2(test_heights) #
            ymax=max_test_hight+ribbon_width
            fig['layout']['yaxis2'].update(range=[min_test_hight-1, ymax])
        fig['layout']['xaxis2'].update(range=shared_x_range_dates)
        fig.update_layout(plot_bgcolor = "white",
                    font = dict(family='AppleGothic', color = "black"),
                    title = None,
                    xaxis = dict(showticklabels=False, showline=False, showgrid=False, titlefont=dict(size=14)),
                    yaxis = dict(showticklabels=False, showline=False, zeroline=False, zerolinecolor='black', zerolinewidth=2, showgrid=False)
                    ) 
        # fig.update_traces(textfont=dict(size = font_size))
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
    fig.update_layout(
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
        # hovermode="x unified"
    )
    fig.update_traces(textfont=dict(size = font_size))
    fig.update_layout(xaxis=dict(range=shared_x_range_dates))
    fig.update_layout(yaxis=dict(fixedrange=True))
    # fig.update_layout(font=dict(size=font_size))
    prev_x_range=fig.layout.xaxis.range
    return fig

def find_ymax_lst2(lst_tests):
    y_vals=[]
    for little_list in lst_tests:
        y_vals.append(little_list[1])
    return max(y_vals)

def find_ymin_lst2(lst_tests):
    y_vals=[]
    for little_list in lst_tests:
        y_vals.append(little_list[1])
    return min(y_vals)

def main():
    icd10_codes_file="231017_002_ICD10dgncodes_dummy_MN.txt"
    lab_results_file="240202_labresults_002_forUscia_MN.txt"
    font_size=30
    data_dt=get_data_disease_traj_type2(icd10_codes_file)
    # data_lab_res=get_array_for_a_plot_lr(lab_results_file)
    data_lab_res=None
    x=[2005, 2023]
    xx=pd.to_datetime(x, format='%Y')
    test_types=["B-Hb","S,P-ALAT","502","509"]
    fig=main_plot_dt2_labpanel(data_dt, data_lab_res, xx, test_types, font_size)
    fig.show()

if __name__=="__main__":
    main()