
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

def check(string, sub_str): 
	if (string.find(sub_str) == -1): 
		return False 
	else: 
		return True

def createsubdf(master_df,str1,str2='NA'):
	result_df=pd.DataFrame()
	if str2=='NA':
		for col in master_df.columns.to_list():
			if check(col,str1):
				result_df[col]=master_df[col]
	else:
		for col in master_df.columns.to_list():
			if check(col,str1) and check(col,str2):
				result_df[col]=master_df[col]
	return result_df

def removeoutliers(df):
	Q1 = df.quantile(0.25)
	Q3 = df.quantile(0.75)
	IQR = Q3 - Q1
	df = df[~((df < (Q1 - 1.5 * IQR)) |(df > (Q3 + 1.5 * IQR))).any(axis=1)]
	return df




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
	# comparision_df.index=comparision_df['metric']
	new_header = comparision_df.T.iloc[0]
	rdf = comparision_df.T[1:]
	rdf.columns = new_header
	return rdf




foldername='/Users/akshaykulkarni/Desktop/WQU/weeklyeqwt'
master_df=pd.DataFrame()
for filename in os.listdir(foldername):
	df = pd.DataFrame()
	if filename.endswith(".xlsx"):
		filepath = os.path.join(foldername, filename)
		temp = re.findall(r'\d+', filename)
		elements=temp[0]
		df=pd.read_excel(filepath,index_col=0)
		df=df.fillna(1)
		new_cols=[]
		for old_col in df.columns.to_list():
			new_cols.append(old_col+','+str(elements)+' days')
		df.columns=new_cols
		master_df=master_df.join(df,how='outer')
		master_df=master_df.fillna(1.0)
		# for col in df.columns.to_list():
		# 	master_df[col]=df[col]

indexfile='/Users/akshaykulkarni/Desktop/WQU/weekly_1_elements_medium_indexeqwt copy.xlsx'

index_df = pd.read_excel(indexfile,index_col=0)

masterindex = master_df.index
# index_df=index_df.reindex(masterindex,fill_value=1.0)
# print(index_df)

ele = '30'
final_df=master_df
ind_df=pd.DataFrame()
# for col in index_df.columns:
# 	if check(col,'nifty'):
# 		final_df  = final_df.reindex(index_df.index)
# 		final_df[col]=index_df[col]
final_df = final_df.join(index_df, how='outer')
final_df=final_df.fillna(1.0)
final_df=createsubdf(final_df,'niftysmallcap100')
# final_df.to_excel('test.xlsx')
# exit()


years=(date.today()-date(2015,1,1))
x = years.days/252

final_df_wo_outliers = removeoutliers(final_df)
# print(final_df_wo_outliers)
# ind_df=removeoutliers(ind_df)
metrics_df = getmetrics(final_df_wo_outliers,x)

# ind_df = getmetrics(ind_df,x)

a = final_df_wo_outliers.cumprod().plot(title='NiftySmallcap100 based Portfolio')
a.legend(loc=2, prop={'size': 6})
# xticks=['10','10,index','120','120,index','20','20,index','5','5,index','60','60,index']
# for l in ['sharpe_ratios','returns','annualised return','std_devs','max_holding_loss']:
# 	#----------
# 	plt.figure()
# 	X = np.arange(len(final_df_wo_outliers.columns))
# 	plt.bar(X,metrics_df[[l]][l].to_list(),color = 'grey',width = 0.25)
# 	plt.bar(X+0.25,ind_df[[l]][l].to_list(),color = 'black', width = 0.25)
# 	plt.legend(['Portfolio','Index'])
# 	plt.xticks([i + 0.25 for i in range(5)], ['10', '120', '20', '5', '60'])
# 	plt.xlabel('Lookback, days')
# 	plt.ylabel(l)
# 	plt.title("Nifty50 based Portfolio with "+ele+" elements")
# 	plt.savefig('/Users/akshaykulkarni/Desktop/WQU/Plots/nifty50 weekly/'+l+'_'+ele+'elements.png')
	#-----------
# print(final_df_wo_outliers.describe())
# b=metrics_df[['returns']].plot.barh(figsize=(5,2.5))
# b.set_yticklabels(xticks)
# b.set_xlabel('Lookback periods, days')
# c=metrics_df[['max_holding_loss']].plot.bar()
# c.set_xticklabels(xticks)
# c.set_xlabel('Lookback periods, days')
# d=metrics_df[['sharpe_ratios']].plot.bar(figsize=(5,2.5))
# d.set_xticklabels(xticks)
# d.set_xlabel('Lookback periods, days')
# e=metrics_df[['std_devs']].plot.bar(figsize=(5,2.5))
# e.set_xticklabels(xticks)
# e.set_xlabel('Lookback periods, days')
# f=metrics_df[['annualised return']].plot.bar(figsize=(5,2.5))
# f.set_xticklabels(xticks)
# f.set_xlabel('Lookback periods, days')
plt.show()
print(metrics_df)
# metrics_df.to_excel('weekly_analysis.xlsx')



