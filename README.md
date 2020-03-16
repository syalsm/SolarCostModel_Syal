# SolarCostModel_Syal
This cost model is used to predict the levelized cost of energy of utility-scale solar PV projects based on a given set of inputs. Additionally, ranges for each input are given in the model to perform a sensitivity analysis. The model architecture is built to support the analysis done in the following paper:

Syal, S. M., and MacDonald, E. F., 2020, "Quantifying the Importance of Solar Soft Costs: A New Method to Apply Sensitivity Analysis to a Value Function," Journal of Mechanical Design (Under Review)

# Model Overview
The model consists of three main python files:
1. main_costmocel_tornadoanalysis.py - this file is the main file to run the analysis and calls the other two python files.
2. mainfunctions.py - this file contains the functions used to do the major calculations used in the main file
3. cashflow.py - this file contains supporting calculations used in both the main file and mainfunctions file

The model also calls two csv files that support depreciation calculations.
1. macrs_halfyear.csv
2. macrs.csv

The model is based on the following sources:

[1] National Renewable Energy Laboratory, 2011, “CREST: Cost of Renewable Energy Spreadsheet Tool,” https://www.nrel.gov/analysis/crest.html.

[2] National Renewable Energy Laboratory, 2020, “System Advisor Model,” https://sam.nrel.gov/

[3] Bolinger, M., Seel, J., and Wu, M., 2016, Maximizing MWh: A Statistical Analysis of the Performance of Utility-Scale Photovoltaic Projects in the United States, Lawrence Berkeley National Laboratory, Berkeley, CA. 
