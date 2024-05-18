"""Risk metrix analysis:
        this projects includes analysis of 5 different riks parameters
        of a portfolio with different assets from separated asset class."""

#importing the required libraries
from datetime import timedelta
import numpy as np
import yfinance as yf
from scipy.stats import norm
import os
import pandas as pd
from scipy.integrate import quad



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
        self.hist_var_n, self.hist_var_ln, self.param_var_n, self.param_var_ln = self.value_at_risk(self.alpha)
        self.hist_es_n, self.hist_es_ln = self.expected_shortfall()
        self.i_tvar_hist_n, self.i_tvar_hist_ln, self.i_tvar_parametric_n, self.i_tvar_parametric_ln = self.tail_value_at_risk_integration()
        self.f_tvar_hist_n, self.f_tvar_hist_ln, self.f_tvar_parametric_n, self.f_tvar_parametric_ln = self.tail_value_at_risk_formula()
        self.stat_n, self.stat_ln = self.summary_stats()

    def assets_data(self):
        """this function extracts the prices of the assets for the last specified
        trading days and the calculates the normal and log-normal returns of each assets
        
        outputs: normal returns of the assets and log-normal returns of the assets"""

        end = self.end
        #if start date is taken 520 ago, the data won't really be 520 days ago as the market is
        #closed in holidays. That's why 1200 days back date was taken as the start date randomly
        #and then last 520 observations were taken separately. 

        random_start_date = (end - timedelta(days=1200)).strftime('%Y-%m-%d')
        prices_all = (yf.Tickers(self.tics).
                   history(start= random_start_date, end=end).resample(str(self.horizon)+'d').
                   last().Close)
        
        prices = abs(prices_all).tail(self.history+1) #here from all observations, last 521 were selected
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
        n_sigma = np.sqrt(np.dot(np.dot(weight,n_cov_mat), np.transpose(weight))) #portfolio volatility was calculated by multiplying weight matrix twice and the covariance matrix
        ln_sigma = np.sqrt(np.dot(np.dot(weight,ln_cov_mat), np.transpose(weight)))
        n_portfolio_return = np.dot(weight, n_avg_ret) #portfolio return was calculated by multiplying the weight and return matrix
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
        #.describe() does not provide skewness and kurtosis, so these two were calculated separately
        summary_stat_n['kurtosis'] = self.daily_n_port_ret.kurtosis()
        summary_stat_n['skewness'] = self.daily_n_port_ret.skew()
        summary_stat_ln = self.daily_ln_port_ret.describe()
        summary_stat_ln['kurtosis'] = self.daily_ln_port_ret.kurtosis()
        summary_stat_ln['skewness'] = self.daily_ln_port_ret.skew()
        return summary_stat_n, summary_stat_ln

    def value_at_risk(self, risk_tolerance):
        """in this function, value at risk of the formed portfolio was calculated from 
        two dimensions: historical and parametric. And these were calculated for both 
         normal and log-normal portfolio returns.
          
         N.B. in this function risk tolerance is taken a separated independent variable though it is 
         stored in _init_ function as alpha; because, for TVaR calculation, this VaR function will be
         integrated in respect to alpha. 
           
        output: normal historical VaR, log-normal historical VaR, 
        normal parametic VaR, and log-normal parametic VaR """
        
        hist_var_n = self.daily_n_port_ret.quantile(q= risk_tolerance, interpolation = 'higher')
        hist_var_ln = self.daily_ln_port_ret.quantile(q= risk_tolerance, interpolation = 'higher')
        var_parametric_n = norm.ppf(risk_tolerance, self.n_portfolio_return, self.n_sigma)
        var_parametric_ln = norm.ppf(risk_tolerance, self.ln_portfolio_ret, self.ln_sigma)
        return hist_var_n, hist_var_ln, var_parametric_n, var_parametric_ln
    
    #Here, Tail VaR was calculated using both integration approach and formula approach

    def tail_value_at_risk_integration(self):
        """In this fuction, tail VaR is calculated. To calculate TVaR here, the integration
         approach was used. here, the formula of var is integrated in respect to the alpha and
          then fird the integrated value of alpha between actual alpha and infinity. and then, the
            integrated value was multiplied by a factor.
              
        output of this function: historical and Parametric TVaR in normal and Log-normal distribution """
        tvar_list = []
        var_list = ['hist normal', 'hist log-normal', 'param normal', 'param log-normal']
        for i in range(0,len(var_list),1):
            result, error = quad(lambda x: self.value_at_risk(x)[i], self.alpha, 1) #quad is used to integrate a function
            tvar = (1/(1-self.alpha))*result
            tvar_list.append(tvar)
        return tvar_list[0], tvar_list[1], tvar_list[2], tvar_list[3]

    def tail_value_at_risk_formula(self):
        """Here again, TVaR was calculated; but here the formula approach was used to calculate the TVaR
        two different formulas were used separately for historical and parametric TVaR.
         
        Output: historical and Parametric TVaR in normal and Log-normal distribution """
        tvar_hist_n = self.daily_n_port_ret[self.daily_n_port_ret<self.hist_var_n].mean()
        tvar_hist_ln = self.daily_ln_port_ret[self.daily_ln_port_ret<self.hist_var_ln].mean()
        tvar_parametric_n = -self.n_portfolio_return - self.n_sigma * norm.pdf(norm.ppf(self.alpha, 0,1), 0, 1)/ (self.alpha)
        tvar_parametric_ln = -self.ln_portfolio_ret - self.ln_sigma * norm.pdf(norm.ppf(self.alpha, 0,1), 0, 1)/ (self.alpha)
        return tvar_hist_n, tvar_hist_ln, tvar_parametric_n, tvar_parametric_ln    
    
    def expected_shortfall(self):
        """Here expected shortfall for the portfolio were calulated both for normal and log-normal
        distribution. And for each case, the greater returns over VaR were taken and then calculated the
        average of those higher returns.
        
        output: Expected shortfalls for normally distributed and log-normally distruted returns of the
        porfolio."""
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
    
    #As we assume that the distribution of the return is continuous and increasing, the CTE and CVAR will
    # be same as TVaR and ES accordingly. So, CTE and CVAR need not to be calculated. However, I calculated
    # here if for testing purpose; but I did not put these two in the main output.  
      
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
        """this function is for combining all risk metrics and printing those in an organised way.
        In the first part of this function, the summary statistics was printed and in the later part
         a dataframe was created to combine all the risk parameters and then the dataframe was printed. """
        
        output = {'Metrix':
                  ['Historical VaR(N)', 'Historical VaR(LN)',
                   'Parametric VaR(N)', 'Parametric VaR(LN)',
                   'Historical TVaR(N)-integration', 'Historical TVaR(LN)-integration', 
                   'Parametric TVaR(N)-integration', 'Parametric TVaR(LN)-integration',
                   'Historical TVaR(N)-formula', 'Historical TVaR(LN)-formula', 
                   'Parametric TVaR(N)-formula', 'Parametric TVaR(LN)-formula',
                   'Historical ES(N)', 'Historical ES(LN)'],
        'rates': [self.hist_var_n, self.hist_var_ln, self.param_var_n, 
                   self.param_var_ln, self.i_tvar_hist_n, self.i_tvar_hist_ln,
                self.i_tvar_parametric_n, self.i_tvar_parametric_ln, self.f_tvar_hist_n, self.f_tvar_hist_ln,
                self.f_tvar_parametric_n, self.f_tvar_parametric_ln, self.hist_es_n, self.hist_es_ln]
        }
        output_df = pd.DataFrame(output)
        output_df['amount'] = round(output_df['rates']*self.capital, 2)
        print("-"*50)
        print(f'all the configuration data: \n'
              f'Portfolio assets: {self.tics} \n'
              f'Number of assets: {len(self.tics)} \n'
              f'Confidence interval: {self.alpha} \n'
              f'Portfolio Size: {self.capital} \n'
              f'trading horizon: {self.horizon} day \n'
              f'Trading date: {self.end} format: YYYY-MM-DD \n'
              f'historical days: {self.history} days \n'
              f'asset weighting: Equal')
        print("-"*50)
        print(f'summary statistics of normal returns \n {self.stat_n}')
        print(f'summary statistics of log-normal returns \n {self.stat_ln}')
        print("-"*50)
        print(f'the risk metrix: \n {output_df}')
