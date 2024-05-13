import plotly.graph_objects as go
import numpy as np
import math
from datetime import datetime
from disease_trajectory import *

global prev_date, prev_level_count0, prev_level_count1,prev_date_count0, prev_date_count1

prev_level_count1=-1
prev_level_count0=-1
prev_date_count0=datetime(1900,1,1)
prev_date_count1=datetime(1900,1,1)

def get_array_for_a_plot_type1_v2(file):
    decoded = base64.b64decode(file[0])
    decoded_file=decoded.decode('unicode_escape')
    disease_history_df = pd.read_csv(StringIO(decoded_file), sep='\t', encoding= 'unicode_escape')
    # disease_history_df = pd.read_csv(file, sep='\t', encoding= 'unicode_escape')
    # disease_history_df = pd.read_csv(file,sep='\t',encoding= 'unicode_escape')
    codes_array = np.asarray(disease_history_df['DiagnosisConsolidated icd10 code'])
    date_of_diagnosis_array = np.asarray(disease_history_df['DiagnosisConsolidated earliestDate'])
    dates=date_of_diagnosis_array
    df_codes_years=np.column_stack((dates, codes_array))
    return df_codes_years

def group_year_codes(df_codes_years):
    grouped_codes_years={}
    for date, code in df_codes_years:
        if date in grouped_codes_years:
            grouped_codes_years[date].append(code)
        else:
            value=[]
            grouped_codes_years.setdefault(date, value)
            grouped_codes_years[date].append(code)
    return grouped_codes_years

def dict_to_numpy_type1_v2(dictionary):
    keys = list(dictionary.keys())
    values = list(dictionary.values())
    array_from_dict = np.array(list(zip(keys, values)), dtype=[('key', 'U10'), ('value', object)])
    # print(array_from_dict)
    return array_from_dict

def change_labels(labels_given):
    labels=[]
    for code in labels_given:
        if len(code)==1 or len(code)==2:
            label="<br>".join(code)
        elif len(code)==3:
            label=" ".join(code[:1])
            label=label+"<br>"+code[2]
        else:
            i=0
            text=[]
            for c in code:
                if i>=2:
                    text.append("<br>")
                    text.append(c)
                    i=0
                else:
                    text.append(c)
                    i+=1
            label=" ".join(text)
        labels.append(label)
    return labels

def distribute_positive_labels(dates,levels):
    # print(dates, levels)
    indeces=[]
    prev_date=None
    for i,level in enumerate(levels):
        if level>0:
            indeces.append(i)
    for ind in indeces:
        date=dates[ind]
        date=datetime.strptime(date, "%Y-%m-%d") 
        if prev_date is not None:
            delta=date-prev_date
            if delta<timedelta(weeks=20):
                new_level=levels[ind]-3
                levels[ind]=new_level
        prev_date=date
    return levels

def substitue_levels(indeces, levels):
    mult=-1
    shift=0
    for el in indeces:
        if shift>4:
            shift=0
        level=levels[el]
        new_level=((level+shift)*mult)
        if new_level<0:
            levels[el]=new_level-5
        else:
            levels[el]=new_level
        mult=mult*-1
        shift+=4
    return levels

#get indeces of labels of specific count
def extract_indeces(data, count_check):
    ind=0
    indeces_count=[]
    for label in data:
        count=label.count("<br>")
        index=ind
        if count==count_check:
            indeces_count.append(index)
        ind+=1
    return indeces_count

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

def disease_trajectory_type1(fig, path_of_the_file, shared_x_range, font_size, letters):
    global prev_date, prev_level_count1, prev_level_count0, prev_date_count0, prev_date_count1
    np_date_codes=extract_data_by_letters(path_of_the_file,letters)
    np_date_codes=group_year_codes(np_date_codes)
    dates=[]
    codes=[]
    for pair in np_date_codes:
        dates.append(pair)
        codes.append(np_date_codes[pair])
    labels=[]
    for code in codes:
        if len(code)==1:
            label="<br>".join(code)
        elif len(code)>1:
            label=" ".join(code)
            lst=[c for c in code]
            label=label="<br>".join(lst)
        labels.append(label)
    levels=[]
    i=0
    j=0
    for label in labels:
        count=label.count("<br>")
        if count==0:
            if j==0:
                level=10.5
            else:
                level=16/j+1
        elif count>=0:
            level=((count+4)*2)+5
        if j>5:
            j=0
        else:
            j+=2
        levels.append(level)
    levels=distribute_positive_labels(dates,levels)
    max_count=0
    for label in labels:
        count=label.count("<br>")
        if count>max_count:
            max_count=count
    for num in range(max_count):
        indeces_count=extract_indeces(labels, num)
        levels=substitue_levels(indeces_count, levels)
    # print(codes)
    #create y locations for diamonds
    diamonds_y_values=np.zeros(len(dates))
    #add diamond shapes
    fig.add_trace(go.Scatter(x=dates, y=diamonds_y_values, mode='markers', name="",
                            marker=dict(size=15, color="Red", symbol=23,line=dict(width=2, color="Black"), 
                            opacity=1), 
                            showlegend=False, text=codes, hoverinfo ='none',
                            # hovertemplate = 'Date: %{x|%B %d, %Y}<br>%{text}'
                            hovertemplate = None))
    #draw vertical lines
    for date, level, code in zip(dates, levels, labels):
        fig.add_shape(type="line",
        x0=date, y0=0, x1=date, y1=level,
        line=dict(color="Red",width=2))   
        if i==len(levels):
            i+=0
        else:
            i+=1
    #plot disease codes over vertical lines
    # Add a scatter plot trace with adjusted y values
    labels=change_labels(codes)
    iter=0
    for level,label in zip(levels,labels):
        if level<0:
            levels[iter]=level-(get_label_height(label, 12)/3)
        iter+=1
    fig.add_trace(go.Scatter(x=dates, y=levels, text=labels,textfont=dict(size=font_size), 
                             textposition="top center", mode="text", name="", showlegend=False,
                             hovertemplate = 'Date: %{x|%B %d, %Y}<br>%{text}'))
    fig.update_layout(plot_bgcolor = "white",
                    font = dict(family='"Times New Roman"', color = "black"),
                    # title = dict(text = title, font = dict(size = 26)),
                    xaxis = dict(anchor="free",  linecolor = "black", range=shared_x_range, titlefont=dict(size=14)),
                    xaxis_tickformat = '%Y',
                    yaxis = dict(range=[-40,40],showticklabels=False, showline=False, zeroline=True, zerolinecolor='black', zerolinewidth=2)
                    )
    
    return fig
    
# Function to calculate label height
def get_label_height(text, font_size):
    i=1
    b=2
    if len(text)>10 and len(text)<=20:
        i=0.8
        b=5
        # print(text, len(text))
    elif len(text)>20 and len(text)<=30:
        i=1/2
        b=6
    elif len(text)>30:
        b=9
        i=1/4
    return len(text)*i * 0.1 * (font_size)+b


if __name__=="__main__":
    # Incorporate data
    path_of_the_file="231017_002_ICD10dgncodes_dummy_MN.txt"
    #path_of_the_file=input("enter file path: ")
    x=[2000, 2023]
    xx=pd.to_datetime(x, format='%Y')
    print(xx)
    fig=go.Figure()
    fig=disease_trajectory_type1(fig,path_of_the_file,xx,12)
    fig.show()
   
