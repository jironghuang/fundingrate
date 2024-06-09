import requests
import pandas as pd
import datetime

class funding_dydx(object):
    
    # constructor 			  		 			     			  	   		   	  			  	
    def __init__(self, ticker_list, version = 'v3'):
        
        self.ticker_list = ticker_list
        self.version = version
        
        column_names = ["market", "rate", "price", "effectiveAt"]
        funding_rates_all = pd.DataFrame(columns = column_names)
                
        self.funding_rates_all = funding_rates_all
        
    def get_single_ticker_funding(self, ticker):
        
        if self.version == 'v3':        
            URL = f"https://api.dydx.exchange/v3/historical-funding/{ticker}"
            r = requests.get(url = URL)
            r_json = r.json()
            funding_rates_df = pd.json_normalize(r_json, record_path =['historicalFunding'])   #Dictionary path
        elif self.version == 'v4':
            URL = f"https://indexer.dydx.trade/v4/historicalFunding/{ticker}"
            r = requests.get(url = URL)
            r_json = r.json()
            funding_rates_df = pd.json_normalize(r_json, record_path =['historicalFunding'])   #Dictionary path
            
        
        return funding_rates_df
        
    def get_all_ticker_funding(self):
        
        for ticker in self.ticker_list:
            single_ticker_df = self.get_single_ticker_funding(ticker)
            single_ticker_df['market'] = ticker
            
            self.funding_rates_all = self.funding_rates_all.append(single_ticker_df)
                
    def format_funding_rates_df(self):
        
        self.funding_rates_all['effectiveAt'] = self.funding_rates_all['effectiveAt'].astype(str)
        
        self.funding_rates_all['date'] = self.funding_rates_all['effectiveAt'].str[:10]
        self.funding_rates_all['date'] = pd.to_datetime(self.funding_rates_all['date'])
        self.funding_rates_all['date'] = self.funding_rates_all['date'].dt.date
        
        self.funding_rates_all['hour'] = self.funding_rates_all['effectiveAt'].str[11:13]    
        self.funding_rates_all['hour'] = self.funding_rates_all['hour'].astype(int)   
        
        #Change column type
        self.funding_rates_all[["rate", "price", "hour"]] = self.funding_rates_all[["rate", "price", "hour"]].apply(pd.to_numeric)
        
        #Select only necessary columns
        self.funding_rates_all = self.funding_rates_all[['market', 'rate', 'price', 'date', 'hour']]
        self.funding_rates_all.reset_index()
        
    def get_formatted_funding_rates(self):
        
        self.get_all_ticker_funding() 
        self.format_funding_rates_df()
        
        return self.funding_rates_all
    
    
if __name__ == "__main__":    
    
    #For dydx v3
    dydx = funding_dydx(['BTC-USD','ETH-USD','SOL-USD'], version = 'v3')    
    dydx_rates = dydx.get_formatted_funding_rates()    
    dydx_rates.info()

    #For dydx v4
    dydx = funding_dydx(['BTC-USD','ETH-USD','SOL-USD'], version = 'v4')    
    dydx_rates = dydx.get_formatted_funding_rates()    
    dydx_rates.info()  
    
    
    
    
    
    
    
    
    
        
