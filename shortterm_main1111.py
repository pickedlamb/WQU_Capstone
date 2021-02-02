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
		df2=df1
		df2['Change'] = (df1.Close - df1.Close.shift(lookback))*100/df1.Close.shift(lookback)
		df2['afterholding']=df1['Close'].pct_change(holdingdays).shift(-1*holdingdays)
		if i ==0:
			df_final = df2
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

def getweights(tokennames,df_final,holdingdays,dt,basket_elements):
	#df = df_final[df_final['Symbol'].isin(tokennames)]
	df=pd.DataFrame()
	ann = 252/holdingdays
	for token in tokennames:
		l = df_final[df_final['Symbol']==token].Close
		df[token]=l
	df.index = pd.to_datetime(df.index)
	df=df.loc[:dt]
	#print(df)
	p_ret = [] # Define an empty array for portfolio returns
	p_vol = [] # Define an empty array for portfolio volatility
	p_weights = [] # Define an empty array for asset weights
	num_assets = len(df.columns)
	#print(num_assets)
	num_portfolios = 100
	for portfolio in range(num_portfolios):
		weights = np.random.random(num_assets)
		weights = weights/np.sum(weights)*num_assets/basket_elements
		p_weights.append(weights)
		ind_er = df.resample(str(holdingdays)+'D').last().pct_change().mean()
		ind_er=ind_er.fillna(0)
		
		returns = np.dot(weights, ind_er)
		p_ret.append(returns)
		cov_matrix = df.pct_change().apply(lambda x: np.log(1+x)).cov()
		var = cov_matrix.mul(weights, axis=0).mul(weights, axis=1).sum().sum()# Portfolio Variance
		sd = np.sqrt(var) # Daily standard deviation
		#change. here
		ann_sd = sd*np.sqrt(ann) # Annual standard deviation = volatility
		p_vol.append(ann_sd)
	data = {'Returns':p_ret, 'Volatility':p_vol}

	for counter, symbol in enumerate(df.columns.tolist()):
		#print(counter, symbol)
		data[symbol] = [w[counter] for w in p_weights]
	portfolios  = pd.DataFrame(data)
	#print(portfolios)
	#portfolios.plot.scatter(x='Volatility', y='Returns', marker='o', s=10, alpha=0.3, grid=True, figsize=[10,10])
	min_vol_port = portfolios.iloc[portfolios['Volatility'].idxmin()]
	#print(min_vol_port)
	# Finding the optimal portfolio
	rf = 0.01 # risk factor
	optimal_risky_port = portfolios.iloc[((portfolios['Returns']-rf)/portfolios['Volatility']).idxmax()]
	# Plotting optimal portfolio
#     plt.subplots(figsize=(10, 10))
#     plt.scatter(portfolios['Volatility'], portfolios['Returns'],marker='o', s=10, alpha=0.3)
#     plt.scatter(min_vol_port[1], min_vol_port[0], color='r', marker='*', s=50)
#     plt.scatter(optimal_risky_port[1], optimal_risky_port[0], color='g', marker='*', s=50)
	return optimal_risky_port
   
nifty50=get_index_constituents_list("nifty50").Symbol.tolist()
# niftymidcap50=get_index_constituents_list("niftymidcap50").Symbol.tolist()
niftymidcap100=get_index_constituents_list("niftymidcap100").Symbol.tolist()
# niftymidcap150=get_index_constituents_list("niftymidcap150").Symbol.tolist()
niftysmallcap100=get_index_constituents_list("niftysmallcap100").Symbol.tolist()
# token_name = ['ADANIPOWER','AMARAJABAT','APOLLOHOSP','APOLLOTYRE','ASHOKLEY','BALKRISIND','BANKINDIA','BATAINDIA','BEL','BHARATFORG','BHEL','CESC','CANBK','CASTROLIND','CHOLAFIN','CUMMINSIND','ESCORTS','EXIDEIND','FEDERALBNK','GMRINFRA','GLENMARK','GODREJPROP','IDFCFIRSTB','IBULHSGFIN','JINDALSTEL','JUBLFOOD','L&TFH','LICHSGFIN','MRF','MGL','MANAPPURAM','MFSL','MINDTREE','NATIONALUM','OIL','RBLBANK','RECLTD','SRF','SAIL','SUNTV','TVSMOTOR','TATACONSUM','TATAPOWER','RAMCOCEM','TORNTPOWER','UNIONBANK','IDEA','VOLTAS','NETFMID150']
# index_name=['NIFTYMID50','NIFTY SMALLCAP 50','NIFTY AUTO','NIFTY BANK','NIFTY IT','NIFTY METAL','NIFTY REALTY','NIFTY PHARMA','NIFTY FMCG','NIFTY GROWSECT 15','NIFTY50 VALUE 20','NIFTY GS 10YR']
# etf_name=['GOLDBEES','LIQUIDBEES','LICNETFGSC','SETF10GILT','NETFLTGILT']


indexwise_dict={}
indexwise_dict['nifty50']=nifty50
#indexwise_dict['niftymidcap50']=niftymidcap50
indexwise_dict['niftymidcap100']=niftymidcap100
#indexwise_dict['niftymidcap150']=niftymidcap150
indexwise_dict['niftysmallcap100']=niftysmallcap100
#indexwise_dict['etfs']=etf_name
to_date = date.today()- timedelta(days=0)
interval = "day"
from_date=date(2015,1,1)
longterm={}

#longterm['weekly']={'lookback':[5,10,20,60,120],'holdingdays':5,'basket_elements':[10,20,25,30]}
#longterm['biweekly']={'lookback':[5,10,20,60,120],'holdingdays':10,'basket_elements':[10,20,25,30]}
longterm['monthly']={'lookback':[10,20,60,120,240],'holdingdays':20,'basket_elements':[10,20,25,30]}

for strategy in longterm:
	holdingdays=longterm[strategy]['holdingdays']
	for basket_elements in longterm[strategy]['basket_elements']:
		output_df=pd.DataFrame()
		for l in indexwise_dict.keys():
			for lookback in longterm[strategy]['lookback']:
				print(l,str(lookback)+'days',str(basket_elements)+'elements')
				df_final = read_data('/Users/akshaykulkarni/Desktop/WQU/raw/'+str(l)+'_raw.xlsx',indexwise_dict[l], from_date, to_date,interval,False,lookback,holdingdays)
				print('data read')
				basket_df=createbasket(df_final,basket_elements,False,lookback,holdingdays)
				print('baskets generated')
				return_df=getbasketreturn(df_final,basket_df,holdingdays,basket_elements)
				print('got the returns')
				output_df[l+','+str(lookback)+' days']=return_df['afterholding'].apply(lambda x: (x-0.05)/100 +1 )
				
				
		output_df.to_excel(str(strategy)+'_'+str(basket_elements)+'_elements_medium_eqwt'+'.xlsx')



