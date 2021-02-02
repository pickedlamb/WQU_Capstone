from nsepy import get_history
from datetime import datetime,timedelta,date
import pandas as pd
import numpy as np
import datetime
import matplotlib
import operator
import itertools
from nsepy.symbols import get_symbol_list, get_index_constituents_list
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


def read_data(filename,token_name,from_date, to_date,interval,indexbool,lookback,holdingdays):
	df = pd.read_excel(filename,index_col=0)
	i=0
	while i < len(token_name):
		df1=df[df['Symbol']==token_name[i]]
		if i==0:
			df2=df1
		else:
			df1 = df1.reindex(ind)
			df2=df1.fillna(method='ffill')

		df2['Change'] = (df1.Close - df1.Close.shift(lookback))*100/df1.Close.shift(lookback)
		df2['afterholding']=df1['Close'].pct_change(holdingdays).shift(-1*holdingdays)
		if i ==0:
			df_final = df2
			ind=df_final.index
		else:
			df_final = pd.concat([df_final, df2],axis = 0)
		i = i+1
	df_final['Date']=df_final.index
	return df_final

def createbasket(df_final,basket_elements,indexbool,lookback,holdingdays):
	output=pd.pivot_table(df_final,index=df_final.index,columns='Symbol',values=["Change"])
	output=output.fillna(0)
	pivotdicts=output.to_dict(orient="records")
	wt = 1.0/basket_elements
	basket_df=pd.DataFrame()
	#datelist=[]
	basketlist=[]
	for i in range(lookback,len(output)-holdingdays,holdingdays):
		sorted_pivotdicts=dict(sorted(pivotdicts[i].items(), key=operator.itemgetter(1),reverse=True))
		temp_dict={'basket':dict(itertools.islice(sorted_pivotdicts.items(), basket_elements))}
		temp_list=[]
		#datelist.append()
		basket_dict={}
		for key in temp_dict['basket'].keys():
			temp_list.append(key[1])
			temp_tup=('Change',key[1])
			basket_dict[key[1]]=temp_dict['basket'][temp_tup]
			del temp_tup
	
		current_date=output.index[i]
		prev_date=output.index[i-lookback]
		for token in temp_list:
			#print(token)
			temp_df=df_final[df_final['Symbol']==token]
			temp_df_curr=temp_df[temp_df['Date']==current_date]
			# temp_df_prev=temp_df[temp_df['Date']==prev_date]
			# current_close=temp_df_curr['Close']
			# prev_close=temp_df_prev['Close']
			#print(current_close,prev_close)
			
			if not indexbool:
				try:
					#ret = (current_close.iloc[0]-prev_close.iloc[0])/100.0
					ret = temp_df_curr['Change'].item()
					if (ret<=0.0):
						del basket_dict[token]
				except:
					pass
				
				   
		basketlist.append({'basket':basket_dict})
	basket_df=pd.DataFrame(basketlist,index=output.index.tolist()[lookback:len(output)-holdingdays:holdingdays])
	basket_df['Date']=basket_df.index
	return basket_df

def getbasketreturn(df_final,basket_df,holdingdays,basket_elements):
	return_df=pd.DataFrame()
	#wt = 1.0/basket_elements
#     test=df_final['Close']
#     df_final['afterholding']=test.pct_change(holdingdays)
	#print(df_final.head(20))
	basket_df['afterholding']=''
	for i in range(0,len(basket_df)):
		tokennames=[]
		change=pd.DataFrame()
		for key in basket_df.iloc[i,0].keys():
			tokennames.append(key)
		wt = 1.0/basket_elements*len(tokennames)/basket_elements
		dt=basket_df.index.to_list()[i]
		dt=pd.to_datetime(dt, format='%Y-%m-%d', errors='ignore')
		#print(dt)
		#portfolio=getweights(tokennames,df_final,holdingdays,dt,basket_elements)
		cond1 = df_final['Symbol'].isin(tokennames)
		cond2 = df_final['Date']==basket_df.iloc[i,1]
		#print(basket_df.iloc[i,1])
		
		change=df_final[cond1 & cond2][['Symbol','afterholding']]
		#change=change.fillna(0)
		returnn=0
		for idx,row in change.iterrows():
			# returnn=returnn+portfolio[row['Symbol']]*(row['afterholding'])
			returnn=returnn+wt*(row['afterholding'])
		#for ret in change.tolist():
		#    returnn=returnn+wt*ret
		basket_df['afterholding'][i]=returnn*100
		
	return_df=basket_df[basket_df['afterholding']!= ""]
	return return_df

longterm={}
# longterm['weekly']={'lookback':[5,10,20,60,120],'holdingdays':10,'basket_elements':[1]}
# longterm['biweekly']={'lookback':[5,10,20,60,120],'holdingdays':10,'basket_elements':[1]}
# longterm['monthly']={'lookback':[10,20,60,120,240],'holdingdays':20,'basket_elements':[1]}
longterm['quarterly']={'lookback':[20,60,120,240],'holdingdays':60,'basket_elements':[1]}
# longterm['halfyearly']={'lookback':[60,120,240],'holdingdays':120,'basket_elements':[1]}
# longterm['yearly']={'lookback':[120,240],'holdingdays':240,'basket_elements':[1]}


indices=['nifty50','niftymidcap100','niftysmallcap100','GOLDBEES','LICNETFGSC']

to_date = date.today()- timedelta(days=0)
interval = "day"
from_date=date(2015,1,1)

for strategy in longterm:
	holdingdays=longterm[strategy]['holdingdays']
	for basket_elements in longterm[strategy]['basket_elements']:
		output_df=pd.DataFrame()
		for lookback in longterm[strategy]['lookback']:
			print(strategy,lookback)
			temp_df=pd.DataFrame()
			df_final= read_data('/Users/akshaykulkarni/Desktop/WQU/sectorraw.xlsx',indices, from_date, to_date,interval,False,lookback,holdingdays)
			basket_df=createbasket(df_final,1,False,lookback,holdingdays)
			return_df=getbasketreturn(df_final,basket_df,holdingdays,1)
			temp_df['Rotation,'+str(lookback)+' days']=return_df['afterholding'].apply(lambda x: (x-0.05)/100 +1 )
			output_df=output_df.join(temp_df,how='outer')
			output_df=output_df.fillna(1.0)
	output_df.to_excel('rotation_'+strategy+'_eqwt'+'.xlsx')


