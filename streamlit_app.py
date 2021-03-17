# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 22:38:29 2021

@author: Zhiyun Gong
"""


import data_on_map
import gdp_line_map
import comparison
import streamlit as st

PAGES = {
    "Worldwide view": data_on_map,
    "Country-wide Trends on map": gdp_line_map,
    "Interested countries inspection": comparison}

st.sidebar.title('Navigation')
selection = st.sidebar.radio("Show me:", list(PAGES.keys()))
page = PAGES[selection]
page.app()