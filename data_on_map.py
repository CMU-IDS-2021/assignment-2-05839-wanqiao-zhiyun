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
    country_year_arr = df['country-year'].unique()       #np.array
    country = np.vectorize(getCountry)(country_year_arr) #np.array
    year    = np.vectorize(getYear)(country_year_arr)    #np.array
    suicide_rate = suicide_rate_sum.to_numpy()
    df_sum = pd.DataFrame(np.column_stack((country,year,suicide_rate)),\
                          columns=['country','year','suicides/100k'])
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

st.set_page_config(layout="wide")
df1 = loadData(1)
df2 = loadData(2)
df3 = getSumData()
df3.year = df3.year.astype('int64') #Convert data type of years

countries  = alt.topo_feature(data.world_110m.url,'countries')
# Get backgroup world map
background = alt.Chart(countries).mark_geoshape(
    fill="lightgrey",
    stroke="black",
    strokeWidth=0.15)
# Get year count map
fg_year_count = (
    alt.Chart(countries)
    .mark_geoshape(stroke="black", strokeWidth=0.15)
    .encode(
        color=alt.Color("year-count:Q",scale=alt.Scale(scheme="purpleblue")),
        tooltip=[alt.Tooltip("country:N", title="Country"),
                 alt.Tooltip("year-count:Q", title="Data available in years")]
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(df1,"id", ["year-count", "country"]))
)

map_year_count = (
    (background + fg_year_count)
    .configure_view(strokeWidth=0)
    .properties(
        width=1000, height=600,
        title="Data available from each country(in years)")
    .project("naturalEarth1")
)

# Get mean suicides/100k over years map
fg_avg_all = (
    alt.Chart(countries)
    .mark_geoshape(stroke="black", strokeWidth=0.15)
    .encode(
        color=alt.Color("suicides/100k:Q",scale=alt.Scale(scheme="reds")),
        tooltip=[alt.Tooltip("country:N", title="Country"),
                 alt.Tooltip("suicides/100k:Q", title="Average suicides/100k per year")]
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(df2,"id", ["suicides/100k", "country"]))
)

map_avg_all = (
    (background + fg_avg_all)
    .configure_view(strokeWidth=0)
    .properties(
        width=1000, height=600,
        title="Average suicides/100k over years")
    .project("naturalEarth1")
)

# Get mean suicides/100k over years map
slider = alt.binding_range(
    min=int(df3['year'].min()),
    max=int(df3['year'].max()),
    step=1, name='year:')

selector = alt.selection_single(
    name="slider",
    fields=['year'],
    bind=slider, init={'year': 1985})

fg_select_year = alt.Chart(df3).mark_geoshape()\
    .encode(color=alt.Color("suicides/100k:Q",scale=alt.Scale(scheme="reds")),\
            tooltip=[alt.Tooltip("country:N", title="Country"),\
                     alt.Tooltip("suicides/100k:Q", title="Total suicides/100k")])\
    .add_selection(selector)\
    .transform_filter(selector)\
    .transform_lookup(
        lookup='id',
        from_=alt.LookupData(countries, key='id',
                             fields=["type", "properties", "geometry"])
    )

map_select_year = (
    (background + fg_select_year)
    .configure_view(strokeWidth=0)
    .properties(
        width=1000, height=600,
        title="Total suicides/100k each year")
    .project("naturalEarth1")
)


# Get map with year selection function

# st.write(map_year_count,map_avg_all)
def app():
    st.write(map_year_count,map_avg_all,map_select_year)

