'''
File Name: main__costmodel_tornadoanalysis.py
Owner: Sita Syal
Last updated: Jan 6, 2020
Description: This model is based on the NREL CREST model to determine real LCOE for
a solar PV project. The LCOE equation comes from the SAM model. The output of this model is
just one LCOE value based on the inputs chosen. Ranges used in the paper analysis
for the tornado diagram are included in comments by each input used.

Assumptions

All cost values are converted to 2018 dollars
Assume technology is "Photovoltaic"
No State Rebates, Tax Credits, and/or REC Revenue, only Federal ITCs
Assume owner is a taxable entity
Federal grants Treated as Taxable Income: YES
Assume no decommissioning reserves (this funding comes from operations)
Reserve Requirement = $0
Assume Bonus Depreciation
Assume technology is "tracking"

'''

import numpy as np
import pandas as pd
import time
import csv
import cashflow
import mainfunctions


def main():


	#_______________________FIXED INPUTS________________________________________

	# Project Size and Performance__________________

	#************Input: Generatory Nameplate Capacity************
	# Units: kWdc
	genNPC = 100000
	#***********************************************************

	#************Input: Net Capacity Factor************
	# Units: percentage
	# Source: Bolinger, Seel, and Wu, 2015: statistical model for understanding 
	# variability of utiltiy-scale PV project performance (NCF)
	b1 = 0.0478
	b2 = 0.0429
	b3 = 0.2391
	b0 = 0.2328

	GHI = 5.55 # 4.8-6.3 #5.39 is the value for Bakersfield, according to NREl, this can vary from 6.3 to 3.8 for CA
	meanGHI = 5.52 #Mean GHI in California
	tracking = 1 #Can be 1 or 0, Assume Tracking
	ILR = 1.28 # 1.22-1.34 # Median as per EPA data, this can vary!! From 1.25 to 1.37
	meanILR = 1.26 #From California Data


	netCapFac = b1*(GHI-meanGHI) + b2*(tracking) + b3*(np.log(ILR)-np.log(meanILR)) + b0
	print ("Net Capacity Factor is: ", netCapFac)


	#--------------Calculation: Production in Year 1---------
	# Units: kW
	ProdYr1 = genNPC*netCapFac*8760 #8760=number of hours in a year
	# print('Year 1 production is ', ProdYr1)
	#--------------------------------------------------------

	#************Input: Project Degredation************
	# Units: percentage (between 0.25% and 1%)
	ProjDeg = 0.00625 # can vary from 0.25% to 1.0%
	print("Project Degredation is: ", ProjDeg)
	#**************************************************

	#************Input: Useful Life*********************
	# Units: years
	UseLife = 30
	#***************************************************

	#________________________Capital Costs______________________
	# Assume "Intermediate" level

	#************Input: Generation Eqiupment Cost************
	# Cost of module
	# Units: $/Wdc
	# This value can range:
	# Fu et al, 2015: 0.69 $/Wdc (2018 dollars)
	modulecost = 0.58 # 0.47-0.69 # 2018 dollars
	module = modulecost*genNPC*1000

	# Cost of inverter
	# Units: $/Wdc
	# This value can range:
	# NREL cost benchmark 2018: $0.05/Wdc, 2018 dollars
	# Fu et al, 2015: $0.12/Wdc, 2018 dollars
	invertercost = 0.085 #0.05-0.12 #2018 dollars
	inverter = invertercost*genNPC*1000

	# Units: $
	GenEqCost = module + inverter
	print('Generation Equipment Cost: ', GenEqCost)
	#***********************************************************

	#************Input: Balance of Plant************
	# Units: $
	# Includes mounting devices, electrical infrastructure

	# Mounting Devices
	# Fu et al, 2015: 0.17 2018 $/Wdc
	# Range from 2018 NREL cost benchmark: $0.1 - 0.21 / Wdc, 2018 dollars
	Mountcost = 0.155 # $2018 / Wdc
	Mount = Mountcost*genNPC*1000

	# Electrical Infrastructure
	# Wires/conduits
	WiresCondcost = 0.17 # $2018 / Wdc, source: Fu et al 2015
	WiresCond = WiresCondcost*genNPC*1000
	# Transmision
	# Source: Fu et al 2015. Also ranges $0.01-0.03/Wdc as per NREL 2018 cost benchmark
	Transmissioncost = 0.02 # $2018/Wdc
	Transmission = Transmissioncost*genNPC*1000

	BOPCost = Mount + WiresCond + Transmission
	print('Balance of Plant Cost, ', BOPCost)
	#***********************************************************

	#************Input: Interconnection************
	# Units: $
	# Bird et al 2018 gives data for interconnection studies
	# Limitation: The size of these projects are small (100 kW - 20 MW)
	# Ranges from 0.0161 - 0.9972 USD/W
	Intercon = 0.50665 # $/Wdc, 2018 dollars

	InterconCost = Intercon*genNPC*1000
	print('Interconnection Cost: ', InterconCost)
	#***********************************************************

	#************Input: Development Cost and Fees************
	# Units: $
	# Development Cost and Fees is made up of the following:

	# Permitting
	# Source: Fu et al, 2015
	# In California, they said permitting ranges $200,000-$1,000,000, assumed $500,000, 2015 dollars
	# ($211889 - $1059447, assumed $529723, in 2018 dollars)
	Permit = 529723 # $ 2018

	# Land Acquisition
	# Source: Fu et al, 2015
	# Only one value reported
	LandAcCost = 0.03 #$/Wdc, 2018 dollars
	LandAc = LandAcCost*genNPC*1000

	# Labor and construction Equipment, can vary based on union or nonunion
	# Source: Fu et al, 2015 range 0.35-0.38 for nonunion/union
	LaborConstcost = 0.365 #2018 $/Wdc, Unionized labor and equipment for 100 MW (note: $0.35/Wdc for nonunionized)
	LaborConst = LaborConstcost*genNPC*1000

	# EPC Overhead
	# Markup of equipment (EPC costs + Generation Equipment cost + Mouting cost + Wires cost)
	# Source: NREL cost benchmark, 2018
	# Range given for low and high, 8.67% - 13% on equipment and material (excpet transmission line)
	EPCoverheadperc = 0.10835

	DevCFCost = Permit + LandAc + LaborConst+ EPCoverheadperc*(Permit+LandAc+GenEqCost+Mount+WiresCond)

	# EPC Profit 
	# Markup on percentage of equipment, labor, and development costs
	# Range 5% - 8%
	# Source: NREL cost benchmark, 2018
	EPCprofitperc = 0.065
	
	DevCFCost = DevCFCost + EPCprofitperc*(GenEqCost+Mount+WiresCond+DevCFCost)

	# Contingency 
	# Markup on all EPC costs and construction costs
	# Source: Fu et al, 2015 and NREL cost benchmark, 2018
	# 3-4% of all development and construction costs
	Contingency = 0.035

	DevCFCost = DevCFCost + Contingency*(DevCFCost)

	# Developer Overhead
	# Markup on development costs
	# Source: NREL cost benchmark, 2018
	# Range 2-12% (they assume 2% for 100 MW)
	DevOverheadperc = 0.07

	DevCFCost = DevCFCost + DevOverheadperc*DevCFCost
	print("Development Cost and Fees (soft costs): ", DevCFCost)
	#***********************************************************

	
	#________________________Operations and Maintenance______________________

	#************Input: Fixed O&M Expense Yr 1************
	# Units: $/kWdc-yr
	# Sources: NREL cost benchmark, 2018; Bolinger & Seel, 2018; EIA capital costs, 2016
	# Range, all converted to 2018 dollars: [10.40, 14.64, 21.20, 28.48, 30.85]
	FixedOandM = 20.625
	print("Fixed O&M Costs: ", FixedOandM)
	#***********************************************************

	#************Input: Variable O&M Expense Yr 1************
	# Units: cents/kWh dc
	VarOandM = 0
	#***********************************************************

	#************Input: O&M Cost Inflation, initial period************
	# Units: %
	OMcostinfl = 0.016
	#***********************************************************

	#************Input: Initial Period ends last day of:************
	# Units: year
	LastDay = 10
	#***********************************************************

	#************Input: O&M Cost Inflation, thereafter************
	# Units: %
	OMcostinflafter = 0.016
	#***********************************************************

	#************Input: Insurance, Year 1 (% of total cost)************
	# Units: %
	Insuryr1perc = 0.004
	#***********************************************************

	#************Input: Project Management************
	# Units: $/yr
	ProjMan = 0
	#**************************************************

	#************Input: Property Tax or PILOT, Yr1************
	# Units: $/yr
	PILOT = 28000
	#**************************************************
	
	#************Input: Annual Property Tax Adjustment Factor************
	# Units: %
	PropTaxAd = -0.1
	#**************************************************

	#************Input: Land Lease************
	# Units: $/yr
	# Source: Ong et al, 2013
	# Found data on land acres / MWdc for California projects >= 50 MW
	# Includes tracking, fixed, and unknown
	# See excel sheet - the distribution looks slightly skewed normal
	# Assume $1000/acre/year for average California SJV in 2018 dollars

	# Land data from Ong et al, 2013 is approximately normally distributed
	# Units: acre / MWdc
	# For normal: mu = 7.92, sigma = 4.24, lower, upper = 0, 14 truncate for realistic values
	acresperMW = 8.705 #4.29-13.12
	# print(acresperMW)

	# Average rate, $/acre/year
	# Source: Solar Strategic Group, $1000-$2000
	rate = 1500
	# print(rate)

	# Units: 2018 $/year
	LandLease = (genNPC/1000) * acresperMW * rate
	print('Land Lease: ', LandLease)
	#**************************************************
	

	#************Input: Royalties (% of revenue)************
	# Units: %
	Royal = 0.03
	#**************************************************

	#________________________Construction Financing______________________

	#************Input: Construction Period************
	# Units: months
	ConstPeriod = 6
	#***********************************************************

	#************Input: Interest Rate Annual************
	# Units: %
	IntRateAnnual = 0.04
	#***********************************************************
	

	#________________________Permanent  Financing______________________
	#************Input: % Debt % of hard costs) Mortgage-style amort.************
	# Units: %
	# Source: Feldman and Schwabe, 2017
	# Range: 40% - 50% (median: 42.50%)
	PercDebt = .45
	#***********************************************************

	#************Input: Debt Term************
	# Units: yrs
	# Source: Feldman and Schwabe, 2017
	# Range: 5-20 (median: 13) 

	DebtTerm = 13
	#******************************************

	#************Input: Interest Rate on Term Debt************
	# Units: %
	# Source: Feldman and Schwabe, 2017
	# Range: 3.5% - 5.25% (median: 4.24%)
	
	IntRateDebt = 0.04375
	#******************************************

	print("Debt Percent: ", PercDebt, ", Debt Term: ", DebtTerm, ", Interest rate: ", IntRateDebt)
	print('----------')

	#************Input: Lender's Fee (% total borrowing)************
	# Units: %
	LenderFee = 0.03
	#******************************************

	#************Input: Required Minimum Annual DSCR************
	# Units: --
	MinAnnualDSCR = 1.2
	#******************************************

	#************Input: Required Average DSCR************
	# Units: --
	# Source: Feldman and Schwabe, 2017
	# Range: 1.25 - 1.33 (median: 1.3)
	AvgAnnualDSCR = 0
	#******************************************

	#--------------Calculation: Equity---------
	# Units: $
	Equity = 1-PercDebt

	#--------------------------------------------------------

	#************Input: Target After-Tax Equity IRR************
	# Units: %
	# Source: Feldman and Schwabe, 2017
	# Range: 6.5% - 11% (median: 8.5%)
	# This is corroborated by Fu et al., 2015 using 7.01%
	AfterTaxEquity = 0.0875
	#******************************************

	#************Input: Other closing costs************
	# Units: $
	ClosingCosts = 0
	#******************************************

	#________________________Tax______________________
	# Assume owner is a taxable entity
	# Adssume Federal and Tax Benefits are used as generated

	#************Input: Federal Income Tax Rate************
	# Units: %
	FedTaxRate = 0.35
	#******************************************

	#************Input: State Income Tax Rate************
	# Units: %
	StateTaxRate = 0.123 # Changed to CA (highest tax bracket rate)
	#******************************************

	#************Calculation: Effective Income Tax Rate************
	# Units: %
	EffIncomeTaxRate = FedTaxRate + (StateTaxRate*(1-FedTaxRate)) 
	#******************************************

	#________________________Cost-Based Tariff Rate Structure______________________
	
	#************Input: Payment Duration for Cost-Based Tariff************
	# Units: years
	PayDur = 30
	#******************************************

	#************Input: % of Year-One Tariff Rate Escalated************
	# Units: %
	Yr1TariffRateEsc = 0
	#******************************************

	#************Input: Cost-Based Tariff Escalation Rate************
	# Units: %
	CostBasedTEscR = 0
	#******************************************

	#________________________Federal Incentives______________________
	# Form of Federal Incentives: Cost-Based
	# Type of incentive: Investment Tax Credit (ITC)

	#************Input: ITC amount************
	# Units: %
	ITC = 0.3
	#******************************************

	#************Input: ITC utilization factor************
	# Units: %
	ITCutilization = 1
	#******************************************

	## No additional Federal or State taxes.

	#________________________Capital Expenditures: Inverter Replacements______________________

	#************Inputs: Equiment replacement and costs************
	# Units: year
	OneEqRepl = 12
	# Units: $/Watt dc
	OneReplCost = 0.16
	# Units: year
	TwoEqRepl = 24
	# Units: $/Watt dc
	TwoReplCost = 0.16

	# Cost for each replacement (needed for cashflow calculations)
	firstRep = OneReplCost * genNPC * 1000
	secondRep = TwoReplCost * genNPC * 1000
	#******************************************

	#____________________Reserves Funded from Operations: Decommissioning Reserves______________________
	# Fund from Operations
	ReserveReq = 0

	#________________________Initial Funding of Reserve Accounts______________________
	#************Input: # of months of Debt Service************
	# Units: month
	monthsDebt = 6
	#******************************************
	#************Input: # of months of O&M expense************
	# Units: month
	monthsOM = 6
	#******************************************
	#************Input: Interest on All Reserves************
	# Units: %
	intReserve = 0.02
	#******************************************

	#________________________Depreciation Allocation______________________
	# Assume Bonus Depreciation = YES
	#************Input: % of bonus depreciation applied in Year 1************
	# Units: % (note, this is usually a federal number)
	depY1 = 0.5
	#******************************************

	# Table of Allocation of costs (MACRS)
	macrs = pd.read_csv('macrs.csv',index_col=0)
	# print(macrs)

	macrs_halfyear = pd.read_csv('macrs_halfyear.csv',index_col=0)
	# print(macrs_halfyear.values)

	#________________________Financial Values______________________
	#These values are used to calculate LCOE using the equation found in the 1995 econ handbook
	
	# Real discount rate: very difficult to find, as it depends on the investor
	# Note: for a renewabel energy project that is a higher risk than an alternative investment, 
	# the IRR (profit requirement or risk of project) may be higher than the discount rate (value
	# of alternative investment)


	# Discount rates are "very subjective" and project developments don't want to share theve rates
	# Source: NREL cost benhcmark 2018 uses 6.3%
	# Law firm Grant Thorton did a survey in 2018 and uses 6.5%
	# Uniform distrubution: 6.3% - 6.5%
	d_real = 0.064

	# Inflation rate: used average inflation from bls.gov (last 12 months as of Nov 2019)
	inflation = 0.021

	#Nominal discount rate (using the values above to calculate)
	d_nom = (1+d_real)*(1+inflation) - 1

	n = np.arange(1,UseLife+1,1)
	d_real_matrix = np.power((1+d_real), n)
	d_nom_matrix = np.power((1+d_nom), n)


	#_______________________CASH FLOW TAB___________________________________
	
	# Production
	# Row 0: Production Degredation Factor
	# Row 1: Production
	production = cashflow.Production(UseLife, ProdYr1, ProjDeg)



	#-----------------Calculation: Insurance Year 1 ($) -------
	# Units: $	Depends on DevCFCost, InterconConst
	Insuryr1 = Insuryr1perc*(GenEqCost+BOPCost+InterconCost+DevCFCost)
	# ---------------------------------------------------------
	#--------------Calculation: Interest during Construction---------
	# Units: $	Depends on DevCFCost, InterconConst
	IntConst = (GenEqCost + BOPCost + InterconCost + DevCFCost)*(IntRateAnnual/12)*(ConstPeriod/2)
	#--------------------------------------------------------
	i = 0 #For old calcs

	Yr1COE, NPV, TotInstCost, TotalOpExp = mainfunctions.CashFlowFunction(i, UseLife, Yr1TariffRateEsc, CostBasedTEscR,\
		GenEqCost, BOPCost, InterconCost, DevCFCost, PercDebt, DebtTerm, IntRateDebt, production,\
		Royal, PayDur, LastDay, OMcostinfl, OMcostinflafter, FixedOandM, genNPC, VarOandM,\
		Insuryr1, ProjMan, PILOT, PropTaxAd, LandLease, monthsDebt, monthsOM, firstRep, secondRep,\
		OneEqRepl, TwoEqRepl, ReserveReq, intReserve, LenderFee, IntConst, ClosingCosts, macrs,\
		macrs_halfyear, depY1, OneReplCost, TwoReplCost, EffIncomeTaxRate, StateTaxRate, FedTaxRate,\
		AfterTaxEquity, ITC, ITCutilization)

	LCOE_real = -(-TotInstCost + sum(np.divide(TotalOpExp,d_nom_matrix))) / sum(np.divide(production[1,:],d_real_matrix))
	LCOE_nom = -(-TotInstCost + sum(np.divide(TotalOpExp,d_nom_matrix))) / sum(np.divide(production[1,:],d_nom_matrix))

	print('Real LCOE (cents/kWh): ', LCOE_real*100)
	# print('Nominal LCOE (cents/kWh): ', LCOE_nom*100)
	# print('Year 1 production', production[1,1])
	# print('Total Capacity (kWdc): ', genNPC)
	# print('Installed Cost: ', TotInstCost)
	print('Installed Cost per watt: ', TotInstCost/(genNPC*1000))

if __name__ == '__main__':
	start_time = time.time()
	main()
	print("--- %s seconds ---" % (time.time() - start_time))
