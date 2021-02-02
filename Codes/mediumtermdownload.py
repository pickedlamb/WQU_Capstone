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



def download_data(token_name, from_date, to_date,interval,indexbool,l):
    i=0
    while i < len(token_name):
        records = get_history(symbol=token_name[i],start=from_date,end=to_date,index=indexbool)
        df = pd.DataFrame(records)
        df['Symbol']=token_name[i]
        if i ==0:
            df_final = df
        else:
            df_final = pd.concat([df_final, df],axis = 0) 
        i = i+1
    df_final['Date']=df_final.index
    df_final.to_excel(str(l)+'_rawmedium.xlsx')


# nifty50=get_index_constituents_list("nifty50").Symbol.tolist()
# # niftymidcap50=get_index_constituents_list("niftymidcap50").Symbol.tolist()
# niftymidcap100=get_index_constituents_list("niftymidcap100").Symbol.tolist()
# # niftymidcap150=get_index_constituents_list("niftymidcap150").Symbol.tolist()
# niftysmallcap100=get_index_constituents_list("niftysmallcap100").Symbol.tolist()
# token_name = ['ADANIPOWER','AMARAJABAT','APOLLOHOSP','APOLLOTYRE','ASHOKLEY','BALKRISIND','BANKINDIA','BATAINDIA','BEL','BHARATFORG','BHEL','CESC','CANBK','CASTROLIND','CHOLAFIN','CUMMINSIND','ESCORTS','EXIDEIND','FEDERALBNK','GMRINFRA','GLENMARK','GODREJPROP','IDFCFIRSTB','IBULHSGFIN','JINDALSTEL','JUBLFOOD','L&TFH','LICHSGFIN','MRF','MGL','MANAPPURAM','MFSL','MINDTREE','NATIONALUM','OIL','RBLBANK','RECLTD','SRF','SAIL','SUNTV','TVSMOTOR','TATACONSUM','TATAPOWER','RAMCOCEM','TORNTPOWER','UNIONBANK','IDEA','VOLTAS','NETFMID150']
#index_name=['NIFTYMID50','NIFTY SMALLCAP 50','NIFTY AUTO','NIFTY BANK','NIFTY IT','NIFTY METAL','NIFTY REALTY','NIFTY PHARMA','NIFTY FMCG','NIFTY GROWSECT 15','NIFTY50 VALUE 20','NIFTY GS 10YR']
#index_name=['NIFTY 50','NIFTY MIDCAP 100','NIFTY SMALLCAP 100']
# etf_name=['GOLDBEES','LIQUIDBEES','LICNETFGSC','SETF10GILT','NETFLTGILT']
# sectors = ['NIFTY AUTO','NIFTY BANK','NIFTY IT','NIFTY METAL','NIFTY REALTY','NIFTY PHARMA','NIFTY FMCG']
sectors=['NIFTY REALTY', 'NIFTY INFRA','NIFTY ENERGY','NIFTY FMCG','NIFTY PHARMA','NIFTY BANK','NIFTY AUTO','NIFTY METAL','NIFTY MEDIA','NIFTY IT','NIFTY OIL & GAS']
indexwise_dict={}
# indexwise_dict['nifty50']=nifty50
#indexwise_dict['niftymidcap50']=niftymidcap50
# indexwise_dict['niftymidcap100']=niftymidcap100
#indexwise_dict['niftymidcap150']=niftymidcap150
# indexwise_dict['niftysmallcap100']=niftysmallcap100
#indexwise_dict['etfs']=etf_name
# indexwise_dict['index_name']=index_name

to_date = date.today()- timedelta(days=0)
interval = "day"
from_date=date(2015,1,1)

# for l in indexwise_dict.keys():
#     download_data(indexwise_dict[l], from_date, to_date,interval,True,l)

download_data(sectors, from_date, to_date,interval,True,'SECTORS')



