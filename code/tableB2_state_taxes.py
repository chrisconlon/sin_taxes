import pandas as pd
import numpy as np
import pathlib as path

from common_import import data_dir, tab_dir
from common_import import write_tex_table, liters_per_gallon, ethanol_in_beer, ethanol_in_wine, ethanol_in_spirits


# Inputs
f_cig_out = data_dir/'states_cigarettes.parquet'
f_alcohol_out = data_dir / 'states_alcohol.parquet'
fn_panel = data_dir / 'panel_data_all_years.parquet'


### Table B2 in Appendix
fn_table_out = tab_dir / 'tableB1.tex'


# Read in the Tax Info
df1 = pd.read_parquet(f_alcohol)
df2 = pd.read_parquet(f_cigarette)
df = pd.read_parquet(fn_panel)


# Merge the tax data
tax_panel = pd.merge(df1, df2, left_on=['State abbreviation','panel_year'],right_on=['STATE','panel_year'])
tax_panel = tax_panel[tax_panel['panel_year']==2018][['STATE','Beer','Wine','Spirits','TAX RATE']]
tax_panel = tax_panel.rename(columns={'Beer':'beer tax','Wine':'wine tax','Spirits':'spirits tax','TAX RATE':'cigarette tax'})


# Define a lambda function to compute the weighted mean:
wm = lambda x: np.average(x, weights=df.loc[x.index, "projection_factor"])

print(np.average(df['total_tax_but_ssb'],weights = df['projection_factor']))

df =  df.groupby('fips_state_desc')\
		.agg(weighted_mean=("total_tax_but_ssb", wm))\
		.reset_index()

fnl = pd.merge(tax_panel, df, left_on='STATE',right_on='fips_state_desc',how='left')\
		.drop(columns=['fips_state_desc'])

fnl['Beer tax per ethanol/L'] = fnl['beer tax'] /ethanol_in_beer
fnl['Wine tax per ethanol/L'] = fnl['wine tax'] /ethanol_in_wine
fnl['Spirits tax per ethanol/L'] = fnl['spirits tax'] /ethanol_in_spirits
fnl = fnl[['STATE','beer tax','wine tax','spirits tax','cigarette tax','Beer tax per ethanol/L','Wine tax per ethanol/L','Spirits tax per ethanol/L','weighted_mean']]
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

