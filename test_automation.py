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
findError=find_all(Template(r"tpl1730341129190.png", record_pos=(0.386, 0.749), resolution=(1080, 2340)))
print(findError)

