import streamlit as st
import pandas as pd

# 计算在线率
def rate_cal(stationdata,date):
    data = stationdata.iloc[:,date]
    count_online = (data == 'online').sum()
    count_error = (data == '1error').sum()+(data == '2error').sum()+(data == '3error').sum()
    count_offline = (data == 'offline').sum()
    error_rate = round(count_error/(count_online+count_error+count_offline)*100,2)
    offline_rate = round(count_offline/(count_online+count_error+count_offline)*100,2)
    online_rate = round(count_online/(count_online+count_error+count_offline)*100,2)
    result=[online_rate,error_rate,offline_rate,count_online,count_error,count_offline]
    return result
# 读取Excel文件
stationdata = pd.read_excel('UATtracking.xlsx')

tempo_list = pd.DataFrame(index=None,columns=['Name', 'ErrorRate','OfflineRate'])
date_list= pd.DataFrame(index=None,columns=['OnlineRate','ErrorRate','OfflineRate'])
# 计算场站故障率和离线率
stationcount=0
for stationcount in range(stationdata.shape[0]):
    singlestationdata = stationdata.iloc[stationcount]
    station_name =singlestationdata[0]
    station_week =singlestationdata[-5:]
    online_sum = (station_week == 'online').sum()
    error_sum = (station_week == '1error').sum()+(station_week == '2error').sum()+(station_week == '3error').sum()
    offline_sum = (station_week == 'offline').sum()
    if online_sum+error_sum+offline_sum==0:
        continue
    else:
        error_rate = round(error_sum/(online_sum+error_sum+offline_sum)*100,2)
        offline_rate = round(offline_sum/(online_sum+error_sum+offline_sum)*100,2)
        tempo_list.loc[stationcount] = [station_name,error_rate,offline_rate]
        stationcount+=1
# 计算测试整体故障率和离线率
rate_today=rate_cal(stationdata,-1)
rate_yesterday=rate_cal(stationdata,-5)
trend=[round(rate_today[0]-rate_yesterday[0],2),round(rate_today[1]-rate_yesterday[1],2),round(rate_today[2]-rate_yesterday[2],2)]

#计算总桩量
def pile_cal(col):
    pilecount=0
    pilesum=0
    for pilecount in range(stationdata.shape[0]):
        pilesum+=stationdata.iloc[pilecount,col]
        pilecount+=1
    return pilesum
pile_actual=pile_cal(2)
pile_app=pile_cal(3)

def pilestatus_cal(date_col):
    pilecount=0
    onlinepilesum=0
    errorpilesum=0
    offlinepilesum=0
    for pilecount in range(stationdata.shape[0]):
        if stationdata.iloc[pilecount,date_col]=='online':
            onlinepilesum+=stationdata.iloc[pilecount,3]
        elif stationdata.iloc[pilecount,date_col]=='offline':
            offlinepilesum+=stationdata.iloc[pilecount,3]
        elif stationdata.iloc[pilecount,date_col]=='1error':
            errorpilesum+=1
            onlinepilesum+=(stationdata.iloc[pilecount,3]-1)
        elif stationdata.iloc[pilecount,date_col]=='2error':
            errorpilesum+=2
            onlinepilesum+=(stationdata.iloc[pilecount,3]-2)
        elif stationdata.iloc[pilecount,date_col]=='3error':
            errorpilesum+=3
            onlinepilesum+=(stationdata.iloc[pilecount,3]-3)
        else:
            print('Something wrong happens at row '+str(pilecount))
    return [onlinepilesum,errorpilesum,offlinepilesum]

def pilerate_cal(count_online,count_error,count_offline):
    error_rate = round(count_error/(count_online+count_error+count_offline)*100,2)
    offline_rate = round(count_offline/(count_online+count_error+count_offline)*100,2)
    online_rate = round(count_online/(count_online+count_error+count_offline)*100,2)
    result=[online_rate,error_rate,offline_rate]
    return result
#设置表格颜色
def set_color(status):
    if status == 'offline':
        return 'color: gray'
    if status == 'online':
        return 'color: green'
    if status == '1error' or status=='2error':
        return 'color: red'

todayspilestatus=pilestatus_cal(-1)
yesterdaypilestatus=pilestatus_cal(-5)
datecount=0
for datecount in range(5):
    singledaydata = stationdata.iloc[:,-1-datecount]
    date_name =singledaydata.name
    pilestatus=pilestatus_cal(-1-datecount)
    pilerate=pilerate_cal(pilestatus[0],pilestatus[1],pilestatus[2])
    date_list.loc[date_name] = [round(pilerate[0]/100,2),round(pilerate[1]/100,2),round(pilerate[2]/100,2)]
pilerate_today=pilerate_cal(todayspilestatus[0],todayspilestatus[1],todayspilestatus[2])
pilerate_yesterday=pilerate_cal(yesterdaypilestatus[0],yesterdaypilestatus[1],yesterdaypilestatus[2])
piletrend=[round(pilerate_today[0]-pilerate_yesterday[0],1),round(pilerate_today[1]-pilerate_yesterday[1],1),round(pilerate_today[2]-pilerate_yesterday[2],1)]

#筛选出近期故障的场站，以及场站最后7次的状态
new_stationdata = stationdata.set_index('Name')
todaydata = new_stationdata.iloc[:,-1]
error_dataframe=pd.DataFrame()
for index, value in todaydata.items():
    if value=='1error'or value=='2error'or value=='3error':
        errorstation_week= new_stationdata.loc[index].tail(5)
        errorstationchart=pd.Series(errorstation_week)
        error_dataframe=pd.concat([error_dataframe,errorstationchart],axis=1)
error_frame=pd.DataFrame(error_dataframe).transpose()

offline_dataframe=pd.DataFrame()
for index, value in todaydata.items():
    if value=='offline':
        offlinestation_week= new_stationdata.loc[index].tail(5)
        offlinestationchart=pd.Series(offlinestation_week)
        offline_dataframe=pd.concat([offline_dataframe,offlinestationchart],axis=1)
offline_frame=pd.DataFrame(offline_dataframe).transpose()

# streamlit图标构建
st.title(f'2024{stationdata.iloc[:,-1].name} Charging Station Status —— Customer Side')
# 展示一级标题
st.header('1. Overall')
st.subheader('Stations status')
col1, col2, col3, col4 = st.columns(4)
col1.metric("Number of stations", f'{stationdata.shape[0]}')
col2.metric("Number of online stations", f'{rate_today[3]}',delta_color="inverse")
col3.metric("Number of failure stations", f'{rate_today[4]}',delta_color="inverse")
col4.metric("Number of offline stations", f'{rate_today[5]}',delta_color="inverse")
col1, col2, col3 = st.columns(3)
col1.metric("Online rates", f'{rate_today[0]}%', f"{trend[0]}%",delta_color="inverse")
col2.metric("Failure rates", f'{rate_today[1]}%', f"{trend[1]}%",delta_color="inverse")
col3.metric("Offline rates", f'{rate_today[2]}%', f"{trend[2]}%",delta_color="inverse")
st.caption('(All percentage changes are with respect to the data collected last week)')
st.subheader('Plies status')
col1, col2, col3, col4 = st.columns(4)
col1.metric("Number of piles", f'{pile_app}')
col2.metric("Number of online piles", f'{todayspilestatus[0]}')
col3.metric("Number of failure piles", f'{todayspilestatus[1]}')
col4.metric("Number of offline piles", f'{todayspilestatus[2]}')
col1, col2, col3 = st.columns(3)
col1.metric("Online rates", f'{pilerate_today[0]}%', f"{piletrend[0]}%",delta_color="inverse")
col2.metric("Failure rates", f'{pilerate_today[1]}%', f"{piletrend[1]}%",delta_color="inverse")
col3.metric("Offline rates", f'{pilerate_today[2]}%', f"{piletrend[2]}%",delta_color="inverse")
st.caption('(All percentage changes are with respect to the data collected last week)')
st.subheader('\nCharging Piles Online/Failure/Offline rate trend')
chart_data = pd.DataFrame(date_list)
st.line_chart(chart_data)

# # 展示一级标题
# st.header('2. Site to watch')

# # 展示二级标题
# st.subheader('2.1 Stations with the highest failure rates：')

# # 纯文本
# rank_list=[-1,-2,-3]
# rank_list2={}
# for i in rank_list:
#     if new_stationdata.loc[tempo_list_error_rank.iloc[i,0]].tail(1)[0] == 'online':
#         rank_list2[abs(i)]=':green[online]'
#     elif new_stationdata.loc[tempo_list_error_rank.iloc[i,0]].tail(1)[0] == '1error':
#         rank_list2[abs(i)]=':red[failure(1/2)]'
#     elif new_stationdata.loc[tempo_list_error_rank.iloc[i,0]].tail(1)[0] == '2error':
#         rank_list2[abs(i)]=':red[failure(0/2)]'
#     elif new_stationdata.loc[tempo_list_error_rank.iloc[i,0]].tail(1)[0] == 'offline':
#         rank_list2[abs(i)]=':red[offline]'
#     else:
#         rank_list2[abs(i)]='error'

# st.markdown(f'1. Name: {tempo_list_error_rank.iloc[-1,0]}，')
# st.markdown(f'failure rates last month：{tempo_list_error_rank.iloc[-1,1]}%，status now：{rank_list2[1]}')
# st.markdown(f'2. Name: {tempo_list_error_rank.iloc[-2,0]}，')
# st.markdown(f'failure rates last month：{tempo_list_error_rank.iloc[-2,1]}%，status now：{rank_list2[2]}')
# st.markdown(f'3. Name: {tempo_list_error_rank.iloc[-3,0]}，')
# st.markdown(f'failure rates last month：{tempo_list_error_rank.iloc[-3,1]}%，status now：{rank_list2[3]}')
# # 展示二级标题
# st.subheader('2.2 Stations with the highest offline rates：')

# # 纯文本
# rank_list=[-1,-2,-3]
# rank_list2={}
# for i in rank_list:
#     if new_stationdata.loc[tempo_list_offline_rank.iloc[i,0]].tail(1)[0] == 'online':
#         rank_list2[abs(i)]=':green[online]'
#     elif new_stationdata.loc[tempo_list_offline_rank.iloc[i,0]].tail(1)[0] == '1error':
#         rank_list2[abs(i)]=':red[failure(1/2)]'    
#     elif new_stationdata.loc[tempo_list_offline_rank.iloc[i,0]].tail(1)[0] == '2error':
#         rank_list2[abs(i)]=':red[failure(0/2)]'
#     elif new_stationdata.loc[tempo_list_offline_rank.iloc[i,0]].tail(1)[0] == 'offline':
#         rank_list2[abs(i)]=':red[offline]'
#     else:
#         rank_list2[abs(i)]='error'

# st.markdown(f'1. Name: {tempo_list_offline_rank.iloc[-1,0]}，')
# st.markdown(f'offline rates last month：{tempo_list_offline_rank.iloc[-1,2]}%，status now：{rank_list2[1]}')
# st.markdown(f'2. Name: {tempo_list_offline_rank.iloc[-2,0]}，')
# st.markdown(f'offline rates last month：{tempo_list_offline_rank.iloc[-2,2]}%，status now：{rank_list2[2]}')
# st.markdown(f'3. Name: {tempo_list_offline_rank.iloc[-3,0]}，')
# st.markdown(f'offline rates last month：{tempo_list_offline_rank.iloc[-3,2]}%，status now：{rank_list2[3]}')
# 展示一级标题
st.header('2. List of all the non-online stations today')
st.subheader('2.1 List of the failure stations：')
row_errorframe=error_frame.shape[0]
st.dataframe(error_frame.style.applymap(set_color),width=2000,height=int(row_errorframe)*37)

st.subheader('2.2 List of the offline stations：')
row_offlineframe=offline_frame.shape[0]
st.dataframe(offline_frame.style.applymap(set_color),width=2000,height=int(row_offlineframe)*37)