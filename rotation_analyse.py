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
	print(comparision_df)
	# comparision_df.index=comparision_df['metric']
	new_header = comparision_df.T.iloc[0]
	rdf = comparision_df.T[1:]
	rdf.columns = new_header
	return rdf

def removeoutliers(df):
	Q1 = df.quantile(0.2)
	Q3 = df.quantile(0.8)
	IQR = Q3 - Q1
	df = df[~((df < (Q1 - 1.5 * IQR)) |(df > (Q3 + 1.5 * IQR))).any(axis=1)]
	return df

filename='/Users/akshaykulkarni/Desktop/WQU/Rotation/rotation_monthly_eqwt.xlsx'

df = pd.read_excel(filename,index_col=0)
df = df.fillna(1.0)

# df = removeoutliers(df)

years=(date.today()-date(2015,1,1))
x = years.days/252
print(df)
a = df.cumprod().plot(title='Rotation based Portfolio')
a.legend(loc=2, prop={'size': 6})
plt.show()
metrics_df = getmetrics(df,x)
print(metrics_df)

metrics_df.to_excel('monthlyrotation_analysis.xlsx')

