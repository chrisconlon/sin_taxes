import pandas as pd
import numpy as np
import pathlib as path

from common_import import data_dir, tab_dir
from common_import import write_tex_table, liters_per_gallon, ethanol_in_beer, ethanol_in_wine, ethanol_in_spirits




# Inputs
fn_taxes = data_dir/'states_taxes.parquet'
fn_panel = data_dir / 'panel_data_all_years.parquet'


### Table B2 in Appendix
fn_table_out = tab_dir / 'tableB1.tex'


# Read in the Tax Info
df_tax = pd.read_parquet(fn_taxes).query('panel_year==2018')
df = pd.read_parquet(fn_panel)


# Define a lambda function to compute the weighted mean:
wm = lambda x: np.average(x, weights=df.loc[x.index, "projection_factor"])

print(np.average(df['total_tax_but_ssb'],weights = df['projection_factor']))

df =  df.groupby('fips_state_desc')\
		.agg(weighted_mean=("total_tax_but_ssb", wm))\
		.reset_index()

fnl = pd.merge(df_tax, df, left_on='State',right_on='fips_state_desc',how='left')\
		.drop(columns=['fips_state_desc'])

fnl['Beer tax per ethanol/L'] = fnl['Beer'] /ethanol_in_beer
fnl['Wine tax per ethanol/L'] = fnl['Wine'] /ethanol_in_wine
fnl['Spirits tax per ethanol/L'] = fnl['Spirits'] /ethanol_in_spirits
fnl = fnl[['State','Beer','Wine','Spirits','Cigarettes','Beer tax per ethanol/L','Wine tax per ethanol/L','Spirits tax per ethanol/L','weighted_mean']]
# print(fnl.round(2).to_latex(index=False))

# Write the table
latex = fnl.to_latex(float_format="%.2f",index=False).splitlines()
latex[0] = '\\begin{tabular}{l | l l l l | l l l | l}'
latex.insert(2,'& \\multicolumn{3}{c}{Tax Rate (per L)} & &  \\multicolumn{3}{c}{Tax Rate (per Ethanol L)} &'+ ' \\\\')
latex[3] = 'State &  Beer  &  Wine  &  Spirits  &  Cigarette  &  Beer  &  Wine  &  Spirits &  Tax/HH'+ ' \\\\'
latex.insert(5,'FED &           0.15&   0.28&           2.85&           1.01&   3.40&   2.19&7.13    &61.95'+ ' \\\\')
latex.insert(57,latex[14])
del latex[14]
del latex[7]
del latex[15]
write_tex_table('\n'.join(latex), fn_table_out)

