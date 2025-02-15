import os
import pandas as pd
import geopandas as gpd
from src.const import PHpipe_buildcost_Inner_Beijing
def import_data():
    #变
    hydrogen_demand = pd.read_csv("data/consumption_potential/hydrogen_demand.csv", index_col=0) / 1e7  
    electricity_price = pd.read_csv('data/production_potential/electricity_price.csv', index_col=0)
    #不变
    production_upper = pd.read_csv("data/production_potential/production_upper.csv", index_col=0) / 1e7
    NGtable = pd.read_csv("data/existing_pipelines/NGtable.csv", index_col=0) / 1e7
    PHtable = pd.read_csv("data/existing_pipelines/PHtable.csv", index_col=0) / 1e7
    minimal_cost_matrix = pd.read_csv("data/optimal_paths/minimal_cost_matrix_3.csv", index_col=0)
    paths_length = pd.read_csv("data/optimal_paths/paths_length_3.csv", index_col=0)
    df_paths = pd.read_json("data/optimal_paths/df_paths_3.json")
    gdf_cross = gpd.read_file('data/existing_pipelines/gpf_cross_new.geojson', index_col=0)
    gdf_cross['capacity_h2'] = gdf_cross['capacity_h2'] / 1e7


    
    PHpipe_buildcost = minimal_cost_matrix / minimal_cost_matrix.loc['Inner Mongolia', 'Beijing'] *PHpipe_buildcost_Inner_Beijing

    return hydrogen_demand, production_upper, NGtable, PHtable, minimal_cost_matrix, paths_length, df_paths, gdf_cross, electricity_price, PHpipe_buildcost

# 检查目标文件夹是否存在，如果不存在，则创建它
def save_results(filename,df_G,new_paths_dict,paths_100_dict,paths_20_dict):
    folder_path = "data/dispatch/" + filename
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 保存文件到目标文件夹
    df_G.to_csv(folder_path + f'/{filename}_G.csv')
        
    try:
        new_paths_dict=gpd.GeoDataFrame(new_paths_dict).set_geometry('geometry')
        new_paths_dict['color_capacity']=20+(new_paths_dict['capacity'] - new_paths_dict['capacity'].min()) * (100 - 20) / (new_paths_dict['capacity'].max() - new_paths_dict['capacity'].min())
        new_paths_dict.to_file(folder_path+f'/{filename}'+"_PH.geojson", driver='GeoJSON')
    except Exception as e:
        print(e)
    try:    
        paths_100_dict=gpd.GeoDataFrame(paths_100_dict).set_geometry('geometry')
        paths_100_dict['color_capacity']=20+(paths_100_dict['capacity'] - paths_100_dict['capacity'].min()) * (100 - 20) / (paths_100_dict['capacity'].max() - paths_100_dict['capacity'].min())
        paths_100_dict.to_file(folder_path+f'/{filename}'+"_100.geojson", driver='GeoJSON')
    except Exception as e:
        print(e)
    try:
        paths_20_dict=gpd.GeoDataFrame(paths_20_dict).set_geometry('geometry')
        paths_20_dict['color_capacity']=20+(paths_20_dict['capacity'] - paths_20_dict['capacity'].min()) * (100 - 20) / (paths_20_dict['capacity'].max() - paths_20_dict['capacity'].min())
        paths_20_dict.to_file(folder_path+f'/{filename}'+"_20.geojson", driver='GeoJSON')
    except Exception as e:
        print(e)