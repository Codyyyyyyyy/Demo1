import os
# -*- encoding=utf8 -*-
#运行前请连接至安卓手机，开启调试，保证手机WIFI连通，PID账号登录后，将app放置在能看到车辆信息的主页面，测试版本My Porsche App V4.5.2
__author__ = "Cody Chen"
from airtest.core.api import *
from airtest.aircv import *
auto_setup(__file__)
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
import pandas as pd
import numpy as np
#打开EXCEL数据表并创建临时列表储存本次运行的场站结果
excel_file = 'UATtracking.xlsx'
excel_file_list_version=pd.read_excel('UATtracking.xlsx')
temporary_list=[]
pillar_count=[]
#读取场站名称txt，并将其转换成列表
# file_path1 = 'StationName.txt'
# with open(file_path1, 'r',encoding="utf-8") as file:
#     lines = file.readlines()
stationName = excel_file_list_version.iloc[:, 0].tolist()
#创建offline场站txt，并记录当前时间
file_path2 = f'D:/test/{time.strftime("%Y%m%d")}OfflineStation.txt'
with open(file_path2, 'a',encoding="utf-8") as file:
    file.write('offline station name:' + '\n')
#创建error场站txt，并记录当前时间
file_path3 = f'D:/test/{time.strftime("%Y%m%d")}ErrorStation.txt'
with open(file_path3, 'a',encoding="utf-8") as file:
    file.write('error station name:' + '\n')
#从主页面为入口，将筛选条件设为仅搜索保时捷尊享，并进入搜索框
poco("android.widget.LinearLayout").offspring("cn.porsche.app:id/bottom_navigation").offspring("cn.porsche.app:id/connect_home_nav_graph").offspring("cn.porsche.app:id/navigation_bar_item_icon_view").click()
poco(text="找充电站").click()
touch(Template(r"tpl1728378914342.png", record_pos=(0.404, -0.091), resolution=(1080, 2340)))
poco(text="重置全部").click()
poco(text="保时捷尊享").click()
poco(text="确认筛选").click()
# poco("cn.porsche.app:id/map_places_search_button").click()
poco(text="搜索目的地").click()
#使搜索框仅搜索充电站
text('1')
start_time=time.time()
while time.time()-start_time<10:
    if poco(textMatches=".*充电站.*"):
        break
    time.sleep(0.5)
poco(text="充电站").click()
poco("Search Field Trailing Icon").click()
#通过循环语句挨个查找每个场站的状态
for everyStation in stationName: 
    text(everyStation)
    #通过循环语句等待场站元素出现
    start_time=time.time()
    while time.time()-start_time<30:
        if poco(textMatches=".*直流空闲.*"):
            break
        time.sleep(0.5)
    #利用poco找出搜索栏里相应场站的桩在线信息
    nameForPocoSearch=".*"+everyStation+".*"
    if poco(nameMatches='.*android.widget.TextView.*',textMatches=nameForPocoSearch):
        elements = poco(nameMatches='.*android.widget.TextView.*',textMatches=nameForPocoSearch)
        elements_parent=elements.parent()
        print(elements_parent.get_position(),elements_parent.get_name())
        siblings=elements.sibling()
        text_list=[]
        for i in siblings:
            text_list.append(i.get_text())
        # print(text_list)
        result = [text for text in text_list if text is not None and '直流空闲' in text]
        if result!=[]:
            stationStatus=result.pop()[-3:]
        else:
            stationStatus='error'
        #根据结果做出相应的对策
        if stationStatus=='2/2':
            temporary_list.append('online')
            pillar_count.append('2')
        elif stationStatus=='1/1':
            temporary_list.append('online')
            pillar_count.append('1')
        elif stationStatus=='3/3':
            temporary_list.append('online')
            pillar_count.append('3')
        else:
            if stationStatus=='0/3' or stationStatus=='2/3' or stationStatus=='1/3':
                    pillar_count.append('3')
            elif stationStatus=='0/1':
                    pillar_count.append('1')
            elif stationStatus=='0/2'or stationStatus=='1/2':
                    pillar_count.append('2')
            else:
                    pillar_count.append('error')
            elements_parent.click()
            touch(Template(r"tpl1736227346436.png", record_pos=(0.377, 0.581), resolution=(1080, 2340)))
            touch(Template(r"tpl1736227793590.png", record_pos=(0.417, 0.04), resolution=(1080, 2340)))

            if exists(Template(r"tpl1730341129190.png", record_pos=(0.386, 0.749), resolution=(1080, 2340))):
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                snapshot_path = os.path.join("D:\\","test","ErrorStationDetail",f"screenshot_{timestamp}.png")
                snapshot(snapshot_path)
                with open(file_path3, 'a',encoding="utf-8") as file:
                    file.write(everyStation + '\n')
                findError=find_all(Template(r"tpl1730341129190.png", record_pos=(0.386, 0.749), resolution=(1080, 2340)))
                if findError is not None:
                    count = len(findError)
                    temporary_list.append(f'{count}error')
                else:
                    temporary_list.append('online')
            else:
                temporary_list.append('online')
            touch(Template(r"tpl1714357475610.png", record_pos=(0.408, -0.371), resolution=(1080, 2340)))
            touch(Template(r"tpl1729238251407.png", record_pos=(-0.427, -0.944), resolution=(1080, 2340)))
            touch(Template(r"tpl1714357511065.png", record_pos=(-0.41, -0.93), resolution=(1080, 2340)))
        #若查找不到场站，则将该场站名记录至OfflineStation.txt内
    else:
        with open(file_path2, 'a',encoding="utf-8") as file:
            file.write(everyStation + '\n')
        temporary_list.append('offline')
        pillar_count.append(np.nan)
    poco("Search Field Trailing Icon").click()
# 将列表作为新的DataFrame列添加
df = pd.read_excel(excel_file)
df[time.strftime("%m%d")] = temporary_list
# 对非空值进行覆写
null_indices = [i for i, x in enumerate(pillar_count) if pd.isnull(x)]
for i, value in enumerate(pillar_count):
    if i not in null_indices:
        df.loc[i, 'app桩数'] = value
# df['场站桩数']=pillar_count
# 将更新后的DataFrame写回Excel文件
df.to_excel(excel_file, index=False)