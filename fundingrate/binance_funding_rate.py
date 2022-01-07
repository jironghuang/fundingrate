import requests
import pandas as pd
import datetime

class funding_binance(object):
    
    # constructor 			  		 			     			  	   		   	  			  	
    def __init__(self, ticker_list):
        
        self.ticker_list = ticker_list
        
        column_names = ["symbol", "fundingTime", "fundingRate"]
        funding_rates_all = pd.DataFrame(columns = column_names)
                
        self.funding_rates_all = funding_rates_all
        
    def get_single_ticker_funding(self, ticker):
        
        URL = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={ticker}"
        r = requests.get(url = URL)
        r_json = r.json()
        funding_rates_df = pd.json_normalize(r_json)
        
        return funding_rates_df
        
    def get_all_ticker_funding(self):
        
        for ticker in self.ticker_list:
            single_ticker_df = self.get_single_ticker_funding(ticker)
            self.funding_rates_all = self.funding_rates_all.append(single_ticker_df)
                
    def format_funding_rates_df(self):
        
        self.funding_rates_all['timestamp'] = (1000*8*60*60+self.funding_rates_all['fundingTime'])/(1000*24*60*60) * 86400.0   
        self.funding_rates_all['effectiveAt'] = self.funding_rates_all['timestamp'].apply(lambda x: datetime.datetime.utcfromtimestamp(x))
        self.funding_rates_all['effectiveAt'] = self.funding_rates_all['effectiveAt'].astype(str)
        
        self.funding_rates_all['date'] = self.funding_rates_all['effectiveAt'].str[:10]
        self.funding_rates_all['date'] = pd.to_datetime(self.funding_rates_all['date'])
        self.funding_rates_all['date'] = self.funding_rates_all['date'].dt.date
        
        self.funding_rates_all['hour'] = self.funding_rates_all['effectiveAt'].str[11:13]    
        self.funding_rates_all['hour'] = self.funding_rates_all['hour'].astype(int)          
        
        #Change column type
        self.funding_rates_all[["fundingRate", "hour"]] = self.funding_rates_all[["fundingRate", "hour"]].apply(pd.to_numeric)
        
        #Select only necessary columns
        self.funding_rates_all = self.funding_rates_all[['symbol', 'fundingRate', 'date', 'hour']]        
        self.funding_rates_all.columns = ['market', 'rate', 'date', 'hour']
        self.funding_rates_all.reset_index()
        
    def get_formatted_funding_rates(self):
        
        self.get_all_ticker_funding() 
        self.format_funding_rates_df()
        
        return self.funding_rates_all        
    
if __name__ == "__main__":   
       
    #Include ticker symbols in config file or database
    binance = funding_binance(['BTCUSDT','ETHUSDT'])    
    binance_rates = binance.get_formatted_funding_rates()    
    print(binance_rates)
    binance_rates.info()    