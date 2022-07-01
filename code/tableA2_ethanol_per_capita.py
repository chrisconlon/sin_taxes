import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import pathlib as path
from common_import import raw_dir, data_dir,tab_dir,fig_dir,wine_abv,beer_abv,liquor_abv,write_tex_table

# On-premise shares reported in the final column are from Admas Media Inc (2019). 
#NIAAA data are from https://pubs.niaaa.nih.gov/publications/surveillance115/CONS18.htm.19 
#and Census data can be found at https://fred.stlouisfed.org/series/TTLHH25.

def grouped_weighted_avg(values, weights, by):
	return (values * weights).groupby(by).sum() / weights.groupby(by).sum()

# output
fn_table_out = tab_dir / 'tableA2.tex'

# input
df = pd.read_parquet(data_dir/'panel_data_all_years.parquet').query("panel_year==2018")


# Do the work
table = pd.DataFrame(columns=['Nielsen Volume','Nielsen Ethanol','NIAAA Volume', 'NIAAA Ethanol', 'Ethanol Discrepancy(%)','On-Premise (%)'], \
						index=['Beer','Wine','Spirits'])

# Link for these numbers?
table['NIAAA Volume'] = [188.09,26.98,16.95]
table['NIAAA Ethanol'] = [8.46,3.48,6.97]
table['On-Premise (%)'] = [23.00,18.50,21.20]
table['Nielsen Volume'] = [np.average(df['beer'], weights=df.projection_factor),
							np.average(df['wine'], weights=df.projection_factor),
							np.average(df['liquor'], weights=df.projection_factor)]

table['abv'] = [beer_abv,wine_abv,liquor_abv]
table['Nielsen Ethanol'] = table['Nielsen Volume']*table['abv']
table['Ethanol Discrepancy(%)'] = 100*(table['NIAAA Ethanol'] -table['Nielsen Ethanol'])/table['NIAAA Ethanol']


table = table.drop(columns=['abv']).round(2)
table.loc['Total']= table.sum(axis=0)

table.loc['Total','Ethanol Discrepancy(%)']= 100*(table.loc['Total','NIAAA Ethanol'] -table.loc['Total','Nielsen Ethanol'])/table.loc['Total','NIAAA Ethanol']
table.loc['Total','On-Premise (%)']= np.nan
write_tex_table(table.to_latex(float_format="%.2f"), fn_table_out)

