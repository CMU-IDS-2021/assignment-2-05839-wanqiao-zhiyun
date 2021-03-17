import re
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from vega_datasets import data

df = pd.read_csv('suicide_population.csv')

def getCountry(s):
    # Get country name from country-year string
    country = ""
    return country.join(re.findall(r"\D",s))

def getYear(s):
    # Get year from country-year string
    year = ""
    return year.join(re.findall(r"\d",s))

def getSumData():
    df = pd.read_csv('suicide_population.csv')
    # Get suicide rate(suicides/100k pop) sum by adding up suicide rate
    # from all categories(age group, gender).
    country_code = pd.read_csv('country_code.csv')
    suicide_rate_sum = df.groupby('country-year')['suicides/100k'].sum()
    GDP = df.groupby('country-year')['gdp_per_capita'].mean().to_numpy()
    HDI = df.groupby('country-year')['HDI'].mean().to_numpy()
    country_year_arr = df['country-year'].unique()       #np.array
    country = np.vectorize(getCountry)(country_year_arr) #np.array
    year    = np.vectorize(getYear)(country_year_arr)    #np.array
    suicide_rate = suicide_rate_sum.to_numpy()
    df_sum = pd.DataFrame(np.column_stack((country,year,suicide_rate,GDP,HDI)),\
                          columns=['country','year','suicides/100k',
                                   'GDP_per_capita','HDI'])
    merged = pd.merge(df_sum,country_code,how='left',\
                      left_on='country',right_on='country')
    # Returned dataframe each row has suicide rate sum in one country, one year
    return merged

def loadData(idx):
    raw_data = pd.read_csv('suicide_population.csv')
    country_code = pd.read_csv('country_code.csv')
    df = pd.merge(raw_data,country_code,how='left',\
                  left_on='country',right_on='country')
    if idx == 1:
        # Get the first DataFrame for visualization
        # The visual is a world map with each country color coded by how many
        # years we have for the dataset.
        year_count   = df.groupby('country')['year'].unique().apply(len)
        country_year_cnt = pd.DataFrame([year_count.index.tolist(),year_count.tolist()])
        country_year_cnt = country_year_cnt.transpose()
        country_year_cnt.columns = ['country','year-count']
        df_out = pd.merge(country_year_cnt,country_code,how='left',\
                          left_on='country',right_on='country')
    if idx == 2:
        #year_mean = df.groupby('country')['year'].unique().apply
        df = getSumData()
        year_mean = raw_data.groupby(['country'])['suicides/100k'].mean()
        year_mean_df = pd.DataFrame([year_mean.index.tolist(),year_mean.tolist()]).transpose()
        year_mean_df.columns = ['country','suicides/100k']
        df_out = pd.merge(year_mean_df,country_code,how='left',\
                          left_on='country',right_on='country')
    return df_out


def selectByYear(df,year_str):
    # Select rows from one year
    return df.loc[df['year']==year_str]

def selectByKey(df_all,key,groups):
    # Select rows from certain groups(age group, gender) by
    # given key(country, year)
    return df_all.loc[df_all[key].isin(groups)]

country_list = df['country'].unique()
df_selected  = selectByKey(df,'year',['2000'])

# st.set_page_config(layout="wide")
df2 = loadData(2)
df_sum = getSumData()

# Get backgroup world map background
countries  = alt.topo_feature(data.world_110m.url,'countries')
select_country = alt.selection_single(fields=['country'])

background = alt.Chart(countries).mark_geoshape(
    fill="lightgrey",
    stroke="black",
    strokeWidth=0.15)

# Get mean suicides/100k over years choropleth map
choropleth = (
    alt.Chart(countries)
    .mark_geoshape(stroke="black", strokeWidth=0.15)
    .encode(
        color=alt.Color("suicides/100k:Q"),
        opacity=alt.condition(select_country, alt.value(1), alt.value(0.2)),
        tooltip=[alt.Tooltip("country:N", title="Country"),
                 alt.Tooltip("suicides/100k:Q", title="Average suicides/100k")]
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(df2,"id", ["suicides/100k", "country"])
    ).properties(width=1000,height=500).project("naturalEarth1").add_selection(select_country)
)

map=background+choropleth

line_base = alt.Chart(df_sum).encode(
    alt.X('year:O', axis=alt.Axis(title=None))
).properties(width=400,height=100)

gdp_line = line_base.mark_line(stroke='#f5c542',interpolate='monotone').encode(
        alt.Y(
            'GDP_per_capita:Q',
            axis=alt.Axis(title='GDP_per_capita', titleColor='#f5c542'))
    ).transform_filter(select_country)

suicide_line = line_base.mark_line(stroke='#ff1717',interpolate='monotone').encode(
        alt.Y(
            'suicides/100k:Q',
            axis=alt.Axis(title='suicides/100k', titleColor='#ff1717'))
    ).transform_filter(select_country)

line_fg = alt.layer(gdp_line,suicide_line).resolve_scale(
    y = 'independent'
)

def app():
    st.write(map+line_fg)

