import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import base64
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta

global alphabet, letter_abundance_by_date
alphabet=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
alphabet.reverse()
letter_abundance_by_date=[]
global fill_colors
fill_colors=px.colors.qualitative.Dark24
global line_colors
line_colors=px.colors.qualitative.Light24


def get_array_for_a_bubble_plot(file):
    decoded = base64.b64decode(file[0])
    decoded_file=decoded.decode('unicode_escape')
    disease_history_df = pd.read_csv(StringIO(decoded_file), sep='\t', encoding= 'unicode_escape')
    # disease_history_df = pd.read_csv(file, sep='\t', encoding= 'unicode_escape')
    # disease_history_df = pd.read_csv(file,sep='\t',encoding= 'unicode_escape')
    codes_array = np.asarray(disease_history_df['DiagnosisConsolidated icd10 code'])
    date_of_diagnosis_array = np.asarray(disease_history_df['DiagnosisConsolidated earliestDate'])
    #convert string to time
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in date_of_diagnosis_array]
    df_codes_years=np.column_stack((dates, codes_array))
    return df_codes_years

def count_unique_letters_v2(np_date_codes):
    # print('init',np_date_codes)
    letters={}
    for row in np_date_codes:
        # print('row',row ,"end")
        code=row[1]
        if code[0] not in letters:
            letters[code[0]]=1
        else:
            letters[code[0]]+=1
    return letters

def get_letter_count_by_date(data):
    dates={}
    for pair in data:
        date=pair[0]
        if date not in letter_abundance_by_date:
            dates[date]=len(pair[1:])
        else:
            dates[date]=len(pair[1:])
    return dates

def widen_alphabet_ranks(letter_abundance_dict, np_array):
    ranks=list()
    prev_rank=0
    for letter in alphabet:
        if letter in letter_abundance_dict:
            data=extract_by_letters(letter,np_array)
            dict_dates_counts=get_letter_count_by_date(data)
            letter_count=max(dict_dates_counts.values())
            # print(dict_dates_counts,letter, letter_count)
            new_rank=pow(2,letter_count)*700
            new_rank=new_rank+prev_rank
            pair=(letter, prev_rank)
            ranks.append(pair)
            prev_rank=new_rank
    return ranks

def extract_by_letters(letter, np_array):
    items=[]
    prev_date=None
    for row in np_array:
        code=row[1]
        if code[0]==letter:
            items.append(row)
    final_array=[]
    for row in items:
        date=row[0]
        code=[row[1]]
        new_row=[date,code]
        if len(final_array)==0:
            final_array.append(new_row)
        else:
            if date==prev_date:
                last_row=final_array[-1]
                last_row.append(code)
            else:
                final_array.append(new_row)
        prev_date=date
    return final_array

def get_letter_rank(letter, alphabet_rank_lst):
    for i,l in enumerate(alphabet_rank_lst):
        if l[0]==letter:
            rank=l[1]
            index=i
    return rank, index

def append_y_coordinates(np_date_codes):
    # print(np_date_codes)
    prev_date=None
    letter_counts=count_unique_letters_v2(np_date_codes)
    letter_ranks=widen_alphabet_ranks(letter_counts, np_date_codes)
    #extract letters
    array_with_coordinates=[]
    for letter_key in letter_counts:
        prev_date=None
        letter_array=extract_by_letters(letter_key, np_date_codes)
        letter_rank,letter_index=get_letter_rank(letter_key, letter_ranks)
        if letter_index+1<len(letter_ranks):
            next_letter,next_letter_rank=letter_ranks[letter_index+1]
        else:
            next_letter_rank=letter_rank+20
        # next_letter,next_letter_rank=letter_ranks[letter_index+1]
        # print(letter_rank,next_letter_rank)
        sorted(letter_array, key=lambda x: x[0])
        for row in letter_array:
            date=row[0]
            codes=row[1:]
            # print('len of codes: ',codes)
            if prev_date is not None:
                delta=date-prev_date
            else:
                delta=timedelta(days=10000000)
            if len(codes)==1:
                if delta==0:
                    letter_level=letter_rank+((next_letter_rank-letter_rank)+2000)
                    # print('special case')
                elif delta<timedelta(days=150):
                    letter_level=letter_rank+((next_letter_rank-letter_rank)+2000)
                else:
                    letter_level=letter_rank+(next_letter_rank-letter_rank)
                codes.append(letter_level)
                code=codes[0]
                new_row=[date,code[0],codes[1]]
                array_with_coordinates.append(new_row)
            else:
                # print('here')
                if delta<timedelta(days=60):
                    for i,c in enumerate(codes):
                        letter_level=letter_rank+((next_letter_rank-letter_rank)/(len(codes))*(i+1))
                        c.append(letter_level)
                        new_row=[date,c[0],c[1]]
                        array_with_coordinates.append(new_row)
                        # print(row, letter_level,'not here')
                else:
                    for i,c in enumerate(codes):
                        letter_level=letter_rank+((next_letter_rank-letter_rank)/(len(codes))*(i+1))
                        c.append(letter_level)
                        new_row=[date,c[0],c[1]]
                        array_with_coordinates.append(new_row)
                        # print(row, letter_level,'here')
            prev_date=date
            # prev_letter_rank=
    return array_with_coordinates

def extract_data_by_letter_from_np(letter, np_array):
    items=[]
    for row in np_array:
        date=row[0]
        code=row[1]
        level=row[2]
        if code[0]==letter:
            new_row=date,code,level
            items.append(new_row)
    items=np.array(items)
    # print(items)
    return items

def make_grid_lines(fig, array, shared_x_range):
    shift=0
    j=0
    letter_counts=count_unique_letters_v2(array)
    for letter in alphabet:
        j=0
        if letter in letter_counts:
            data=extract_data_by_letter_from_np(letter, array)
            num_cols=len(data)
            while j<=3:
                j+=1
                if j==3:
                    if num_cols==1:
                        fig.add_shape(
                                    dict(type="line", x0=shared_x_range[0]-timedelta(weeks=100), y0=data[0][2]+shift,
                                        x1=shared_x_range[1]+timedelta(weeks=100), y1=data[0][2]+shift, line_width=1,
                                        line_color='grey',opacity=0.25,line=dict(dash='dash',width=1)),layer='below'
                                    )
                    else:
                        
                        fig.add_shape(
                                    dict(type="line", x0=shared_x_range[0]-timedelta(weeks=100), y0=min(data[:,2])+shift,
                                        x1=shared_x_range[1]+timedelta(weeks=100), y1=min(data[:,2])+shift, line_width=1,
                                        line_color='grey',opacity=0.25,line=dict(dash='dash',width=1)),layer='below'
                                    )
                shift+=1000
    
    return fig

def bubble_plot2(fig, array, shared_x_range, font_size):
    fig=make_grid_lines(fig, array, shared_x_range)
    shift=0
    j=0
    custom_tickvals = []  # Example: first and last dates
    custom_ticktext = []  # Custom labels for the tick marks
    letter_counts=count_unique_letters_v2(array)
    for i,letter in enumerate(alphabet):
        j=0
        if letter in letter_counts:
            while j<=3:
                j+=1
                alphabet_index=alphabet.index(letter)
                if alphabet_index==24:
                    fill_color='#BCBD22'
                elif alphabet_index==25:
                    fill_color='#565656'
                else:
                    fill_color=fill_colors[alphabet_index]
                data=extract_data_by_letter_from_np(letter, array)
                num_cols=len(data)
                if num_cols==1:
                    data=data[0]
                    x_s=[data[0]]
                    # print("x",x_s)
                    y_s=[data[2]+ shift]
                    labels=[data[1]]
                elif num_cols>1:
                    # print(data)
                    x_s=data[:,0]
                    y_s=data[:,2]+ shift
                    labels=data[:,1]
                # y_s = [(y+1000) for y in y_s]
                shift+=1000
                # print(i, labels, y_s, shift)
            letter_coordinate=min(y_s)
            custom_tickvals.append(letter_coordinate)
            custom_ticktext.append(letter)
            
            for date,y in zip(x_s,y_s):
                rows_with_the_same_date=extract_data_by_date_from_np(date,array)
                # y_end=max(y_s)#-1000

                line_width=len(rows_with_the_same_date[:,1])
                fig.add_shape(
                        dict(type="line", x0=date, y0=-10,
                            x1=date, y1=y, line_width=line_width,line_color='black'),layer='below'
                        )
            fig.add_trace(go.Scatter(x=x_s, y=y_s, mode='markers', 
                                     hovertemplate = 'Date: %{x|%d-%b-%Y}<br>Code: %{text}<br>', 
                                     hoverinfo='none', name="",
                                     marker=dict(size=25, color=fill_color, opacity=1), text=labels, 
                                     textfont=dict(color='white',size=16), textposition="bottom center", 
                                     showlegend=False))
            fig.add_trace(go.Scatter(x=x_s, y=y_s, mode='text', text=labels, hoverinfo='none',
                                     textfont=dict(color='white', size=font_size, family="Apple Gothic"),
                                     hovertemplate = None, textposition="middle center", 
                                     showlegend=False))


    # Update x-axis layout with custom tick marks and labels

    fig.update_layout(yaxis=dict(tickmode='array',tickvals=custom_tickvals, ticktext=custom_ticktext, tickfont=dict(size=16, family="Apple Gothic",color='black')))
        
    return fig

def extract_data_by_date_from_np(date, np_array):
    items=[]
    for row in np_array:
        date_arr=row[0]
        code=row[1]
        level=row[2]
        if date==date_arr:
            new_row=date,code,level
            items.append(new_row)
    items=np.array(items)
    # print(items)
    return items
    
def main():
    icd10_file='231017_002_ICD10dgncodes_dummy_MN.txt'
    np_date_codes=get_array_for_a_bubble_plot(icd10_file)
    letter_counts=count_unique_letters_v2(np_date_codes)
    letter_ranks=widen_alphabet_ranks(letter_counts, np_date_codes)
    arr1=append_y_coordinates(np_date_codes)
    np_arr1 = np.array(arr1)
    fig=go.Figure()
    x=[2000,2023]
    x_date=pd.to_datetime(x, format="%Y")
    fig=bubble_plot2(fig, np_arr1, x_date)
    fig.update_layout( xaxis=dict(showgrid=False), 
                  yaxis=dict(showgrid=False)
)
    fig.show()


if __name__=="__main__":
    main()