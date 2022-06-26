import pandas as pd
import numpy as np
import pathlib as path

from common_import import raw_dir, data_dir, liters_per_gallon

# inputs
fn_cigarette = raw_dir / 'state_cigarette_rates_5.xlsx'
fn_alcohol = raw_dir / 'state_alcohol_rates.xlsx'

# Outputs
f_cig_out = data_dir/'states_cigarettes.parquet'
f_alcohol_out = data_dir / 'states_alcohol.parquet'

# Constants
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

# functions to process data
def alcohol_tax(fn_in):
	df = pd.read_excel(fn_in, '1982-2022',skiprows=[0,1,2]).query("Year > 2006")[['State name','State abbreviation','Year','Distilled spirits','Beer','Wine']]\
			.rename(columns={'Distilled spirits':'Spirits','Year':'panel_year'})

	df.loc[df['Spirits']=='n.a.','Spirits']=np.nan
	df.loc[df['Wine']=='n.a.','Wine']=np.nan

	df['Beer'] =  df['Beer'].astype(float)/liters_per_gallon
	df['Spirits'] = df['Spirits'].astype(float)/liters_per_gallon
	df['Wine'] = df['Wine'].astype(float)/liters_per_gallon

	df['Region'] = df['State name'].map(Region)

	#use Region to fill missing
	df['Spirits']=df['Spirits'].combine_first(
		df.groupby(['Region'])['Spirits'].transform(np.median)
	)

	df['Wine']=df['Wine'].combine_first(
		df.groupby(['Region'])['Wine'].transform(np.median)
	)

	return df

def cig_tax(fn_in, Y = 2018):
	df_cig = pd.read_excel(fn_in, str(Y), skiprows=[0,1,2])
	df_cig = df_cig.iloc[:27,:]
	df_cig.drop(index=df_cig.index[0], axis=0, inplace=True)
	first_half = df_cig[['STATE','TAX RATE']]
	second_half = df_cig[['STATE.1','TAX RATE.1']].rename(columns={'STATE.1':'STATE','TAX RATE.1':'TAX RATE'})
	df_cig = pd.concat([first_half, second_half], ignore_index=True)
	df_cig = df_cig.iloc[:-1,:]
	df_cig['STATE'] = states
	df_cig['TAX RATE'] = df_cig['TAX RATE']*0.01 #dollars per pack
	df_cig['panel_year'] = Y
	return df_cig

df_cig = pd.concat([cig_tax(fn_cigarette, y) for y in range(2007,2020+1)], ignore_index=True)
df_alcohol = alcohol_tax(fn_alcohol)

# save the files
df_cig.to_parquet(f_cig_out)
df_alcohol.to_parquet(f_alcohol_out)
