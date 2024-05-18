"""Technical analysis backtesting:
     two tools were taken to test the efficacy of the two tools
      whether they can generate positive portfolio returns over the time
       again and again by changing the weights and decision in every rebalacing dates.
        In taking the decison Pandas_ta has been used.  """

# Importing libraries
from datetime import timedelta, datetime
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_ta as ta

#inputs (the first date and the assets)
backtesting_start_date = '2023-09-01'

ticker_symbols = [
    "NWL",  # Newell Brands Inc. (stock)
    "IBRX",  # ImmunityBio, Inc. (stock)
    "BAC",  #Bank of America Corporation (Stock)
    "ASC",  # Ardomore Shipping Corporaation (stock)
    "ARKK",  # ARK Innovation ETF (ETF)
    "NFLX",  # Netflix, Inc. (stock)
]

#the class is taken to calculate the portfolio returns and the graph
class TechnicalAnalysis:
    """technical analysis class.
    this class includes five different functions which are: the _init_ function which 
     takes the inputs of the whole class and the outputs of the other functions; bbands function
      is for calculating the decision of the all portfolio assets for buy or sell for each day 
       of the rebalancing dates in bollinger bands; macd function is also same as bbands function
        but here the decisions are based on moving average convergence and divergence; portfolio
         function is for creating the portfolio on each each day based on the decision and portfolio
          graph function is to calculate the cumulative returns and the graph. """

    def __init__(self, ticker_list, date):
        """initial function:
        this function takes the external inputs as the input of the functions of the whole class
         and takes the outputs of internal functions as the inputs of the other functions. 
           The external inputs are starting backtest date and the list of the assets.
           and the internal inputs are the outputs of bollinger bands output, macd outputs and
           portfolio function's output."""
        self.assets = ticker_list
        self.trade_date = datetime.strptime(date, "%Y-%m-%d")
        self.bollinger_decision, self.rebalances = self.bollinger_bands()
        self.macd_decision = self.macd()

    def bollinger_bands(self):
        """calculation of bollinger bands:
        this function takes the date and the assets as its inputs and calculate the 
        rebalancing dates first and then the decision for asset on each rebalacing date.
        Here, rebalacing is done in each 5 days interval
        So, the outputs are 1) rebalancing dates 2) decision on each ticker of each day"""
        day1 = self.trade_date
        today = datetime.today()
        days_between = (today - day1).days
        rebalancing_dates = []
        for i in range(0, days_between, 5):
            reb_days = day1 + timedelta(days=i)
            rebalancing_dates.append(reb_days)

        decision = []
        for j in rebalancing_dates:
            for ticker in self.assets:
                random_start_date = (j - timedelta(days=70)).strftime('%Y-%m-%d')
                data = yf.Ticker(ticker).history(start=random_start_date, end=j)
                data = data.tail(30)
                bands = ta.bbands(data.Close)
                percentage = bands['BBP_5_2.0']
                ten_avg = percentage.tail(10).mean()
                five_avg = percentage.tail(5).mean()
                last_day = percentage[-1].item()
                three_avg = percentage.tail(3).mean()
                #the decision is taken by comparing 4 different days values
                if last_day < 0.5 and five_avg < 0.5 and ten_avg < 0.5:
                    decision.append([j, ticker, 'buy'])
                elif last_day < 0.5 and five_avg > 0.5 and ten_avg > 0.5:
                    decision.append([j, ticker, 'sell'])
                elif last_day < 0.5 and five_avg < 0.5 and ten_avg > 0.5:
                    decision.append([j, ticker, 'buy'])
                elif last_day > 0.5 and five_avg < 0.5 and ten_avg < 0.5:
                    decision.append([j, ticker, 'buy'])
                elif last_day > 0.5 and five_avg < 0.5 and ten_avg > 0.5:
                    decision.append([j, ticker, 'sell'])
                elif last_day > 0.5 and five_avg > 0.5 and ten_avg > 0.5:
                    decision.append([j, ticker, 'sell'])
                elif last_day < 0.5 and five_avg > 0.5 and ten_avg < 0.5:
                    if three_avg > 0.5:
                        decision.append([j, ticker, 'sell'])
                    else:
                        decision.append([j, ticker, 'buy'])
                elif last_day > 0.5 and five_avg < 0.5 and ten_avg > 0.5:
                    if three_avg > 0.5:
                        decision.append([j, ticker, 'sell'])
                    else:
                        decision.append([j, ticker, 'buy'])
        return decision, rebalancing_dates

    def macd(self):
        """moving average convergence and divergence:
         this function is also calcukating the decision of each ticker on each 
          rebalcing date using moving average convergence and divergence method. 
            So, the output of this function is also the decision by this MACD method."""
        decision = []
        for j in self.rebalances:
            for ticker in self.assets:
                random_start_date = (j - timedelta(days=70)).strftime('%Y-%m-%d')
                data = yf.Ticker(ticker).history(start=random_start_date, end=j)
                macd = data.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)
                macd_hist = macd['MACDh_12_26_9']
                ten_avg = macd_hist.tail(10).mean()
                five_avg = macd_hist.tail(5).mean()
                last_day = macd_hist[-1].item()
                three_avg = macd_hist.tail(3).mean()
                #here also five different days values were used to take a decision
                if last_day > 0 and five_avg > 0 and ten_avg > 0:
                    decision.append([j, ticker, 'buy'])
                elif last_day > 0 and five_avg > 0 and ten_avg < 0:
                    decision.append([j, ticker, 'buy'])
                elif last_day > 0 and five_avg < 0 and ten_avg < 0:
                    decision.append([j, ticker, 'sell'])
                elif last_day < 0 and five_avg < 0 and ten_avg < 0:
                    decision.append([j, ticker, 'sell'])
                elif last_day < 0 and five_avg < 0 and ten_avg > 0:
                    decision.append([j, ticker, 'sell'])
                elif last_day < 0 and five_avg > 0 and ten_avg > 0:
                    decision.append([j, ticker, 'buy'])
                elif last_day > 0 and five_avg < 0 and ten_avg > 0:
                    if three_avg > 0:
                        decision.append([j, ticker, 'buy'])
                    else:
                        decision.append([j, ticker, 'sell'])
                elif last_day < 0 and five_avg > 0 and ten_avg < 0:
                    if three_avg > 0:
                        decision.append([j, ticker, 'buy'])
                    else:
                        decision.append([j, ticker, 'sell'])
        return decision

    def portfolio(self, decision):
        """portfolio function:
        this function is to form the portfolio on each rebalcing day.

        N.B: both long and short strategies are used combined to form a portfolio.
        and for the portfolio return the mean of short return is subtracted from the mean
        of long return to find the adjusted total portfolio return. 
        
        the output of this function is the combined portfolio on each rebalancing date."""
        decision_df = pd.DataFrame(decision, columns=['date', 'ticker', 'decision'])
        grouped = decision_df.groupby('date')
        decision_df_by_date = {}
        for date, group in grouped:
            decision_df_by_date[date] = group.drop(columns=['date']).reset_index(drop=True)

        portfolio = []
        for i in self.rebalances:
            each_day_df = decision_df_by_date[i]
            decison_list_each_day = each_day_df['decision'].to_list()
            decision_tic_each_day = each_day_df['ticker'].to_list() #to keep tickers balanced
            returns = (yf.Tickers(decision_tic_each_day).
                       history(start=i, end=i + timedelta(days=5)).
                       Close.pct_change().dropna())
            mean_ret = returns.mean()
            combined_df = pd.DataFrame({'ticker': decision_tic_each_day,
                        'returns': mean_ret.values,
                        'decision': decison_list_each_day})
            combined_df['adjusted_return'] = (np.where
                                              (combined_df['decision']=='sell',
                                               combined_df['returns']*-1,combined_df['returns']))
            daily_portfolio_returns = combined_df['adjusted_return'].mean()
            portfolio.append([i, daily_portfolio_returns])
        return portfolio, decision_df_by_date

    def portfolio_returns_and_graph(self, portfolio_returns, tool_name):
        """the cumulative portfolio return and the graph over time were calculated here in this 
        function. This function takes the output of the portfolio function as its input and then
        split the portfolios according to days and calculte the cumulative returns and the time
        series pirtfolio return graph to compare the tools."""
        portfolio_returns = pd.DataFrame(portfolio_returns, columns=['date', 'returns'])
        cumulative_portfolio_ret = (portfolio_returns['returns'] + 1).prod() - 1
        plt.plot(portfolio_returns['date'], portfolio_returns['returns'], color='red')
        plt.title(f'portfolio returns in {tool_name}')
        plt.ylabel('portfolio returns')
        plt.xlabel('dates')
        plt.xticks(rotation=45)
        plt.grid()
        plt.show()
        return cumulative_portfolio_ret, portfolio_returns

    def main(self):
        """main function:
        this function generally combines all the functions in one single function
        and put the internal inputs to the other functions."""
        bbands_portfolio = self.bollinger_decision
        macd_portfolio = self.macd_decision
        bbands_port_returns, daily_bbands_decision = self.portfolio(bbands_portfolio)
        macd_port_returns, daily_macd_decision = self.portfolio(macd_portfolio)
        cumulative_bbands_rp, bbands_daily_portfolio = self.portfolio_returns_and_graph(bbands_port_returns,'Bollinger Bands')
        cumulative_macd_rp, macd_daily_portfolio = self.portfolio_returns_and_graph(macd_port_returns, 'Moving Average Convergence/Divergence')

        print('configurations:')
        print(f'the assets: {self.assets}')
        print(f'first date of backtesting: {self.trade_date} and the last date: {datetime.today()}')
        print('strategy: long-short both strategy: short sell is allowed')
        print('rebalancing in every 5 days')
        print(50*'-')
        print('output1: Bollinger Bands')
        print('daily portfolio decision by each asset using bollinger bands')
        print(daily_bbands_decision)
        print('portfolio returns in every rebalacing date by bollinger bands: ')
        print(bbands_daily_portfolio)
        print(f'Cumulative Portfolio returns in Bollinger Bands: {cumulative_bbands_rp * 100:.2f}%')
        print(50*'-')
        print('output2: Moving Average Convergence/Divergences')
        print('daily portfolio decision by each asset using Moving Average Convergence/Divergences')
        print(daily_macd_decision)
        print('portfolio returns in every rebalacing date by Moving Average Convergence/Divergences: ')
        print(macd_daily_portfolio)
        print(f'Cumulative Portfolio returns in Moving Average Convergence/Divergence: {cumulative_macd_rp * 100:.2f}%')       
        tools = ['Bollinger Bands', 'Moving Average Convergence/Divergence']
        cumulative_returns = [cumulative_bbands_rp, cumulative_macd_rp]
        comparison = pd.DataFrame({'Tool Name':tools, 
                                   'Cumulative Return': cumulative_returns})
        comparison['Result'] = np.where(comparison['Cumulative Return']>0, 'Effective', 'Not Effective')
        print(50*'-')
        print('output3: Comparison')
        print('comparison:')
        print(comparison)
        

# running the class
my_technical_analysis = TechnicalAnalysis(ticker_symbols, backtesting_start_date)
my_technical_analysis.main()
