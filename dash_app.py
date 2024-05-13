from dash import Dash, dcc, html, Input, Output, callback, State, ctx
import plotly.graph_objs as go
from subplots_dt1_labres import *
from subplots_dt2_labres import *
from dateutil.relativedelta import relativedelta
import pandas as pd
import dash_bootstrap_components as dbc
import os
from threading import Timer
import webbrowser
import kaleido

def align_lists(test_sel):
    global test_level_color_lst
    current_lst=get_test_heights_dict()
    items_to_delete=[]
    for test in current_lst:
        if test[0] not in test_sel:
            items_to_delete.append(test)
    for item in items_to_delete:
        index=find_element_index(current_lst, item)
        current_lst.pop(index)
    # Iterate over the keys and update their values
    for i,small_lst in enumerate(current_lst):
        small_lst[1]=i*10
        small_lst[2]=colors[i]
    return current_lst
    
# Function to split the long text into chunks
def split_text(text, chunk_size):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# load_figure_template("LUX")
#define constants
global icd10_codes_file,lab_results_file, previous_xrange,slider_present
#change the directories
icd10_codes_file=None
lab_results_file=None
global test_types
test_types=[]    
global prev_clicks
prev_clicks=None
slider_present=False
global default_min, default_max
default_min=None
default_max=None
#determine the biggest interval which fits all values
global shared_x_range, x1, x2, prev_display_button
shared_x_range=None
previous_xrange=shared_x_range
prev_display_button=0
global current_plot_type
current_plot_type=1


#extract data
global data_lab_res, data_dt, data_dt2
data_lab_res=None
data_dt=None
data_dt2=None
global  prev_but_min, prev_but_res, prev_but_max, font_size, marker_size, icd10_dropdow_options
constant_x_range=None
prev_but_min=0
prev_but_res=0
prev_but_max=0
font_size=8
marker_size=25
icd10_dropdow_options=[]
#create plot
global dis_traj1_and_lab_res_plot, figure, icd10_codes_to_plot
icd10_codes_to_plot=[]
dis_traj1_and_lab_res_plot=main_plot(data_dt, data_lab_res, shared_x_range, [], font_size, [])
figure=dis_traj1_and_lab_res_plot
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.icons.BOOTSTRAP, 'dropdown_lab.css'] #, dbc.themes.LUX
exrernal_scripts=external_scripts = [
    {
        'src': 'https://code.jquery.com/jquery-3.5.1.slim.min.js',
        'integrity': 'sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj',
        'crossorigin': 'anonymous'
    },
    {
        'src': 'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.bundle.min.js',
        'integrity': 'sha384-pzjw8f+cvOzX+qKTVQyK7fQTnZ5uD2DK7OG0nIcU8Xr4LQ2ST3g8W00ckH6Z+8N6',
        'crossorigin': 'anonymous'
    },
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js',
        'integrity': 'sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q',
        'crossorigin': 'anonymous'
    }
]

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 25,
    "left": 20,
    "bottom": 25,
    "background-color": "#f0f0f0",
    'overflowY':'auto',
    "border-radius": "15px",
    # 'width':'210px',
    'width':'15vw',
    'flex':'0 0 auto'
}
# content = dcc.RadioItems(['New York City', 'Montreal','San Francisco'], 'Montreal', labelStyle={'display':'block'})
sidebar = html.Div(
    [
        html.H1("Medi_Vizz", style={'margin': '10px', "color":'black','textAlign': 'center', 'font-family':"AppleGothic",'font-weight':"bold",
        'border-radius': '15px', 'letterSpacing': '3px','font-size':'24px'}),
        html.Hr(style={'borderColor': '#9e9e9e','opacity': '0.25', 'borderWidth': '0.5px', 'borderStyle': 'solid','width': '94%', 'margin': '0 auto'}),
        dcc.Upload(
                id='upload-data-distraj',
                children=html.Div([
                    # 'Drag and Drop or ',
                    html.A('Select File With ICD-10 Codes',style={'font-family':'AppleGothic','color':'black'})])
                    ,
                    style={'width': '92%',
            'height': '50px',
            'lineHeight': '50px',
            'borderWidth': '0px',
            'borderStyle': 'solid',
            'borderColor': '#9e9e9e',
            'backgroundColor':'white',
            'borderRadius': '15px',
            'textAlign': 'center',
            'color':'black',
            'font-size':'13px',
            'margin': '8px'},
                    multiple=True,className='upload'),
            html.Div(id='confirm-filename-dt',style={'font-family':'AppleGothic','font-size':'10px','margin-left':'10px','margin-top':'5px','color':'black','textAlign':'center','whiteSpace': 'normal','width':'14vw'}) ,
        dcc.RadioItems(['Plot type 1', 'Plot type 2'], 'Plot type 1', id='radio-items', labelStyle={'font-family':'AppleGothic', 'font-size':'13px','margin-left':'10px'}, inline=True, className='radio-item'),
        html.Div(dcc.Dropdown(
                                id='dropdown-icd-10',
                                options=[],
                                multi=True,
                                searchable=True,
                                clearable=True,
                                placeholder='Select ICD-10 codes...',
                                style={ #CSS to hide the dropdown arrow,
                                 'height':'120px', 'width': '95%', 'textAlign':'center', 'margin-left':'5px','font-size':'13px','color':'black',
                                  'maxWidth':'254px',"borderWidth":'0px', "borderRadius":'15px','font-family':'AppleGothic',
                                 'margin-top':'10px'}
                                ),style={'background-color': '#f0f0f0'} ,className='inputbox'),
        html.Button('Display all codes', id='display-all', n_clicks=0, style={'textAlign':'center','font-size':'12px', 
                                                                       'color':'black', 'borderRadius': '15px', 
                                                                    'width':'90%','margin-left':'10px','margin-top': '10px',
                                                                    'font-family':'AppleGothic', 'font-color':'black', 'height':'35px','background-color':'#feb0e5', 'borderWidth': '0px'
                                                                    }, className='button-class-display'),
        html.Hr(style={'borderColor': '#9e9e9e','opacity': '0.25', 'borderWidth': '0.5px', 'borderStyle': 'solid','width': '94%', 'margin': '0 auto','margin-top':'10px'}),
        
        dcc.Upload(
                            id='upload-data-labres',
                            children=html.Div([
                                # 'Drag and Drop or ',
                                html.A('Select File With Lab Results',style={'font-family':'AppleGothic','color':'black'}),
                            ]),
                            style={'width': '92%',
            'height': '50px',
            'lineHeight': '50px',
            'borderWidth': '0px',
            'borderStyle': 'solid',
            'borderColor': '#9e9e9e',
            'backgroundColor':'white',
            'borderRadius': '15px',
            'textAlign': 'center',
            'color':'black',
            'font-size':'13px',
            'margin': '8px'},
                            # Allow multiple files to be uploaded
                            multiple=True),
            html.Div(id='confirm-filename-labres',style={'font-family':'AppleGothic','font-size':'10px',
                                                         'margin-left':'10px','margin-top':'5px',
                                                         'margin-bottom':'5px','color':'black',
                                                         'textAlign':'center','whiteSpace': 'normal', 'width':'14vw'}),
        html.Div(dcc.Dropdown(
                                id='dropdown-lab-results',
                                options=[],
                                multi=True,
                                searchable=True,
                                clearable=True,
                                placeholder='Select test types...',
                                style={ #CSS to hide the dropdown arrow,
                                 'height':'120px', 'width': '95%', 'textAlign':'center', 'margin-left':'5px','font-size':'13px','color':'black',
                                 'maxHeight':'150px', 'maxWidth':'254px',"borderWidth":'0px', "borderRadius":'15px','font-family':'AppleGothic'}
                                ),style={'background-color': '#f0f0f0'} ,className='inputbox'),
        
        html.H6("Change label size:", style={'textAlign':'center','font-size':'13px', 'color':'black','margin':'8px','font-family':'AppleGothic','color':'black'}),
        html.Div(id='zoom', children=html.Div([
                                html.Button('-', id='button-minimise', n_clicks=0, style={'margin-right':'4%', 'width':'30%', 'color':'black', 'height':'35px', 'borderRadius': '15px', 'background-color':'#feb0e5', 'borderWidth': '0px'}),
                                html.Button('0', id='button-reset', n_clicks=0,  style={'margin-right':'4%', 'width':'30%', 'height':'35px', 'borderRadius': '15px', 'background-color':'#feb0e5', 'borderWidth': '0px'}),
                                html.Button('+', id='button-maximise', n_clicks=0, style={'width':'30%', 'height':'35px', 'borderRadius': '15px', 'background-color':'#feb0e5', 'borderWidth': '0px'}),
                            ],
                              style={'display':'flex', 'width':'14vw', 'margin':'8px'}, className='buttons-zoom')),
        # style={'font-family':'AppleGothic','font-size':'10px','margin-left':'10px','margin-top':'5px','color':'black','textAlign':'center','whiteSpace': 'normal'}),
        html.Hr(style={'borderColor': '#9e9e9e','opacity': '0.25', 'borderWidth': '0.5px', 'borderStyle': 'solid','width': '92%','margin-top':'10px'}),
        html.H6("Enter the name of the file:", style={'textAlign':'center','font-size':'13px', 'color':'black','font-family':'AppleGothic','color':'black', 'margin':'8px'}),
        html.Div(dcc.Input(id='input-on-submit', type='text',style={'textAlign':'center','font-size':'13px', 'color':'black', 'width': '90%', 'margin-left':'8px', 'borderRadius': '15px', 'height':'35px'}),className='inputbox'),
        # html.P(['']),
        html.Button('Export data', id='export-val', n_clicks=0, style={'textAlign':'center','font-size':'13px', 
                                                                       'color':'black', 'borderRadius': '15px', 
                                                                    'width':'92%','margin':'8px', 'height':'35px',
                                                                    'margin-top':'10px','background-color':'#feb0e5',
                                                                    'borderWidth': '0px'}, className='button-class'),
        html.Div(id='confirm',
        style={'font-family':'AppleGothic','font-size':'10px','margin':'8px','color':'black','textAlign':'center','whiteSpace': 'normal', 'width':'14vw'})             
        ],
        
    style=SIDEBAR_STYLE)

# Initialize the Dash app
app = Dash(__name__)# external_scripts=external_scripts,  external_stylesheets=external_stylesheets)
# Define the layout of the Dash app
app.layout = html.Div(children=[
            html.Div(sidebar, className='sidebar'),
                html.Div(
                    dcc.Graph(
                    id='panel',
                    figure=dis_traj1_and_lab_res_plot,
                    style={'textAlign':'center',"position": "fixed",'flex': 'auto', 'overflowY':'auto', 'width':'80vw','height':'70vw', 'margin':'20px', 'margin-left':'17vw', 'font-family':'AppleGothic'}
                    ),
                ),
], className='container')

#callback to get contents of the file with ICD10 CODES
@callback(
        [Output(component_id='panel', component_property='figure', allow_duplicate=True),
        Output(component_id='dropdown-icd-10', component_property='options')],
        Input(component_id='upload-data-distraj', component_property='contents'),
        prevent_initial_call=True
)

def upload_ICD10data_to_panel(contents):
    # print(contents)
    global figure, data_dt, icd10_codes_file, data_lab_res, slider_present,previous_xrange, current_plot_type, constant_x_range, icd10_codes_to_plot, icd10_dropdow_options
    if contents is not None:
        icd10_codes_file=contents
        data=get_array_for_a_bubble_plot(contents)
        dictionary=count_unique_letters_v2(data)
        icd10_dropdow_options=list(dictionary.keys())
        icd10_codes_to_plot=icd10_dropdow_options
        data_dt2=get_data_disease_traj_type2(icd10_codes_file)
        data_dt=get_data_disease_traj_type1(icd10_codes_file)
        if data_lab_res is None:
            xrange=get_plot_range_distraj(icd10_codes_file)
            previous_xrange=xrange
            if current_plot_type==1:
                constant_x_range=xrange
                figure=main_plot_dt2_labpanel(data_dt2, data_lab_res, xrange, test_types, font_size, icd10_codes_to_plot)
            elif current_plot_type==2:
                figure=main_plot(data_dt, data_lab_res, xrange, test_types, font_size, icd10_codes_to_plot)
        elif data_lab_res is not None:
            xrange=get_2plots_range(icd10_codes_file, lab_results_file)
            previous_xrange=xrange
            if current_plot_type==1:
                figure=main_plot_dt2_labpanel(data_dt2, data_lab_res,xrange, test_types, font_size, icd10_codes_to_plot)
            elif current_plot_type==2:
                figure=main_plot(data_dt, data_lab_res, xrange, test_types, font_size, icd10_codes_to_plot)
        return figure, icd10_dropdow_options

#callback to get contents of the file with LAB TESTS and update dropdown menu options
@callback(
        [Output(component_id='panel', component_property='figure', allow_duplicate=True),
        Output(component_id='dropdown-lab-results', component_property='options')],
        Input(component_id='upload-data-labres', component_property='contents'),
        prevent_initial_call=True
)

def upload_LabData_to_panel(contents):
    global data_lab_res,lab_results_file,icd10_codes_file,previous_xrange,slider_present,current_plot_type, data_dt2,constant_x_range, icd10_codes_to_plot
    if contents is not None:
        lab_results_file=contents
        data_lab_res=get_array_for_a_plot_lr(lab_results_file)
        if data_dt is None:
            xrange=get_plot_range_labres(lab_results_file)
            constant_x_range=xrange
            previous_xrange=xrange
            figure=main_plot(data_dt, data_lab_res, xrange, test_types, font_size, icd10_codes_to_plot)
            options=update_dropdown_options(contents)
            return figure,options
        elif data_dt is not None:
            if current_plot_type==1:
                xrange=get_2plots_range(icd10_codes_file, lab_results_file)
                constant_x_range=xrange
                previous_xrange=xrange
                figure=main_plot_dt2_labpanel(data_dt2, data_lab_res, xrange, test_types, font_size, icd10_codes_to_plot)
                options=update_dropdown_options(contents)
            elif current_plot_type==2:
                xrange=get_2plots_range(icd10_codes_file, lab_results_file)
                constant_x_range=xrange
                previous_xrange=xrange
                figure=main_plot(data_dt, data_lab_res, xrange, test_types, font_size, icd10_codes_to_plot)
                options=update_dropdown_options(contents)
            return figure,options

def update_dropdown_options(contents):
    if contents is not None:
        data=get_array_for_a_plot_lr(lab_results_file)
        test_options=get_dropdown_menu(data[:,1])
        return test_options

@callback(
    Output("confirm-filename-dt", "children"),
    Input(component_id='upload-data-distraj', component_property='filename'))

def display_filename(filename):
    if filename is not None:
        print(type(filename[0]))
        chunk_size = 30
        
        text_chunks = split_text(filename[0], chunk_size)  # Split the long text into chunks
        return [html.P(chunk) for chunk in text_chunks]  # Display each chunk on a separate line

    
@callback(
    Output("confirm-filename-labres", "children"),
    Input(component_id='upload-data-labres', component_property='filename'))

def display_filename(filename):
    if filename is not None:
        return filename

# #callback for icd-10 drop down menu
@callback(
    Output(component_id='panel', component_property='figure', allow_duplicate=True),
    Input(component_id='dropdown-icd-10', component_property='value'),
    prevent_initial_call=True
)

def update_icd10panel(icd10_codes):
    global icd10_codes_file, icd10_codes_to_plot
    icd10_codes_to_plot=icd10_codes
    if current_plot_type==1:
        data_dt2=get_data_disease_traj_type2(icd10_codes_file)
        fig=main_plot_dt2_labpanel(data_dt2, data_lab_res, previous_xrange, test_types, font_size, icd10_codes_to_plot)
    elif current_plot_type==2:
        data_dt=get_data_disease_traj_type1(icd10_codes_file)
        fig=main_plot(data_dt, data_lab_res, previous_xrange, test_types, font_size, icd10_codes_to_plot)
    return fig


#callback for lab results dropdown menu and lab panel
@callback(
    Output(component_id='panel', component_property='figure', allow_duplicate=True),
    Input(component_id='dropdown-lab-results', component_property='value'),
    prevent_initial_call=True
)

def update_lab_panel(test_types_to_plot):
    global test_types,current_plot_type, data_dt2, data_dt, data_lab_res, icd10_codes_to_plot
    test_types=test_types_to_plot
    if len(test_types_to_plot)>0:
        if current_plot_type==1:
            data_dt2=get_data_disease_traj_type2(icd10_codes_file)
            fig=main_plot_dt2_labpanel(data_dt2, data_lab_res, previous_xrange, test_types, font_size,icd10_codes_to_plot)
        elif current_plot_type==2:
            data_dt=get_data_disease_traj_type1(icd10_codes_file)
            fig=main_plot(data_dt, data_lab_res, previous_xrange, test_types, font_size, icd10_codes_to_plot)
    elif len(test_types_to_plot)==0:
        if current_plot_type==1:
            data_dt2=get_data_disease_traj_type2(icd10_codes_file)
            fig=main_plot_dt2_labpanel(data_dt2, data_lab_res, previous_xrange, test_types, font_size, icd10_codes_to_plot)
        elif current_plot_type==2:
            data_dt=get_data_disease_traj_type1(icd10_codes_file)
            fig=main_plot(data_dt, data_lab_res, previous_xrange, test_types, font_size, icd10_codes_to_plot)
    return fig

#callback for saving data    
@callback(
    Output("confirm", "children"),
    Input('export-val', 'n_clicks'),
    [State('input-on-submit', 'value'),
     State('panel', 'figure')],
    prevent_initial_call=True
)
def save_data(n_clicks, value, figure):
    global prev_clicks, icd10_codes_file, lab_results_file, previous_xrange, icd10_codes_to_plot
    if prev_clicks!=n_clicks:
        if icd10_codes_file is not None or lab_results_file is not None:
            if current_plot_type==1:
                data_dt2=get_data_disease_traj_type2(icd10_codes_file)
                fig=main_plot_dt2_labpanel(data_dt2, data_lab_res, previous_xrange, test_types, font_size,icd10_codes_to_plot)
                plot_save(fig, value)
            elif current_plot_type==2:
                data_dt=get_data_disease_traj_type1(icd10_codes_file)
                fig=main_plot(data_dt, data_lab_res, previous_xrange, test_types, font_size, icd10_codes_to_plot)
                plot_save(fig, value)
            shared_xrange=previous_xrange
            save_data_dt, save_data_lr=data_for_saving(icd10_codes_file, lab_results_file, shared_xrange, test_types, icd10_codes_to_plot)
            file_=open(value, "w")
            message_to_display="Your data has been successfully exported to the file {0} and to the image of svg format in the folder 'images'!".format(value)
            if save_data_lr is not None and save_data_dt is None:
                file_.write('Date '+'Test type'+'ICD10'+'\n') 
                for line in save_data_lr:
                    file_.write(f'{line}'+'\n')
                message=message_to_display
            elif save_data_dt is not None and save_data_lr is None:
                file_.write('Date '+'ICD10'+'\n') 
                for line in save_data_dt:
                    file_.write(f'{line}'+'\n')
                message=message_to_display
            elif save_data_dt is not None and save_data_lr is not None:
                file_.write('Date '+'ICD10'+'\n') 
                for line in save_data_dt:
                    file_.write(f'{line}'+'\n') 
                file_.write('Date '+'Test_type '+'Test_result'+'\n') 
                for line in save_data_lr:
                    file_.write(f'{line}'+'\n')
                message=message_to_display
            file_.close()
        else:
            message="There is no data to save"
        prev_clicks=n_clicks
        return message
    else:
        return ""

def get_plot_range_callback(relayoutData):
    if relayoutData is not None:
        if "xaxis.range[0]" in relayoutData and 'xaxis.range[1]' in relayoutData:
            x0=relayoutData.get('xaxis.range[0]')
            x1=relayoutData.get('xaxis.range[1]')
            return [x0,x1]
    else:
        return previous_xrange

#selecting plot type call back
@app.callback(
    Output('panel', 'figure'),
    [Input('radio-items', 'value')],
    prevent_initial_call=True
)
def change_plot_type(value):
    global current_plot_type, data_dt2, data_dt, icd10_codes_file, constant_x_range, figure, icd10_codes_to_plot
    if value=='Plot type 1': 
        current_plot_type=1
        if icd10_codes_file is not None:
            data_dt2=get_data_disease_traj_type2(icd10_codes_file)
            figure=main_plot_dt2_labpanel(data_dt2, data_lab_res, constant_x_range, test_types, font_size, icd10_codes_to_plot)
    elif value=='Plot type 2':
        current_plot_type=2
        if icd10_codes_file is not None:
            data_dt=get_data_disease_traj_type1(icd10_codes_file)
            figure=main_plot(data_dt, data_lab_res, constant_x_range, test_types, font_size, icd10_codes_to_plot)
    return figure

#callback to send data range based on which filter values of the plot
@callback(
    Output(component_id='panel', component_property='figure', allow_duplicate=True),
    Input(component_id='panel', component_property='relayoutData'),
    prevent_initial_call=True
)
def get_panel_range(relayoutData):
    global default_min,default_max,range, current_plot_type, previous_xrange, icd10_codes_file, icd10_codes_to_plot
    if relayoutData is not None: 
        # range=previous_xrange
        if 'xaxis.range[0]' in relayoutData:
            xmin = relayoutData['xaxis.range[0]']
            xmax = relayoutData['xaxis.range[1]']
            xmin_lst=xmin.split(" ")
            xmax_lst=xmax.split(" ")
            xmin_date=datetime.strptime(xmin_lst[0], '%Y-%m-%d')
            xmax_date=datetime.strptime(xmax_lst[0], '%Y-%m-%d')
            xrange=[xmin_date,xmax_date]
            previous_xrange=xrange
            if current_plot_type==1:
                data_dt2=get_data_disease_traj_type2(icd10_codes_file)
                return main_plot_dt2_labpanel(data_dt2, data_lab_res, xrange, test_types, font_size, icd10_codes_to_plot)
            elif current_plot_type==2:
                return main_plot(data_dt, data_lab_res, xrange, test_types, font_size, icd10_codes_to_plot)
        if 'xaxis.autorange' in relayoutData:
            if relayoutData['xaxis.autorange']==True:
                previous_xrange=constant_x_range
                if current_plot_type==1:
                    data_dt2=get_data_disease_traj_type2(icd10_codes_file)
                    return main_plot_dt2_labpanel(data_dt2, data_lab_res, constant_x_range, test_types, font_size, icd10_codes_to_plot)
                elif current_plot_type==2:
                    return main_plot(data_dt, data_lab_res, constant_x_range, test_types, font_size, icd10_codes_to_plot)  

#callback for changing font size of the panel
@callback(Output("panel", "figure", allow_duplicate=True), 
          [Input("button-minimise", "n_clicks"),
           Input("button-reset", "n_clicks"),
           Input("button-maximise", "n_clicks")],
           prevent_initial_call=True
)

def update_font_size(but_min, but_res, but_max):
    global prev_but_min, prev_but_max, prev_but_res, data_dt2, data_dt, previous_xrange, test_types, data_lab_res, font_size, marker_size, icd10_codes_to_plot
    if font_size<=2 and marker_size<=18:
        font_size=3
        marker_size=19
        
    if prev_but_min!=but_min:
        font_size-=1
        marker_size-=1
    elif prev_but_res!=but_res:
        font_size=8
        marker_size=25
    elif prev_but_max!=but_max:
        font_size+=1
        marker_size+=2

    if current_plot_type==1:
        data_dt2=get_data_disease_traj_type2(icd10_codes_file)
        figure=main_plot_dt2_labpanel(data_dt2, data_lab_res, previous_xrange, test_types, font_size, icd10_codes_to_plot)
        data=figure['data']
        for trace in data:
            if trace['xaxis'] is None:
                trace['textfont']['size']=font_size
                trace['marker']['size']=marker_size
            else:
                trace['textfont']['size']=font_size
    elif current_plot_type==2:
        data_dt=get_data_disease_traj_type1(icd10_codes_file)
        figure=main_plot(data_dt, data_lab_res, previous_xrange, test_types, font_size, icd10_codes_to_plot)
        data=figure['data']
        for trace in data:
            trace['textfont']['size']=font_size
            # if trace['xaxis'] is None:
            #     trace['textfont']['size']=font_size
            #     trace['marker']['size']=marker_size
            # else:
            #     trace['textfont']['size']=font_size
    prev_but_min=but_min
    prev_but_res=but_res
    prev_but_max=but_max
    return figure

#callback for button to display all codes on the panel 
@callback([Output("panel", "figure", allow_duplicate=True),
           Output("dropdown-icd-10", "value")], 
          Input("display-all", "n_clicks"),
           prevent_initial_call=True
)

def display_all_codes(n_clicks):
    global prev_display_button, icd10_codes_file, figure, icd10_dropdow_options
    if prev_display_button!=n_clicks:
        if current_plot_type==1:
            data_dt2=get_data_disease_traj_type2(icd10_codes_file)
            figure=main_plot_dt2_labpanel(data_dt2, data_lab_res, previous_xrange, test_types, font_size, icd10_dropdow_options)
        elif current_plot_type==2:
            data_dt=get_data_disease_traj_type1(icd10_codes_file)
            figure=main_plot(data_dt, data_lab_res, previous_xrange, test_types, font_size, icd10_codes_to_plot)

    prev_display_button=n_clicks

    return figure, icd10_dropdow_options

def open_browser():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:1222/')   

# Run the Dash app
if __name__ == '__main__':
    # app.run_server(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    Timer(1, open_browser).start()
    app.run_server(debug=False, port=1222)
    
