# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 17:02:16 2021

@author: Zhiyun Gong
"""


import pandas as pd
import altair as alt
import streamlit as st

st.title("Hi!")

country_code = pd.read_csv('country_code.csv')

df = pd.read_csv("suicide_population.csv")
year_counts = df.groupby('country')['year'].unique().apply(len)
ten_year_plus_ind = (year_counts > 10).to_list()
ten_yeat_plus_country = df['country'].unique()[ten_year_plus_ind].tolist()
df_filtered = df.loc[df['country'].isin(ten_yeat_plus_country)]


df_filtered = pd.merge(df_filtered,country_code,how='left', left_on='country',right_on='country')


def make_bar_plot_df_multi_country(country_names,var):

    con_df = df_filtered.loc[df_filtered['country'].isin(country_names)]
    counts_df_list = []
    for c in country_names:
        counts = con_df.loc[con_df['country'] ==c].groupby(var)['suicides_no'].sum().to_frame()
        counts = counts.reset_index()
        counts['country'] = c
        counts_df_list.append(counts)
    counts_df = pd.concat(counts_df_list)

    return counts_df

continent_names = ['Europe','Americas']
def make_bar_plot_multi_continent(continent_names, var):
    con_df = df_filtered.loc[df_filtered['region'].isin(continent_names)]
    counts_df_list = []
    for c in continent_names:
        counts = con_df.loc[con_df['region'] ==c].groupby(var)['suicides_no'].sum().to_frame()
        counts = counts.reset_index()
        counts['continent'] = c
        counts_df_list.append(counts)
    counts_df = pd.concat(counts_df_list)
    return counts_df
        

# def make_line_plot_df(country_name):
#     con_df = df.loc[df['country']==country_name]
#     year_counts = con_df.groupby('year')['suicides_no'].sum().to_frame()
#     year_counts = year_counts.reset_index()
#     return year_counts

country_names = st.multiselect('Select countries', ten_yeat_plus_country, default = ['Albania','Argentina','Ukraine','Thailand'])
vis_var = st.selectbox('Do you want to visualize raw or averaged suicide counts',['raw','average'])



# This functions takes 2 arguments: a list of country names; whether to visualize RAW/ AVG suicide number
def make_line_plot_df_multi_country(country_names, mode):
    con_df = df_filtered.loc[df_filtered['country'].isin(country_names)]
    counts_df_list = []
    res_var = 'suicides_no' if mode == 'raw' else 'suicides/100k pop'
    for c in country_names:
          year_counts = con_df.loc[con_df['country'] ==c].groupby('year')[res_var].sum().to_frame()
          year_counts = year_counts.reset_index()
          year_counts['country'] = c
          counts_df_list.append(year_counts)
         
    counts_df = pd.concat(counts_df_list)
    
    return counts_df

def make_line_plot_df_cont_attributes(country_names, continuous_attr):
    con_df = df_filtered.loc[df_filtered['country'].isin(country_names),['country','year',continuous_attr]]
    counts_df_list = []
    for c in country_names:
          year_counts = con_df.loc[con_df['country'] ==c].groupby('year')[continuous_attr].sum().to_frame()
          year_counts = year_counts.reset_index()
          year_counts['country'] = c
          counts_df_list.append(year_counts)
         
    counts_df = pd.concat(counts_df_list)
    return counts_df
    

def make_grouped_bar_plot_df_discrete(country_names, discrete_attr):
    con_df = df_filtered.loc[df_filtered['country'].isin(country_names),['country','year',discrete_attr, 'suicides_no']]
    return con_df

def make_corr_plot_df(country_name):
    con_df = df_filtered.loc[df_filtered['country']==country_name]
    col_names = ['population', 'gdp_per_capita ($)', 'suicides_no', 'suicides/100k pop']
    corr_mtx = con_df[col_names].corr()
    res_list= []
    for r in range(len(corr_mtx.index)):
        for c in range(len(corr_mtx.columns)):
            curr_list = [corr_mtx.index[r], corr_mtx.columns[c], corr_mtx.iloc[r,c]]
            # curr_list.append()
            res_list.append(curr_list)
    res_df = pd.DataFrame(res_list,columns = ['par_A','par_B','correlation'])
    return res_df




## ------------------------------------ Line chart for multiple countries ---------------------
if len(country_names) >=1:
    multi_country_lines = make_line_plot_df_multi_country(country_names,vis_var)
    if vis_var == "raw":
        
        line_plot = alt.Chart(multi_country_lines).mark_line().encode(
        x = 'year',
        y = 'suicides_no',
        color = 'country',
        strokeDash = 'country')
    else:
        line_plot = alt.Chart(multi_country_lines).mark_line().encode(
        x = 'year',
        y = 'suicides/100k pop',
        color = 'country',
        strokeDash = 'country')

    st.altair_chart(line_plot)
else:
    st.write("Please select at least on country to begin")




###------------------------------ Bar plot for multiple countries -----------------------

# country_name = st.selectbox('Select country', ten_yeat_plus_country)
attributes = [ 'sex', 'age', 'generation']
var = st.selectbox('Select attribute', attributes)

multi_bar_df = make_bar_plot_df_multi_country(country_names, var)
multi_bar_chart = alt.Chart(multi_bar_df).mark_bar(opacity =0.3).encode(
    x = var,
    y = 'suicides_no',
    color = 'country')


st.altair_chart(multi_bar_chart)


### --------------------------- Line plot for continuous variables of multiple countries --------
var1 = st.selectbox('Select a continous attribute to visualize', ['population', 'gdp_per_capita ($)'])
ctry_line_plot_df = make_line_plot_df_cont_attributes(country_names, var1)
ctry_line_plot = alt.Chart(ctry_line_plot_df).mark_line().encode(
    x = 'year',
    y = var1,
    color = 'country')

st.altair_chart(ctry_line_plot)

### ---------------------------Bar plot for discrete variables of multiple continents -------- 
ctnt_line_plot_df = make_bar_plot_multi_continent(continent_names,var)
ctnt_line_plot = alt.Chart(ctnt_line_plot_df).mark_bar().encode(
    x = var,
    y = 'suicides_no',
    color = 'continent')

st.altair_chart(ctnt_line_plot)

### -------------------- Correlation heatmap of continous variables for a single country --------
corr_country = st.selectbox('Select country', ten_yeat_plus_country)
corr_plot_df = make_corr_plot_df(corr_country)

corr_plot = alt.Chart(corr_plot_df).mark_rect().encode(
    x = 'par_A',
    y = 'par_B',
    color = 'correlation:Q')

st.altair_chart(corr_plot)


### ------------------- Grouped bar plot of a single discrete variable for multiple countries --------
grouped_bar_df = make_grouped_bar_plot_df_discrete(country_names, 'sex')

slider = alt.binding_range(min =grouped_bar_df['year'].min(), max=grouped_bar_df['year'].max(),step=1)
select_year = alt.selection_single(name = 'year',
                                    fields = ['year'],
                                    bind = slider, init={'year':1997})

# select_year = st.slider('Select year', min_value = int(grouped_bar_df['year'].min()),
#                         max_value = int(grouped_bar_df['year'].max()), value = int(1997), step = 1)

grouped_bar_plot = alt.Chart(grouped_bar_df).mark_bar().encode(
    x = alt.X('country:N'),
    y = alt.Y('suicides_no:Q'),
    color = alt.Color('country:N'),
    column = 'sex'
).add_selection(
    select_year
).transform_filter(
    select_year
)

st.altair_chart(grouped_bar_plot)    

### ----------------------- Pyramid -----------------------------------
# source = data.population()
source = df_filtered[df_filtered['country']==corr_country][['country','year','age','sex','suicides_no']]

base = alt.Chart(source).add_selection(
    select_year
).transform_filter(
    select_year
)

color_scale = alt.Scale(domain=['male', 'female'],
                        range=['#1f77b4', '#e377c2'])
    
left = base.transform_filter(
    alt.datum.sex == 'female'
).encode(
    y=alt.Y('age:O', axis=None),
    x=alt.X('suicides_no:Q',
            title='Suicides count',
            sort=alt.SortOrder('descending')),
    color=alt.Color('sex:N', scale=color_scale, legend=None)
).mark_bar().properties(title='Female')

middle = base.encode(
    y=alt.Y('age:O', axis=None),
    text=alt.Text('age:N'),
).mark_text().properties(width=20)

right = base.transform_filter(
    alt.datum.sex == 'male'
).encode(
    y=alt.Y('age:O', axis=None),
    x=alt.X('suicides_no:Q', 
            title='Suicides count'),
    color=alt.Color('sex:N', scale=color_scale, legend=None)
).mark_bar().properties(title='Male')

pyramid_plot = alt.concat(left, middle, right, spacing=5)
st.altair_chart(pyramid_plot)