import numpy as np
import pandas as pd
import time
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process, freeze_support  # Import freeze_support
from planner.Astar import AStar
from mesh.mesh import cut
from src.const import list_provincial_level
import pickle
import os
import sys

# sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

#import itertools
# start_time = time.time()
# cost_matrix = pd.read_csv('data/cost_matrix/factor_mesh/cost_matrix_2.csv')
  
# combinations = []
# list_provincial_level.remove('Taiwan') #台湾省和大陆网格上不连通
# # minimal_cost_matrix = pd.DataFrame(columns=list_provincial_level, index=list_provincial_level)
# # paths = pd.DataFrame(columns=list_provincial_level, index=list_provincial_level)
# for i in list_provincial_level:
#     for j in list_provincial_level:
#         if i != j:
#             combinations.append((i, j))

# def search_wrapper(args):
#     try:
#         Astar = AStar("euclidean", 0.2) 
#         i, j = args
#         mymesh=cut(cost_matrix,i,j)
#         path = Astar.searching(mymesh, i, j)
#         with open(f'data/optimal_paths/paths_pickle/path_{i}_{j}.pkl', 'wb') as f:
#             pickle.dump(path, f)
#         #print(combinations.index((i,j)))
#         # paths.loc[i, j] = path
#         # minimal_cost_matrix.loc[i, j] = mymesh.loc[mymesh['coord'].isin(path), 'cost_factor'].sum()
#         return True
#     except Exception as e:
#         print(f"Error processing path from {i} to {j}: {e}")
#         return False

# if __name__ == '__main__':
#     freeze_support() 
#     with ProcessPoolExecutor() as pool:
#         futures = []
#         for arg in tqdm(combinations, total=len(combinations), desc="Processing process submissions"):
#             futures.append(pool.submit(search_wrapper, arg))
        
#         for future in tqdm(futures):
#             print(future.result())
            
#     # paths.to_csv('data/optimal_paths/paths.csv')
#     # minimal_cost_matrix.to_csv('data/optimal_paths/minimal_cost_matrix.csv')
#     end_time = time.time()
#     print(f"Elapsed time: {end_time - start_time} seconds")


#*******************************************************************************************
cost_matrix = pd.read_csv('data/cost_matrix/factor_mesh/cost_matrix_2.csv', index_col=0)
list_provincial_level.remove('Taiwan')  # 台湾省和大陆网格上不连通,需要去掉，否则永远找不到路径

def search_wrapper(args):
    i, j = args
    try:
        astar = AStar(heuristic_type='euclidean', step=0.2)
        mymesh = cut(cost_matrix, i, j)
        path = astar.searching(mymesh, i, j)
        with open(f'data/optimal_paths/paths_pickle_2/path_{i}_{j}.pkl', 'wb') as f:
            pickle.dump(path, f)
        return True
    except Exception as e:
        print(f"Error processing path from {i} to {j}: {e}")
        return False
    
def run_optimal_path_search():
    start_time = time.time()
    combinations = [(i, j) for i in list_provincial_level for j in list_provincial_level if i != j]
    results = []
    with ProcessPoolExecutor() as pool:
        futures = [pool.submit(search_wrapper, arg) for arg in combinations]
        
        for future in tqdm(futures, total=len(combinations), desc="Processing process submissions"):
            results.append(future.result())
            
    end_time = time.time()
    print(f"Elapsed time: {end_time - start_time} seconds")
    return results


if __name__ == '__main__':  
    #只有在运行本文件时，才会执行if __name__ == '__main__':下的代码，如果被其他文件import，if __name__ == '__main__':下的代码不会被执行
    run_optimal_path_search()