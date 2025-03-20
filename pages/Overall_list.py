import streamlit as st
import pandas as pd
st.header('All stations status history')
stationdata = pd.read_excel('UATtracking.xlsx')
new_stationdata = stationdata.set_index('Name')
new_stationdata.replace('online','√',inplace=True)
new_stationdata.replace('error','×(error)',inplace=True)
new_stationdata.replace('offline','×(offline)',inplace=True)
st.dataframe(new_stationdata,use_container_width=True)
