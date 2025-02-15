import pandas as pd
def cut(cost_matrix:pd.DataFrame,province_start:str,province_end:str)->pd.DataFrame:
    """ cut mesh似乎是不必要的，可以直接用cost_matrix在整个中国范围内搜索。时间应该相差不大。
        将中国内陆的网格切割成以两个省份为对角的矩形网格区域,多几格的边(可改)
        东三省与渤海最左端以右,即left>=117.8的省会之间（福建,浙江,江苏,上海)的mesh需要特殊处理,否则会出现网格不连通的情况。
        东三省与新疆之间的mesh同理也需要特殊处理。
        上海：31.3,121.5。121.5-117.8=3.7,3.7/0.2=18.5,即左边界左移18.5个网格,约20个网格,上下右边界不变。
    Args:
    
        cost_matrix (pd.DataFrame): 成本因子网格
        province_start (str): 起点省份
        province_end (str): 终点省份

    Returns:
        pd.DataFrame: 以两个省份为对角的矩形网格区域
    """    
    #取出始末省份省会的经纬坐标
    lon_start=cost_matrix[cost_matrix["capital"]==province_start]["left"].iloc[0]
    la_start=cost_matrix[cost_matrix["capital"]==province_start]["bottom"].iloc[0]
    lon_end=cost_matrix[cost_matrix["capital"]==province_end]["left"].iloc[0]
    la_end=cost_matrix[cost_matrix["capital"]==province_end]["bottom"].iloc[0]
    add_lon=5*0.2 #经度增加5个网格,每个网格0.2度
    add_la=5*0.2   
    min_lon=min(lon_start,lon_end)-add_lon
    min_la=min(la_start,la_end)-add_la
    max_lon=max(lon_start,lon_end)+add_lon
    max_la=max(la_start,la_end)+add_la

    #特殊省份处理
    special_province_1=['Shanghai','Fujian','Zhejiang','Jiangsu']
    special_province_2=['Liaoning','Jilin','Heilongjiang']
    special_province_3=['Xinjiang']
    if ((province_start in special_province_1) and (province_end in special_province_2)) or ((province_start in special_province_2) and (province_end in special_province_1)):
        min_lon=min(lon_start,lon_end)-22*0.2
    if ((province_start in special_province_2) and (province_end in special_province_3)) or ((province_start in special_province_3) and (province_end in special_province_2)):
        min_la=min(la_start,la_end)-15*0.2

    
    #选取矩形范围内的网格
    mymesh=cost_matrix[(cost_matrix["left"]>=min_lon) & (cost_matrix["right"]<=max_lon) & (cost_matrix["bottom"]>=min_la) & (cost_matrix["top"]<=max_la)]   

    mymesh=mymesh[['left','bottom','cost_factor','capital']]  # 重新整理,只保留需要的列
    mymesh.loc[:,'coord']=list(zip((mymesh['left']+0.1).round(1), (mymesh['bottom']+0.1).round(1))) # 增加一列,将网格中心点经纬度合并成一个tuple
    
    return mymesh