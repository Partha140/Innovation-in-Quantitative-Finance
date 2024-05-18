"""running the risk metrics class in a different directory with the inputs of the
configuration file related to the formed portfolio"""

import sys

#here the directory where the python file of the class is formed- the directory of the risk module
sys.path.append("D:\\academy\\spring24\\innovation\\projectIOF2024\\Partha\\pycode_Partha")

#importing the class of the risk analysis from the file of the above directory
from riskmodule import RiskAnalysis

#directory of the configuration file- the directory of the configuration file
PATH = "D:\\academy\\spring24\\innovation\\projectIOF2024\\Partha"

#the name of the configuration file
THE_FILE = 'configuration.yaml'

#Calling the class with the external inputs: directory and file name of the configuration file
my_risk_data = RiskAnalysis(PATH, THE_FILE)

#run the main function: the summary function of the class
my_risk_data.main()