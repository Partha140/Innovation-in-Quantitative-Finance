**Risk Metrix Analysis of Portfolio**

This analysis includes calculating various risk metrix with historical performance of the portfolio. 

---

## The Contents

This includes the steps of this analysis

1. Creating project flowchart.
2. Setting the assumptions. 
3. Selecting the inputs and creating the configuration file.
4. Creating a proof of concept file.
5. Constructing a risk module
6. Calculating the risk metrix
7. Testing the reliability of the output
8. Storing the output
9. References

---

## 1. Creating project flowchart

In this flowchart, the plans and chronology of the whole analysis were set, which starts from setting the assumptions and inputs to the warehouse of the output. The flowchart is in this directory: **"D:/academy/spring24/innovation/projectIOF2024/Partha/FLOW CHART (Partha_Pratim_Roy).pdf"**

---

## 2. Setting the assumptions

To form the portfolio and analyze the risks of this portfolio, some assumptions have been set. These are:

a. The assets returns are both normally and log-normally distributed.
b. The returns' distribution is continuous and increasing.
c. All assets are equally weighted so that there is no need to rebalance.

---

## 3. Selecting the inputs and creating the configuration file.

For this analysis, I have to take some inputs like: date or end date, capital amount, tickers with the asset class, risk tolerance etc. I put all the inputs in the configuration file. Find my configuration file in: **"D:\academy\spring24\innovation\projectIOF2024\Partha\configuration.yaml"**

---

## 4. Creating a proof of concept file.

Proof of concept was done to test the accuracy of the risk metrix in a different file with the tickers or some of the tickers (at least 2 tickers.). I did this PoC in a Microsoft Excel file. Find my PoC file: **"D:\academy\spring24\innovation\projectIOF2024\Partha\POC.xlsx"**

---

## 5. Constructing a risk module

Here a comprehensive risk analysis module was created so that any portfolio having equal weights can be analysed in terms of its risk behavior. This module was done through a class function of python with various function including price extraction of the assets, portfolio formation and historical performance, then summary statistics of the formed portfolio, then using these portfolio data, VaR, TVaR, ES were calculated for both normal and log-normal returns of the portfolio. The risk module file: **"D:\academy\spring24\innovation\projectIOF2024\Partha\pycode_Partha\riskmodule.py"**

---

## 6. Calculating the risk metrix

After completing the risk module python file, I just took the directory of the configuration file (inputs file) as and the name of the configuration file as the inputs of the class; and the class function automatically calculated the summary statistics of the portfolio returns and the risk metrics (VaR, TVaR, ES) as both percentage figure and amount in dollar. However, the codes for running the risk module file was done in a separated file called main file. The main file is:
**"D:\academy\spring24\innovation\projectIOF2024\Partha\pycode_Partha\main.py"**

---

## 7. Testing the reliability of the output

There are two different approaches to identify whether the module is providing the reliable and consistent result over time. Firstly, in the risk module, there are functions for CTE and CVaR which will be almost closer to the TVaR and ES. I tested these two outputs by changing assets in the portfolio and in everytime, these two are consistent. Secondly, I checked the risk matrics with the data of proof of concept file and the outputs are almost same. 

---

## 8. Storing the output

After completing the analysis, the output is stored in a separated text file. Besides, the risk module python file includes a print function where all the matrix were kept as a dataframe. The output text file is:
**"D:\academy\spring24\innovation\projectIOF2024\Partha\output.txt"**

---

## 9. References

1. Acerbi, C. (2002).
Spectral measures of risk: A coherent representation of subjective risk
aversion.
Journal of Banking and Finance.

2. Belles-Sampera, J., Montserrat, G., and Santolino, M. (2018).
Risk quantification and allocation methods for practitioners.
Amsterdam University Press.

3. Cont, R., Deguest, R., and Scandolo, G. (2010).
Robustness and sensitivity analysis of risk measurement procedures.
Quantitative Finance

4. Rockafellar, T. R. and Uryasev, S. (2002).
Conditional value-at-risk for general loss distributions.
Journal of Banking and Finance.