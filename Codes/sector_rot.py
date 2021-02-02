from datetime import datetime,timedelta,date
import pandas as pd
import numpy as np
import datetime
import matplotlib
import operator
import itertools
import matplotlib.pyplot as plt
import os
import re

def getmetrics(df,x):
	returns={}
	sharpe_ratios={}
	max_drawdown={}
	std_devs={}
	ann_returns={}
	ann_returns['metric']='annualised return'
	returns['metric']='returns'
	sharpe_ratios['metric']='sharpe_ratios'
	max_drawdown['metric']='max_holding_loss'
	std_devs['metric']='std_devs'

	for column in df.columns.to_list():
		sharpe_ratios[column]=(df[column]-1).mean()*1.0/(df[column]-1).std()
		max_drawdown[column]=(df[column]-1).min()
		returns[column]=df[column].prod()
		ann_returns[column]=df[column].prod()**1.0/x*100
		std_devs[column]=(df[column]-1).std()

	comparision_df=pd.DataFrame()
	comparision_df=comparision_df.append(returns,ignore_index=True)
	comparision_df=comparision_df.append(sharpe_ratios,ignore_index=True)
	comparision_df=comparision_df.append(max_drawdown,ignore_index=True)
	comparision_df=comparision_df.append(std_devs,ignore_index=True)
	comparision_df=comparision_df.append(ann_returns,ignore_index=True)
	comparision_df.index=comparision_df['metric']
	# new_header = comparision_df.T.iloc[0]
	# rdf = comparision_df.T
	# rdf.columns = new_header
	return comparision_df.T

def removeoutliers(df):
	Q1 = df.quantile(0.2)
	Q3 = df.quantile(0.8)
	IQR = Q3 - Q1
	df = df[~((df < (Q1 - 1.5 * IQR)) |(df > (Q3 + 1.5 * IQR))).any(axis=1)]
	return df

result=pd.DataFrame()
for e in ['quarterly','halfyearly','yearly']:#['weekly','biweekly','monthly']:#,'quarterly','halfyearly','yearly']:
	foldername='/Users/akshaykulkarni/Desktop/WQU/Codes/sectorrotation/'+e
	master_df=pd.DataFrame()
	for filename in os.listdir(foldername):
		df = pd.DataFrame()
		if filename.endswith(".xlsx"):
			filepath = os.path.join(foldername, filename)
			names=filename.split('_')
			elements=names[1]
			strat=names[2]
			df=pd.read_excel(filepath,index_col=0)
			df=df.fillna(1)
			new_cols=[]
			for old_col in df.columns.to_list():
				new_cols.append(old_col+','+str(elements)+' elements, '+strat)
			df.columns=new_cols
			master_df=master_df.join(df,how='outer')
			master_df=master_df.fillna(1.0)

	years=(date.today()-date(2015,1,1))
	x = years.days/252

	#final_df = removeoutliers(master_df)
	metrics_df = getmetrics(master_df,x)
	result = pd.concat([result, metrics_df],axis = 0)
	print(metrics_df)
result.to_excel('sectorrotlong.xlsx')
