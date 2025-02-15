import numpy as np
import pandas as pd
import geopandas as gpd
from tqdm import tqdm
from src.const import list_provincial_level
import gurobipy as gp
from gurobipy import GRB
from shapely.geometry import LineString
from src.const import alpha,PHpipe_transcost,PHpipe_capacity_Inner_Beijing,NGpipe_seperate_cost,NGpipe_convcost_20,NGpipe_convcost_100
from src.function import import_data,save_results

def full_model(year,hydrogen_demand,production_upper,electricity_price,PHpipe_buildcost,NGpipe_convcost_20,NGpipe_seperate_cost,NGpipe_convcost_100,PHpipe_transcost,filename,w):
    global PHtable,NGtable,Blendtable, Puretable  # 全局变量，因为有if__name__ == '__main__':的限制，不能在函数内部定义全局变量
    #PHtable:已存在的纯氢管道,NGtable：剩余的纯天然气管道,Blendtable：已存在的混合管道, Puretable：已存在的由天然气管道改造的纯氢管道 
    
    electricity_cost = alpha * electricity_price ## 电费成本系数，单位为亿元/万吨
    model = gp.Model()
    G, P, B,hydrogen_0,hydrogen_blend,hydrogen_100,convert_blend,convert_pure,cable = {},{}, {}, {},{},{},{},{},{}
    # G:用自身绿电生产的氢量， P:通过纯氢管道的输氢量 B:通过天然气管道的输氢量 hydrogen_0：天然气管道是否不输送氢 hydrogen_blend：天然气管道是否掺氢 hydrogen_100:H2是否以纯氢形式在天然气管道中运输，convert_blend:天然气管道是否转换成掺氢管道，  convert_pure:天然气管道是否转换成纯氢管道 cable:电线输送电代输氢量
    
    for a in list_provincial_level:
        G[a] = model.addVar(name="G_%s" % a, lb=0,ub=production_upper.loc[a, "production_upper"], vtype=GRB.CONTINUOUS)
        
    ub_P=hydrogen_demand['hydrogen_demand'].sum()
    for a in list_provincial_level:
        for b in list_provincial_level:
            P[a, b] = model.addVar(name="P_%s,%s" % (a, b),lb=0, ub=ub_P, vtype=GRB.CONTINUOUS)
            cable[a,b] = model.addVar(name="cable_%s,%s" % (a, b),lb=0, ub=production_upper.loc[a, "production_upper"], vtype=GRB.CONTINUOUS)
            
    for k in gdf_cross.index:
        B[k] = model.addVar(name="B_%s" % k, lb=0, ub=gdf_cross.loc[k, 'capacity_h2']*5, vtype=GRB.CONTINUOUS)
        
    x = model.addVars(list_provincial_level, list_provincial_level, vtype=GRB.BINARY, name="x")  # 是否新建纯氢管道，假设不再新建天然气管道
    for i in gdf_cross.index:  #gdf_cross是不变的，意为目前为止所有的天然气管道
        #三变量和为1
        hydrogen_0[i] = model.addVar(vtype=GRB.BINARY, name=f"hydrogen_0_{i}")
        hydrogen_blend[i] = model.addVar(vtype=GRB.BINARY, name=f"hydrogen_blend_{i}")
        hydrogen_100[i] = model.addVar(vtype=GRB.BINARY, name=f"hydrogen_100_{i}")
        
    for i in NGtable.index:    #NGtable是会进行更新的，意为剩下的纯天然气管道
        #hydrogen_0和这两个变量的和为1
        convert_blend[i]=model.addVar(vtype=GRB.BINARY,name=f"blend_{i}")
        convert_pure[i]=model.addVar(vtype=GRB.BINARY,name=f"pure_{i}")    
    model.update()

    objective = gp.quicksum(year*(G[i]-sum(cable[i,j] for j in list_provincial_level if i!=j))*electricity_cost.loc[i]  for i in list_provincial_level) #氢气电解成本，每电解1kgH2需要多少万元
    objective += gp.quicksum(
            #输电代输氢的成本,结合距离，线损
            year*cable[i,j]*(w*electricity_cost[j]+(1-w)*electricity_cost[i])*loss.loc[i,j]   for i in list_provincial_level for j in list_provincial_level if i!=j)
    
    objective += gp.quicksum(
        #新建纯氢管道建设成本
            x[i, j]  #是否建
            * PHpipe_buildcost.loc[i, j] #cost_matrix得到的建设成本
            #* y[i,j] #容量
            #纯氢管道运输成本
            + year*PHpipe_transcost * P[i, j]* paths_length.loc[i,j]
            for i in list_provincial_level
            for j in list_provincial_level)

    #由天然气管道转换而来的纯氢管道的运输成本
    objective += gp.quicksum(hydrogen_100[k]*year*PHpipe_transcost*B[k]*gdf_cross.loc[k,'length'] for k in gdf_cross.index)
    
    #天然气管道转换成纯氢管道的成本
    objective += gp.quicksum(convert_pure[f]*NGpipe_convcost_100*gdf_cross.loc[f,'length']  for f in NGtable.index)
    
    #掺氢天然气管道掺氢的运输+分离成本      
    objective += gp.quicksum(hydrogen_blend[k]*year*(NGpipe_seperate_cost *B[k] + PHpipe_transcost*B[k]*gdf_cross.loc[k,'length']) for k in gdf_cross.index )
    
    #天然气管道掺氢的转换成本                        
    objective+= gp.quicksum(convert_blend[k]*NGpipe_convcost_20*gdf_cross.loc[k,'length'] for k in NGtable.index)  

            #electricity_cost的单位是万元/kgH2
    # buildcost也需要和capacity:P[i,j]-PHtable.loc[i,j]成正比,且只要输气就有输送成本，不管在已建成的管道还是新建的管道

    model.setObjective(objective, sense=GRB.MINIMIZE)
    model.update()
    
    
    
    #增加自身到自身的约束
    for a in list_provincial_level:
        P[a, a].ub = 0  # 将上界设置为0，因此P[a, a] 必须为0
        x[a,a].ub=0
        cable[a,a].ub=0 #把电线当作另外一种管道
    
    #B大于20%的管道，要变成纯氢管道，否则则是掺氢管道。    
    M = 1e17
    #expresion <=  M * x <= M + expression - B
    for k in gdf_cross.index:
    
        model.addConstr(0.1-B[k] <= M * hydrogen_0[k], "0_constraint")   # B[k]<0.1时，hydrogen_0[k]=1的约束
        model.addConstr(M * hydrogen_0[k] <= M + 0.1 - B[k]-1, "0_constraint")  # B[k]>0.1时，hydrogen_0[k]=0的约束
        
        # model.addConstr( gdf_cross.loc[k,'capacity_h2']-B[k]  <= M * hydrogen_blend[k] , "blend_constraint") #B[k]<capacity_h2时，hydrogen_blend[k]=1
        model.addConstr(M * hydrogen_blend[k]<=M+ gdf_cross.loc[k,'capacity_h2']-B[k] -1, "blend_constraint")#B[k]>=capacity_h2时，hydrogen_blend[k]=0
        
        model.addConstr(B[k]-gdf_cross.loc[k,'capacity_h2']  <= M * hydrogen_100[k] , "pure_constraint") #B[k]>=capacity_h2时，hydrogen_100[k]=1
        model.addConstr(M * hydrogen_100[k]<=M+ B[k]-gdf_cross.loc[k,'capacity_h2'] -1, "pure_constraint") #B[k]<capacity_h2时，hydrogen_100[k]=0
        
        model.addConstr(hydrogen_0[k] + hydrogen_blend[k] + hydrogen_100[k]  == 1, "binary_constraint")

    for k in NGtable.index:
        model.addConstr(convert_blend[k] == hydrogen_blend[k], "NG_constraint")
        model.addConstr(convert_pure[k] == hydrogen_100[k], "NG_constraint")

            
    #产氢量+电线的总容量<=总产能上限
    model.addConstrs(G[i]+sum(cable[i,j] for j in list_provincial_level) <=production_upper.loc[i, "production_upper"] for i in list_provincial_level) 
    
    for i in list_provincial_level:
        model.addConstr(
            G[i] == 
            hydrogen_demand.loc[i].values[0]  
            +sum(cable[i,j] for j in list_provincial_level if i!=j)
            -sum(cable[j,i] for j in list_provincial_level if i!=j)
            +sum(P[i, j] for j in list_provincial_level)
            -sum(P[j, i] for j in list_provincial_level)
            +sum([hydrogen_blend[k]* B[k] for k in gdf_cross.index if gdf_cross.loc[k,'start']==i])
            -sum([hydrogen_blend[k]* B[k] for k in gdf_cross.index if gdf_cross.loc[k,'end']==i]) 
            +sum(hydrogen_100[k]*B[k] for k in gdf_cross.index if gdf_cross.loc[k,'start']==i) 
            -sum(hydrogen_100[k]*B[k] for k in gdf_cross.index if gdf_cross.loc[k,'end']==i) 
            
        )
        
    
        # -s_minus+s_plus 约束1：每个省的氢的生产+天然气管道输入（2种）+新建纯氢管道输入=消耗+天然气管道输出（2种）+新建纯氢管道输出，后续可以在h2_use上再考虑出口。
    # model.addConstrs((y[i, j] * y[i, j] == (P[i, j] - PHtable.loc[i, j])/PHpipe_capacity_Inner_Beijing
    #                     for i in list_provincial_level for j in list_provincial_level), "sqrtConstr")
        # 设置 NonConvex 参数允许求解非凸问题
    # model.setParam('NonConvex', 2)

    for i in list_provincial_level:  # 约束2：当PHtable[i,j]=0,且P[i,j]>0时，或P[i,j]>3*PHtable[i,j]时，需要新建管道,Gurobi 不能直接处理布尔表达式作为约束,需要引入一个大 M 值
        for j in list_provincial_level:
            if PHtable.loc[i, j] == 0:
                model.addConstr(x[i, j]*M >= P[i, j] )
            else:
                model.addConstr(x[i, j] * M >= P[i, j] - 3*PHtable.loc[i, j])
                model.addConstr(x[i, j] * M <= M + P[i, j] - 3*PHtable.loc[i, j] - 1)
            
   
    model.Params.TimeLimit = 60*16
    # model.setParam("MIPGap", 0.004)
    if model.Status != GRB.Status.INF_OR_UNBD and model.Status != GRB.Status.INFEASIBLE:
        model.optimize()
    else:
        print("Model is infeasible or unbounded")
        return


    df_G = pd.DataFrame([G[i].X for i in list_provincial_level],index=list_provincial_level, columns=['G'])
    df_G[df_G < 1] = 0 

    df_P = pd.DataFrame([[P[i, j].X for j in list_provincial_level] for i in list_provincial_level],
                        index=list_provincial_level, columns=list_provincial_level)
    df_P[df_P < 1] = 0
    PH_amount=df_P.sum().sum()
    print(f'{PH_amount}kg通过纯氢管道')
    
    #更新、保存总共的纯氢管道
    PHtable=df_P.where(df_P >= PHtable, PHtable)
    # PHbuild=df_P-PHtable
    # x = PHbuild[PHbuild > 0].fillna(0)
    # x = x[x <= 0].fillna(1)   #有管道的地方是0，没有的地方是1
    
    #保存了使用了的纯氢管道,
    new_paths_dict = []
    for i in df_P.index: #哪一行，起点
        for j in df_P.columns: #哪一列，终点
            if df_P.loc[i,j]>0:
                new_paths_dict.append({'from': i, 'to': j, 'geometry': LineString(df_paths.loc[i, j]), 'capacity': df_P.loc[i,j],'length':paths_length.loc[i,j]})
    
    #保存了由天然气管道转换而来的纯氢管道
    pure_paths_dict = [] 
    for i in gdf_cross.index:
        if hydrogen_100[i].X==1:
            pure_paths_dict.append({'from': gdf_cross.loc[i,'start'], 'to': gdf_cross.loc[i,'end'], 'geometry': gdf_cross.loc[i, 'geometry'], 'amount':B[i].X,'capacity': gdf_cross.loc[i,'capacity_h2']*5,'length':gdf_cross.loc[i,'length']})
            
    #保存了掺氢天然气管道       
    blend_paths_dict = []
    for i in gdf_cross.index:
        if hydrogen_blend[i].X==1:
            blend_paths_dict.append({'from': gdf_cross.loc[i,'start'], 'to': gdf_cross.loc[i,'end'], 'geometry': gdf_cross.loc[i, 'geometry'], 'amount':B[i].X,'capacity': gdf_cross.loc[i,'capacity_h2']*5,'length':gdf_cross.loc[i,'length']})
    
    #删除更新NGtable,Blendtable,Puretable
    for i in NGtable.index:
        if convert_blend[i].X==1:
            Blendtable.loc[i,:]=gdf_cross.loc[i,:]
            NGtable.drop(i,inplace=True)
        if convert_pure[i].X==1:
            Puretable.loc[i,:]=gdf_cross.loc[i,:]
            NGtable.drop(i,inplace=True)
    
    NG_20_amount=sum(item['amount'] for item in blend_paths_dict)
    NG_100_amount=sum(item['amount'] for item in pure_paths_dict)
    print(f'{NG_20_amount}kg通过掺氢管道')
    print(f'{NG_100_amount}kg通过纯氢管道')

    
    df_cable = pd.DataFrame([[cable[i, j].X for j in list_provincial_level] for i in list_provincial_level],
                        index=list_provincial_level, columns=list_provincial_level)
    df_cable[df_cable < 1] = 0
    cable_amount=df_cable.sum().sum()
    print(f'电线输送{cable_amount}kgH2')
    
    save_results(filename,df_G,df_P,PHtable,new_paths_dict,pure_paths_dict,blend_paths_dict,NGtable,df_cable)
    return PH_amount,NG_20_amount,NG_100_amount,cable_amount,model.objVal
    


if __name__ == '__main__':
    
    production_upper, PHtable, minimal_cost_matrix, paths_length, df_paths, gdf_cross,NGtable, Blendtable, Puretable, electricity_price, PHpipe_buildcost,loss= import_data()
    
    t=10
    list_obj=[]
    list_PH_amount=[]
    list_blend_amount=[]
    list_100_amount=[]
    list_cable_amount=[]
    list_w=[0,0.25,0.5,0.75,1]
    for year in [2030,2040,2050,2060]:
        #递进式的优化，2030年的P会变成优化2024年时的PHtable
        hydrogen_demand=pd.read_csv(f"/home/xiangdebin/ceci/data/consumption_potential/demand_{year}.csv",index_col=0)
        
        PH_amount,NG_20_amount,NG_100_amount,cable_amount,objVal=full_model(t,hydrogen_demand,production_upper,electricity_price['level'],PHpipe_buildcost,NGpipe_convcost_20,NGpipe_seperate_cost,NGpipe_convcost_100,PHpipe_transcost,f"year{year}_w{0.5}",0.5)
            
        list_PH_amount.append(PH_amount)
        list_blend_amount.append(NG_20_amount)
        list_100_amount.append(NG_100_amount)
        list_cable_amount.append(cable_amount)
        list_obj.append(objVal)
      
    
    print(list_PH_amount)
    print(list_blend_amount)
    print(list_100_amount)
    print(list_cable_amount)
    print(list_obj)
    print(f"total cost: {sum(list_obj)}")
    
    




 