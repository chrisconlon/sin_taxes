import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import pathlib as path
from common_import import raw_dir, data_dir,tab_dir,fig_dir,wine_abv,beer_abv,liquor_abv,write_tex_table

fn_table_out = tab_dir / 'tableA2.tex'

df_panel = pd.read_parquet(data_dir/'panel_data_all_years.parquet').query("panel_year==2018")
# # pd.set_option('display.max_columns', 500)

pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', None)
# pd.options.mode.chained_assignment = None




def grouped_weighted_avg(values, weights, by):
	return (values * weights).groupby(by).sum() / weights.groupby(by).sum()



#Another way to verify our data - with total gallons in NIAAA
def Run1(df):
	table = pd.DataFrame(columns=['Nielsen Volume','Nielsen Ethanol','NIAAA Volume', 'NIAAA Ethanol', 'Ethanol Discrepancy(%)','On-Premise (%)'], \
							index=['Beer','Wine','Spirits'])
	
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
	table.loc['Total','On-Premise (%)']= ''
	write_tex_table(table.to_latex(float_format="%.2f"), fn_table_out)
	# print(table.drop(columns=['abv']).round(2).to_latex())




Run1(df_panel)

