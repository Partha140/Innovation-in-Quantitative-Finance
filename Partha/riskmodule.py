"""Risk metrix analysis:
        this projects includes analysis of 5 different riks parameters
        of a portfolio with different assets from separated asset class."""

#importing the required libraries
from datetime import datetime, timedelta
import numpy as np
import yfinance as yf
from scipy.stats import norm
import os
import pandas as pd


#Test libyaml vs pyyaml, default to pyyaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
    print("Using libyaml")
except ImportError:
    print("Using pyyaml")
    from yaml import Loader, Dumper

#created a class for the whole analysis of the risk
class RiskAnalysis:
    """a class with various function including price extraction of the assets,
    portfolio formation and historical performance, then summary statistics of the 
    formed portfolio, then using these portfolio data VaR, TVaR, ES were calculated for both 
    normal and log-normal returns of the portfolio."""

    def __init__(self, configuration_file_directory, configuration_file_name):
        """this function accumulates all the inputs
        for this project the external inputs are mainly the configuration file 
         directory and the name of the configuration file.
          
           Besides these two external inputs, all the outputs of the internal functions are taken
            as inputs in this function; because often time the output of one function becomes the
             input of another function. For example: the output of the function of extracting asset 
              price is the input of the function of portfolio performance. """
        
        self.cwd = configuration_file_directory
        self.filename = configuration_file_name
        stream = open(os.path.join(self.cwd,self.filename))
        data = load(stream, Loader=Loader)
        dump(data)
        self.alpha = data['Risk tolerance']
        tickers_dict = data['Tickers']
        self.tics = [ticker for d in tickers_dict for ticker_list in d.values() for ticker in ticker_list]
        self.end = data['Seed']
        self.capital = data['Capital']
        self.history = data['Historical days']
        self.horizon = data['Holding period']
        self.normal_return, self.log_returns = self.assets_data()
        self.n_portfolio_return, self.ln_portfolio_ret, self.n_sigma, self.ln_sigma, self.daily_n_port_ret, self.daily_ln_port_ret = self.portfolio_risk_return()
        self.hist_var_n, self.hist_var_ln, self.param_var_n, self.param_var_ln = self.value_at_risk()
        self.hist_es_n, self.hist_es_ln = self.expected_shortfall()
        self.tvar_hist_n, self.tvar_hist_ln, self.tvar_parametric_n, self.tvar_parametric_ln = self.tail_value_at_risk()
        self.stat_n, self.stat_ln = self.summary_stats()

    def assets_data(self):
        """this function extracts the prices of the assets for the last specified
        trading days and the calculates the normal and log-normal returns of each assets
        
        outputs: normal returns of the assets and log-normal returns of the assets"""

        end = self.end
        end2 = (end - timedelta(days=1)).strftime('%Y-%m-%d')
        end3 = (end - timedelta(days=2)).strftime('%Y-%m-%d')
        thousand_days_back = (end - timedelta(days=1000)).strftime('%Y-%m-%d')
        prices_all = (yf.Tickers(self.tics).
                   history(start= thousand_days_back, end=end).resample(str(self.horizon)+'d').
                   last().Close)
        try:
            index = prices_all.index.get_loc(end)
        except KeyError:
            try:
                index = prices_all.index.get_loc(end2)
            except KeyError:
                try:
                    index = prices_all.index.get_loc(end3)
                except KeyError:
                    print('no date')
        
        prices = abs(prices_all[index-self.history-1:index])

        normal_return = prices.pct_change().dropna()
        log_returns = (np.log(prices)).diff().dropna()
        return normal_return, log_returns
    
    def portfolio_risk_return(self):
        """This function calculates all the historical performance of the formed portfolio
         where the implicit assumption of the portfolio was the weights of the assets are equal.
          
          the ouputs: normal average portfolio returns, log normal average portfolio returns,
           normal volatility, log-normal volatility, daily normal portfolio returns and daily
            log-normal portfolio returns """
        
        weight = np.repeat(1/len(self.tics), len(self.tics))
        n_avg_ret = self.normal_return.mean()
        ln_avg_ret = self.log_returns.mean()
        n_cov_mat = self.normal_return.cov()
        ln_cov_mat = self.log_returns.cov()
        n_sigma = np.sqrt(np.dot(np.dot(weight,n_cov_mat), np.transpose(weight)))
        ln_sigma = np.sqrt(np.dot(np.dot(weight,ln_cov_mat), np.transpose(weight)))
        n_portfolio_return = np.dot(weight, n_avg_ret)
        ln_portfolio_ret = np.dot(weight, ln_avg_ret) # daily portfolio return is needed
        daily_n_port_ret = self.normal_return*weight
        daily_n_port_ret = daily_n_port_ret.sum(axis=1)
        daily_ln_port_ret = self.log_returns*weight
        daily_ln_port_ret = daily_ln_port_ret.sum(axis=1)
        return n_portfolio_return, ln_portfolio_ret, n_sigma, ln_sigma, daily_n_port_ret, daily_ln_port_ret
    
    
    def summary_stats(self):
        """this function is to find the related statistics of the portfolio, which provides
        minimum, maximum, average, top and bottom quartile, median, skewness and kurtosis."""

        summary_stat_n = self.daily_n_port_ret.describe()
        summary_stat_n['kurtosis'] = self.daily_n_port_ret.kurtosis()
        summary_stat_n['skewness'] = self.daily_n_port_ret.skew()
        summary_stat_ln = self.daily_ln_port_ret.describe()
        summary_stat_ln['kurtosis'] = self.daily_ln_port_ret.kurtosis()
        summary_stat_ln['skewness'] = self.daily_ln_port_ret.skew()
        return summary_stat_n, summary_stat_ln

    def value_at_risk(self):
        """in this function, value at risk of the formed portfolio was calculated from 
        two dimensions: historical and parametric. And these were calculated for both 
         normal and log-normal portfolio returns.
          
           output: normal historical VaR, log-normal historical VaR, 
           normal parametic VaR, and log-normal parametic VaR """
        
        hist_var_n = self.daily_n_port_ret.quantile(q= self.alpha, interpolation = 'higher')
        hist_var_ln = self.daily_ln_port_ret.quantile(q= self.alpha, interpolation = 'higher')
        var_parametric_n = norm.ppf(self.alpha, self.n_portfolio_return, self.n_sigma)
        var_parametric_ln = norm.ppf(self.alpha, self.ln_portfolio_ret, self.ln_sigma)
        return hist_var_n, hist_var_ln, var_parametric_n, var_parametric_ln
    
    #self.n_portfolio_return, self.ln_portfolio_ret, self.n_sigma, self.ln_sigma, self.daily_n_port_ret, self.daily_ln_port_ret
    def tail_value_at_risk(self):
        """Calculating Tail Value at Risk"""
        tvar_hist_n = self.daily_n_port_ret[self.daily_n_port_ret<self.hist_var_n].mean()
        tvar_hist_ln = self.daily_ln_port_ret[self.daily_ln_port_ret<self.hist_var_ln].mean()
        tvar_parametric_n = -self.n_portfolio_return - self.n_sigma * norm.pdf(norm.ppf(self.alpha, 0,1), 0, 1)/ (self.alpha)
        tvar_parametric_ln = -self.ln_portfolio_ret - self.ln_sigma * norm.pdf(norm.ppf(self.alpha, 0,1), 0, 1)/ (self.alpha)
        return tvar_hist_n, tvar_hist_ln, tvar_parametric_n, tvar_parametric_ln
    
    def expected_shortfall(self):
        """calculating expected Shortfall"""
        n_shortfall = []
        for i in range(0,len(self.daily_n_port_ret),1):
            if self.daily_n_port_ret[i] - self.hist_var_n>=0:
                n_shortfall.append(self.daily_n_port_ret[i])
        h_es_n = np.mean(n_shortfall)

        ln_shortfall = []
        for i in range(0, len(self.daily_ln_port_ret),1):
            if self.daily_ln_port_ret[i] - self.hist_var_ln>= 0:
                ln_shortfall.append(self.daily_ln_port_ret[i])
        h_es_ln = np.mean(ln_shortfall)
        return h_es_n, h_es_ln
    
    def conditional_tail_expectation(self):
        """calculating coditional tail expectation"""
        cte_n = self.hist_var_n + (1/(1-self.alpha))*self.hist_es_n
        cte_ln = self.hist_var_ln + (1/(1-self.alpha))*self.hist_es_ln
        return cte_n, cte_ln
    
    def conditional_value_at_risk(self):
        """calculating conditional value at risk"""
        cvar_n = self.hist_es_n/(1-self.alpha)
        cvar_ln = self.hist_es_ln/(1-self.alpha)
        return cvar_n, cvar_ln
    
    
    def main(self):
        """combining all risk metrics"""
        output = {'Metrix':
                  ['Historical VaR(N)', 'Historical VaR(LN)',
                   'Parametric VaR(N)', 'Parametric VaR(LN)',
                   'Historical TVaR(N)', 'Historical TVaR(LN)', 
                   'Parametric TVaR(N)', 'Parametric TVaR(LN)',
                   'Historical ES(N)', 'Historical ES(LN)'],
        'rates': [self.hist_var_n, self.hist_var_ln, self.param_var_n, 
                   self.param_var_ln, self.tvar_hist_n, self.tvar_hist_ln,
                self.tvar_parametric_n, self.tvar_parametric_ln, self.hist_es_n, self.hist_es_ln],
        }
        output_df = pd.DataFrame(output)
        output_df['amount'] = output_df['rates']*self.capital
        print(f'summary statistics of normal returns \n {self.stat_n}')
        print(f'summary statistics of log-normal returns \n {self.stat_ln}')
        print(f'the risk metrix: \n {output_df}')



#### an example: for project I will import the input data later
        
