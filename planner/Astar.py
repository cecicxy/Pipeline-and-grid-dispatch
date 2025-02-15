"""
A_star 2D
"""
import math
import heapq
import pandas as pd
import numpy as np
from typing import List, Tuple
class AStar:
    """AStar set the cost + heuristics as the priority
    """
    def __init__(self,heuristic_type,step):
        self.heuristic_type = heuristic_type
        self.step=step
        self.u_set = [(-step, 0), (-step, step), (0, step), (step, step),
                        (step, 0), (step, -step), (0, -step), (-step, -step)]  
        # feasible input set,multiply the x and y, if not zero, it is diagonal

        self.OPEN = []  # priority queue / OPEN set
        self.CLOSED = []  # VISITED order / CLOSED set
        self.PARENT = dict()  # recorded parent
        self.g = dict()  # cost to come
        

    def searching(self,mesh:pd.DataFrame,i: str,j:str)->List:
        """A_star Searching

        Args:
            mesh (pd.DataFrame): cutted mesh
            start (Tuple): start point's coordinate
            end (Tuple): end point's coordinate

        Returns:
            List: path
        """        
        self.mymesh = mesh
        self.mesh_coords_set = set(self.mymesh['coord'])  # 新增属性来存储坐标集合
        
        self.s_start = self.mymesh[self.mymesh['capital'] == i]['coord'].values[0]
        self.s_goal = self.mymesh[self.mymesh['capital'] == j]['coord'].values[0]
        self.PARENT[self.s_start] = self.s_start
        self.g[self.s_start] = 0
        self.g[self.s_goal] = math.inf
        self.coeffient=self.mymesh['cost_factor'].mean() #从mean改成min，或许能满足一致性

        heapq.heappush(self.OPEN,
                       (self.f_value(self.s_start), self.s_start)) 
        #heapq.heappush(A,B）,  will add B into A. self.OPEN is a list that is being used as a heap. A heap is a binary tree where a parent node is less than or equal to its child node(s). Insert a tuple, compare the first element of tuple which is the f value
        

        
        while self.OPEN:
            # while self.OPEN: will continue to loop as long as self.OPEN is not empty. If self.OPEN becomes empty (i.e., it has no elements), the loop will stop.

            _, s = heapq.heappop(self.OPEN) 
            #print(f"pop {s}")
            # pops the smallest item from the heap，will remove the smallest element in the heap every time, here only need the state，namely coordinate
                
            self.CLOSED.append(s) 
            #The self.CLOSED list contains all the nodes that have been visited during the search, in the order they were visited. This is not necessarily the optimal path from the start to the goal

            if s == self.s_goal:  # stop condition
                #print("goal reached")
                break

            for s_n in self.get_neighbor(s):   #遍历了所有的邻居
                if s_n not in self.mesh_coords_set: #如果邻居不在mesh里，即越界，则跳过这个邻居
                    #print(f"{s_n} is not in mesh")
                    continue

                
                new_g = self.g[s] + self.cost(s, s_n)
                
                if s_n not in self.g:         #初始化,if s_n is goal,next round will break
                    self.g[s_n] = math.inf

                if new_g < self.g[s_n]:  # 有cost更小的邻居则替代到parent里，conditions for updating g-value
                    self.g[s_n] = new_g
                    self.PARENT[s_n] = s    #child:parent
                    #parent and child  have some neighbors(children) in common. but dict can not have same key, so the one with lower g-value will be kept
                    heapq.heappush(self.OPEN, (self.f_value(s_n), s_n))  
            
                    
        return self.extract_path(self.PARENT)

    def get_neighbor(self, s):
        """
        find neighbors of state s that not in obstacles.
        :param s: state
        :return: neighbors
        """
        return [(round(s[0] + u[0],1), round(s[1] + u[1],1)) for u in self.u_set] # return a list, each element is a tuple
    
    def haversine(self,s, s_n):
        # 将经纬度转换成弧度
        list_s=list(s)
        list_s_n=list(s_n)
        list_s[1], list_s[0], list_s_n[1], list_s_n[0] = map(math.radians, [s[1], s[0], s_n[1], s_n[0]])

        # 计算纬度和经度的差值
        dlat = list_s_n[1] - list_s[1]
        dlon = list_s_n[0] - list_s[0]

        # 应用Haversine公式
        a = math.sin(dlat / 2)**2 + math.cos(list_s[1]) * math.cos(list_s_n[1]) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))

        # 地球的平均半径（公里）
        r = 6371

        # 计算结果,单位为公里
        return c*r
    
    def cost(self, s, s_n):
        """
        Calculate Cost for this motion
        :param s: current node
        :param s_n: next node
        :return:  Cost for this motion
        :note: Cost function could be more complicated!
        """

        if s_n not in self.mymesh['coord'].to_list() :
            return math.inf
        #2、cost_factor的均值0.42,在启发函数里不能单纯用距离，否则会导致启发函数值大于实际值，从而导致A*算法不会选择最优路径
        return 0.5*(self.mymesh[self.mymesh['coord']==s_n]['cost_factor'].iloc[0] + self.mymesh[self.mymesh['coord']==s]['cost_factor'].iloc[0])*self.haversine(s, s_n)


    def f_value(self, s):
        """
        f = g + h. (g: Cost to come, h: heuristic value)
        :param s: current state
        :return: f
        """
        return self.g[s] + self.heuristic(s)

    def extract_path(self, PARENT):
        """
        Extract the path based on the PARENT set.
        :return: The planning path
        """
        path = [self.s_goal] #initialize path, goal is determined
        s = self.s_goal      #Backtracking from goal to start

        while True:
            s = PARENT[s] # child:parent
            path.append(s)  # add patent to path

            if s == self.s_start:  #until start is reached
                break

        return list(reversed(path)) #start to goal

    def heuristic(self,s):
        """
        Calculate heuristic.
        :param s: current node (state)
        :return: heuristic function value
        理想情况下，h(n) 应该是「乐观的」，意味着它应该低于或等于从 n 到目标的实际最小成本。这样可以确保算法总是朝着目标前进。
        可以进行修改
        """

        #heuristic_type = self.heuristic_type  # heuristic type
        #goal = self.s_goal  # goal node
          #可以调整，主要为了让启发函数f和g值在同一个数量级上，且偏小
        # if heuristic_type == "manhattan":
        #     return abs(goal[0] - s[0]) + abs(goal[1] - s[1])
        
        return self.coeffient*self.haversine(s,self.s_goal)

if __name__ == '__main__':
    import warnings
    warnings.filterwarnings('ignore')
    import pandas as pd
    import geopandas as gpd
    import time 
    from concurrent.futures import ProcessPoolExecutor
    
    import sys
    import os

    # 添加 folder1 到 sys.path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mesh')))

    # 现在可以导入 folder1 中的模块
    import mesh


    cost_matrix=pd.read_csv('data/cost_matrix/factor_mesh/cost_matrix.csv')
    start_time=time.time()
    little_provinces = ['Heilongjiang','Shanghai']
    import warnings
    warnings.filterwarnings('ignore')
    minimal_cost_matrix=pd.DataFrame(columns=little_provinces,index=little_provinces)
    paths=pd.DataFrame(columns=little_provinces,index=little_provinces)

    for i in little_provinces:
        for j in little_provinces:
            if i!=j:
                Astar=AStar("euclidean",0.2)
                mymesh=mesh.cut(cost_matrix,i,j)
                path=Astar.searching(mymesh,i,j) #找到最短路径
                paths.loc[i,j]=path  
                minimal_cost_matrix.loc[i,j]=mymesh.loc[mymesh['coord'].isin(path),'cost_factor'].sum()  #保存最短路径对应的最小成本            
    #minimal_cost_matrix #.to_csv("../data/geo data/minimal_cost_matrix.csv")
    end_time=time.time()
    print("time cost:",end_time-start_time)
    print(paths)

