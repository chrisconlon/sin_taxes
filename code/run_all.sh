#!/bin/sh

# These should be run in order
python 0_read_nielsen_data.py
python 1_Prep_States_Tax.py
python 2_Create_Panel.py
python 3_Assign_Clusters.py


# These can be run in any order
python table1_revised.py
python table2_odds_ratio.py
python table3_by_year.py
python tableA1_alcohol_usage.py
python tableA2_ethanol_per_capita.py
python tableA3_tobacco_useage.py
python tableB2_state_taxes.py
python tableD1_tax_burden_by_inc.py
python tableD2_sin_tax_by_Race.py
python tableD4_tax_inc_ratio.py
python tableD6multiNM.py
python tableE1E2_Other_Cluster_Number.py

# These can be run in any order
python Figure1_cdfs.py
python Figure2_Correlation.py
