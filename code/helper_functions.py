import pandas as pd
import numpy as np
import re
import pyarrow.dataset as ds
from common_import import (oz_l, qt_l, ml_l, l_oz,beer_abv, wine_abv,SSB_tax_rate,
	 age_map, edu_map, inc_map, race_map, FED_Beer, FED_Wine, FED_Spirits, FED_cigarette, tab_dir, write_tex_table)

# Fix the weird capitalization
rename_dict={'Projection_Factor':'projection_factor',
	    'Household_Income':'household_income',
	    'Fips_State_Desc':'fips_state_desc',
	    'DMA_Cd':'dma_code'}

# Column lists
purch_cols = ['household_code','upc','upc_ver_uc','quantity','total_price_paid','panel_year']

prod_cols = ['upc',  'upc_ver_uc','brand_code_uc','product_module_code','product_module_descr','upc_descr','brand_descr',
	'product_group_code','size1_amount','size1_units','multi']

ix_cols = ['household_code', 'panel_year']

hh_cols = ['projection_factor','fips_state_desc','Household_Size',
    'household_income','median_income','inc_per_capita', 'presence_child',
    'Hispanic_Origin','Adult', 'income_group', 'age_group', 'edu_group', 'race']

def clean_upc_descr(df):
	df['upc_descr']=df['upc_descr'].str.strip()
	return df


def calc_abv(df):
	df['abv'] = df['proof']/200
	df.loc[(df['subcate']=='beer') & (df['product_group_code'] != 5002),'abv'] = beer_abv
	df.loc[(df['subcate']=='wine') & (df['product_group_code'] != 5002),'abv'] = wine_abv
	df['abv'] = df['abv'].fillna(0)
	return df

### Product below
##Scrape Proof content from upc description
def getProof(descr):
	pattern = re.compile("\d\d*\\.*\d*P")    
	if descr is None:
		return 0    
	matches = pattern.findall(descr.replace("PK", "").replace("PT", ""))
	if len(matches) > 1:
	#print("Multiple matches found: " + descr)
	#print(matches)
		return matches[0][:-1]
	elif (len(matches) < 1):
	#print("Zero matches found: " + descr)
	#cc: use np.nan for missing
		return np.nan
	else:
		return matches[0][:-1]


##Manualy fill out some outlier cases
def add_proof(p):
	p2 = p.query('product_group_code==5002').copy()
	p2['proof'] = p2['upc_descr'].str.strip().apply(getProof)

	#manually adjust proof column of a few edge cases	
	#cc:  use category to fill missing
	p2['proof']=p2['proof'].combine_first(
		p2.groupby(['product_module_code'])['proof'].transform(np.median)
	)
 	# Assign by brand
	p2.loc[(p2.upc_descr=='RG13P RUM PRALINE 80P'),'proof']= 80
	p2.loc[(p2.upc_descr=='FFLY MSN WHISKEY BKBRY 71.4 P'),'proof']= 71.4
	p2.loc[(p2.upc_descr=='WLT STRT RYE WHISKEY 117.4 P'),'proof']= 117.4
	p2.loc[(p2.upc_descr=='1876PH BRNDY DM 80P'),'proof']= 80

	p2.loc[(p2.brand_code_uc==774056),'proof']= 25
	p2.loc[(p2.brand_code_uc==659748),'proof']= 60
	p2.loc[(p2.brand_code_uc==500928),'proof']= 60
	p2.loc[(p2.upc==75837116504),'proof']= 92.6
	p2.loc[(p2.upc==8249686255),'proof']= 86
	p2.loc[(p2.upc==8807617700),'proof']= 86
	p2.loc[(p2.upc==8775202160),'proof']= 95
	p2.loc[(p2.upc==8043211361),'proof']= 92
	p2.loc[(p2.upc==85176700112),'proof']= 100
	p2.loc[(p2.upc==60998675231),'proof']= 30
	p2.loc[(p2.upc==83613700704),'proof']= 70

	p2['proof'] = p2['proof'].astype(float)

	# merge against original data
	p3 = pd.merge(p, p2[['upc','upc_ver_uc','proof']], on=['upc','upc_ver_uc'], how='left')

	# Call "RTD liquor" less than 5% abv (beer)
	p3.loc[(p3.product_module_code.isin([5040,5048])) & (p3.proof <= 10),'subcate'] = 'beer'

	return p3

def prep_product_data(fn_prod, fn_cat):
	df_cat = pd.read_excel(fn_cat,'category')[['product_group_code','product_module_code','category','subcate']]

	diet_list = pd.read_excel(fn_cat,'diet')['brand_code_uc'].unique()
	
	df_prod = pd.merge(
		ds.dataset(fn_prod)\
		.to_table(columns=prod_cols)\
		.to_pandas(),
		df_cat, on =['product_group_code','product_module_code'])\
		.pipe(clean_upc_descr)\
		.pipe(add_proof)\
		.pipe(calc_abv)

	df_prod.loc[df_prod.brand_code_uc.isin(diet_list),'subcate'] = 'diet'

	# Unit Conversion
	df_prod['size1_adjusted'] = df_prod['size1_amount']
	df_prod.loc[df_prod.size1_units == 'OZ','size1_adjusted'] = (df_prod['size1_amount']*oz_l)
	df_prod.loc[df_prod.size1_units == 'QT','size1_adjusted'] = (df_prod['size1_amount']*qt_l)
	df_prod.loc[df_prod.size1_units == 'ML','size1_adjusted'] = (df_prod['size1_amount']*ml_l)
	#convert units from ct to pack 
	df_prod.loc[df_prod.subcate == 'cigars','size1_adjusted'] = (df_prod['size1_amount']/20)
	
	df_prod['category'] = df_prod['category'].astype('category')
	df_prod['subcate'] = df_prod['subcate'].astype('category')


	return df_prod.drop(columns=['upc_descr'])

### Product above
### Household below

def clean_hh(df, fn_bins):
	# Compute number of Adults= HHSize - # Kids
	df2=df.rename(columns=rename_dict).pipe(add_adults, age_threshold=18)

	# consolidate groups
	# Use the highest age/education for household
	df2['income_group'] = df2.household_income\
		.map(inc_map).astype('category')
	df2['age_group'] = df2[['Male_Head_Age', 'Female_Head_Age']].max(axis=1)\
		.map(age_map).astype('category')
	df2['edu_group'] = df2[['Male_Head_Education', 'Female_Head_Education']].max(axis=1)\
		.map(edu_map).astype('category')
	df2['race'] = df2['Race']\
		.map(race_map).astype('category')

	# Compress data types when possible
	df2['fips_state_desc'] = df2['fips_state_desc'].astype('category')
	df2['Hispanic_Origin'] = (df2['Hispanic_Origin']==1).astype(bool)
	df2['dma_code'] = df2['dma_code'].astype('int')
	df2['presence_child'] = (df2['Age_And_Presence_Of_Children'] < 9).astype(bool)

	# Construct the median income and per capita income
	df_bins = pd.read_excel(fn_bins, engine='openpyxl')
	df3 = pd.merge(df2, df_bins, on='household_income')
	if df3.panel_year.max() < 2010:
		df3['median_income'] = df3['med_inc_early']
	else:
		df3['median_income'] = df3['med_inc_late']
	df3['inc_per_capita'] = df3['median_income']/df3['Household_Size']
	return df3

def add_adults(df, age_threshold=18):
	# Total Household size less number of kids under age_threshold
	df['Adult'] = (
		df['Household_Size'].values- 
		(df.filter(regex=('Member_.*_Birth')).values >
		 (df.panel_year-age_threshold).values[:,None]).sum(axis=1)
		).astype(int)
	return df

### Household Above

###Aggregate consumption to household level
def calc_volume(df_purchases):
	df_purchases['total_volume'] = df_purchases['quantity'] * df_purchases['size1_adjusted']* df_purchases['multi']
	df_purchases['ethanol'] = df_purchases['total_volume']*df_purchases['abv']
	return df_purchases[['household_code','total_price_paid','total_volume','panel_year','category','subcate','ethanol']]


def hh_consumption(fn_hh, fn_purchases, fn_bins, df_prod, year=2018):
	# household data
	hh_data = pd.read_parquet(fn_hh)\
		.pipe(clean_hh, fn_bins)\
		[ix_cols + hh_cols]

	#Read in purchase data
	df_totals = pd.merge(pd.read_parquet(fn_purchases,columns=purch_cols)\
		.query('panel_year == @year'),
		df_prod,
		on=['upc', 'upc_ver_uc'])\
		.pipe(calc_volume)\
		.groupby(['household_code','panel_year','category','subcate'], observed=True, as_index=False)\
		[['total_price_paid','total_volume','ethanol']]\
		.sum()
		
	print('Done with purchase data: ',year)

	return pd.merge(df_totals, hh_data, on=ix_cols)

def remove_outlier(df, al_ub, tb_ub):

	df['ethanol'] = df['ethanol'].fillna(value=0)



	mask = (df['ethanol']/df['Adult'] <= al_ub) & (df['cigars']/df['Adult'] <= tb_ub)
	print("\nOutliers by year:")
	print(df[~mask].groupby(['panel_year'])['household_income'].count())

	rename_dict={'beer':'Beer','cigars':'Cigarettes','carbonated':'SSB','median_income':'Income',
					'liquor':'Spirits','wine':'Wine','ethanol':'Ethanol','Household_Size':'Household Size'}
	temp = df.reset_index().query('panel_year==2018')
	
	fn_table_outA = tab_dir/"tableC1_A.tex"
	fn_table_outB = tab_dir/"tableC1_B.tex"
	outliers_al = temp[temp['ethanol']/temp['Adult'] > al_ub][['beer','liquor','wine','ethanol','cigars','Household_Size','Adult','carbonated','median_income']]
	outliers_tb = temp[temp['cigars']/temp['Adult'] > tb_ub][['beer','liquor','wine','ethanol','cigars','Household_Size','Adult','carbonated','median_income']]

	latex1 = outliers_al.rename(columns=rename_dict).describe().to_latex(float_format="%.2f").splitlines()
	latex1.insert(2,'\\multicolumn{9}{l}{\textbf{Panel A: Alcohol Outliers - 20}}'+ ' \\\\')
	del latex1[5]
	write_tex_table('\n'.join(latex1), fn_table_outA)

	latex2 = outliers_tb.rename(columns=rename_dict).describe().to_latex(float_format="%.2f").splitlines()
	latex2.insert(2,'\\multicolumn{9}{l}{\textbf{Panel B: Tobacco Outliers - 3}}'+ ' \\\\')
	del latex2[5]
	write_tex_table('\n'.join(latex2), fn_table_outB)

	return df[mask].copy()

# compute ethanol total and price per liter

def get_ethanol_totals(df):
	df_ethanol = df.query('category=="alcohol"')\
		.groupby(ix_cols)\
		[['total_price_paid','ethanol']].sum()
	df_ethanol['price_per_liter'] = df_ethanol['total_price_paid']/df_ethanol['ethanol']
	return df_ethanol[['ethanol','price_per_liter']].copy()

#Attach state tax rate
def tax_per_hh(df, fn_taxes):
	df = df.reset_index()
	df_tax = pd.read_parquet(fn_taxes)

	df = pd.merge(df, df_tax, 
		left_on=['fips_state_desc','panel_year'], 
		right_on=['States','panel_year'])

	## CC: Where are these calculations coming from -- constants live in common_import.py
	df['beer_tax'] = df['beer']*(FED_Beer+df['Beer'])
	df['spirits_tax'] = df['liquor']*(FED_Spirits+df['Spirits'])
	df['wine_tax'] = df['wine']*(FED_Wine+df['Wine'])
	df['cigarette_tax'] = df['cigars']*(FED_cigarette+df['TAX RATE'])
	df['ssb_tax'] = df['carbonated']*l_oz*SSB_tax_rate #per ounce

	df['total_tax'] = df['beer_tax']+df['spirits_tax']+df['wine_tax']+df['cigarette_tax']+df['ssb_tax']
	df['total_tax_but_ssb'] = df['beer_tax']+df['spirits_tax']+df['wine_tax']+df['cigarette_tax']
	return df.drop(columns=['State name','State abbreviation','Spirits','Beer','Wine','TAX RATE','STATE'])
