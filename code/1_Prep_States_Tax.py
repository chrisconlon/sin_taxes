import pandas as pd
import numpy as np

import pathlib as path
import re
from common_import import raw_dir, data_dir, tax_dir, l_gallon,write_tex_table,tab_dir

pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', None)


liters_per_gallon = 3.78541
ethanol_in_beer = 0.045
ethanol_in_wine = 0.129
ethanol_in_spirits = 0.4

fn_cigarette = 'state_cigarette_rates_5.xlsx'
fn_alcohol = 'state_alcohol_rates.xlsx'
fn_panel = data_dir / 'panel_data_all_years.parquet'


Region={'Connecticut':'Northeast','Maine':'Northeast','Massachusetts':'Northeast','New Hampshire':'Northeast','Rhode Island':'Northeast','Vermont':'Northeast','New Jersey':'Northeast','New York':'Northeast','Pennsylvania':'Northeast',
		'Indiana':'Midwest','Illinois':'Midwest','Michigan':'Midwest','Ohio':'Midwest','Wisconsin':'Midwest','Iowa':'Midwest',
		'Kansas':'Midwest','Minnesota':'Midwest','Missouri':'Midwest','Nebraska':'Midwest','North Dakota':'Midwest','South Dakota':'Midwest',
		'Delaware':'South','District Of Columbia':'South','Florida':'South','Georgia':'South','Maryland':'South','North Carolina':'South',
		'South Carolina':'South','Virginia':'South','West Virginia':'South','Alabama':'South','Kentucky':'South','Mississippi':'South',
		'Tennessee':'South','Arkansas':'South','Louisiana':'South','Oklahoma':'South','Texas':'South',
		'Arizona':'West','Colorado':'West','Idaho':'West','New Mexico':'West','Montana':'West','Utah':'West',
		'Nevada':'West','Wyoming':'West','Alaska':'West','California':'West','Hawaii':'West','Oregon':'West','Washington':'West'
		}

states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT","DE", "FL", "GA", 
		  "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
		  "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
		  "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
		  "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY","DC"]

#Sin Tax Rate
#cigarettes

def cig_tax(Y = 2018):
	df_cig = pd.read_excel(raw_dir/fn_cigarette,str(Y),skiprows=[0,1,2])
	df_cig = df_cig.iloc[:27,:]
	df_cig.drop(index=df_cig.index[0], 
			axis=0, 
			inplace=True)
	first_half = df_cig[['STATE','TAX RATE']]
	second_half = df_cig[['STATE.1','TAX RATE.1']].rename(columns={'STATE.1':'STATE','TAX RATE.1':'TAX RATE'})
	df_cig = pd.concat([first_half,second_half],ignore_index=True)
	df_cig = df_cig.iloc[:-1,:]
	df_cig['STATE'] = states
	df_cig['TAX RATE'] = df_cig['TAX RATE']*0.01 #dollars per pack
	df_cig['panel_year'] = Y
	return df_cig

# df_cig = pd.concat([cig_tax(Y) for Y in range(2007,2020+1)],ignore_index=True)
# df_cig.to_parquet(tax_dir/'states_cigarettes.parquet')


def alcohol_tax():
	df = pd.read_excel(raw_dir/fn_alcohol,'1982-2022',skiprows=[0,1,2]).query("Year > 2006")[['State name','State abbreviation','Year','Distilled spirits','Beer','Wine']]\
			.rename(columns={'Distilled spirits':'Spirits','Year':'panel_year'})

	df.loc[df['Spirits']=='n.a.','Spirits']=np.nan
	df.loc[df['Wine']=='n.a.','Wine']=np.nan

	df['Beer'] =  df['Beer'].astype(float)/l_gallon
	df['Spirits'] = df['Spirits'].astype(float)/l_gallon
	df['Wine'] = df['Wine'].astype(float)/l_gallon

	df['Region'] = df['State name'].map(Region)

	#use Region to fill missing
	df['Spirits']=df['Spirits'].combine_first(
		df.groupby(['Region'])['Spirits'].transform(np.median)
	)

	df['Wine']=df['Wine'].combine_first(
		df.groupby(['Region'])['Wine'].transform(np.median)
	)

	df.to_parquet(tax_dir/'states_alcohol.parquet')


# alcohol_tax()

### Table B2 in Appendix
fn_table_out = tab_dir / 'tableB1.tex'
df1 = pd.read_parquet(tax_dir/'states_alcohol.parquet')
print(df1.head())
df2 = pd.read_parquet(tax_dir/'states_cigarettes.parquet')
print(df2.head())

tax_panel = pd.merge(df1,df2,left_on=['State abbreviation','panel_year'],right_on=['STATE','panel_year'])
tax_panel = tax_panel[tax_panel['panel_year']==2018][['STATE','Beer','Wine','Spirits','TAX RATE']]
tax_panel = tax_panel.rename(columns={'Beer':'beer tax','Wine':'wine tax','Spirits':'spirits tax','TAX RATE':'cigarette tax'})

df = pd.read_parquet(data_dir/fn_panel)

# Define a lambda function to compute the weighted mean:
wm = lambda x: np.average(x, weights=df.loc[x.index, "projection_factor"])

print(np.average(df['total_tax_but_ssb'],weights = df['projection_factor']))

df = df.groupby('fips_state_desc').agg(weighted_mean=("total_tax_but_ssb", wm)).reset_index()

fnl = pd.merge(tax_panel,df,left_on='STATE',right_on='fips_state_desc',how='left').drop(columns=['fips_state_desc'])

fnl['Beer tax per ethanol/L'] = fnl['beer tax'] /ethanol_in_beer
fnl['Wine tax per ethanol/L'] = fnl['wine tax'] /ethanol_in_wine
fnl['Spirits tax per ethanol/L'] = fnl['spirits tax'] /ethanol_in_spirits
fnl = fnl[['STATE','beer tax','wine tax','spirits tax','cigarette tax','Beer tax per ethanol/L','Wine tax per ethanol/L','Spirits tax per ethanol/L','weighted_mean']]
# print(fnl.round(2).to_latex(index=False))

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




