import numpy as np
import pandas as pd
import pathlib as path
from common_import import (raw_dir, data_dir,tab_dir,fig_dir,
 weighted_quantile, np_wsum, np_wavg, drinks_per_ethanol_L, write_tex_table)

# input
fn_clusters = data_dir / 'cluster_data_all_years.parquet'
# output
# fn_table1 = tab_dir / 'table1_revision.tex'
fn_table1 = tab_dir / 'table1.tex'

col_order = ['Everything', 'Smokers', 'Heavy Drinkers','Moderate Spirits', 'Mostly Wine',  'Moderate Beer', 'SSB only','Nothing']
row_labels=['Beer (mean)','Wine (mean)','Spirits (mean)','Tobacco (mean)','SSB (mean)','Ethanol (mean)',
			'Beer 50\%','Beer 75\%','Beer 95\%',
			'Wine 50\%','Wine 75\%','Wine 95\%',
			'Spirits 50\%','Spirits 75\%','Spirits 95\%',
			'Tobacco 50\%','Tobacco 75\%','Tobacco 95\%',
			'SSB 50\%','SSB 75\%','SSB 95\%',
			'SSB per Person/Week',
			'Drinks per Week','Drinks per Adult',
			'Effective Ethanol Tax/L', 'Ethanol Externality','Externality Share',
			'Total Tax Share','Alcohol Tax Share','Tobacco Tax Share','SSB Tax Share',
			'Tax Burden/Income (\%)',
			'\# Households','Share of Households'
			]

def per_avg(df,pa_cols):
	x=np_wsum(df, pa_cols, 'projection_factor')
	return x[pa_cols].div(x['total_w'],axis=0)

def process_table(df):
	quantiles = [0.5,0.75,0.95]
	qcol_list = ['beer','wine','liquor','cigars','carbonated']
	col_list = qcol_list +['ethanol']
	tax_cols = ['externality_med','total_tax_but_ssb','alcohol_tax','cigarette_tax','ssb_tax']
	other_cols = ['ssb_ratio','sin_tax_ratio','ssb_tax_ratio','income_share']

	# Compute our fields
	df['alcohol_tax'] = df.beer_tax+df.wine_tax+df.spirits_tax
	df['ethanol_ratio'] = df['ethanol']/df['Adult']
	df['cigar_ratio'] = df['cigars']/df['Adult']
	df['ssb_ratio'] = df['carbonated']/(52*df['Household_Size'])
	df['alcohol_tax_ratio'] = df['alcohol_tax']/df['Adult']
	df['sin_tax_ratio'] = df['total_tax_but_ssb']/df['Adult']

	df['ssb_tax_ratio'] = df['ssb_tax']/df['Adult']
	df['income_share'] = 100.0*df['total_tax']/df['median_income']
	df['effective_ethanol_tax'] = df['alcohol_tax']/df['ethanol']
	df['drinks_per_week'] = df['ethanol']/(drinks_per_ethanol_L * 52)
	df['drinks_per_week_pa'] = df['ethanol']/(df['Adult']*drinks_per_ethanol_L * 52)

	quantile_df=pd.concat([df.groupby('clusters').apply(lambda g: 
		pd.Series(weighted_quantile(g[col], quantiles, g.projection_factor), 
		index=[col +'_'+str(q) for q in quantiles])) for col in qcol_list],axis=1)

	mean_df=df.groupby('clusters').apply(lambda g:
		pd.Series(np.average(g[col_list], axis=0, weights=g['projection_factor']),
		index=['mean_'+str(c) for c in col_list]))

	per_capita_df=df.groupby('clusters').apply(per_avg, 
		['ssb_ratio','drinks_per_week','drinks_per_week_pa']+\
		['effective_ethanol_tax','externality_med'])

	other_df=df.groupby('clusters').apply(per_avg, ['income_share'])

	externality_share= df.groupby('clusters').apply(np_wsum, ['externality_med'],'projection_factor')
	externality_share= (100.*externality_share/externality_share.sum())['externality_med']

	tax_share= df.groupby('clusters').apply(np_wsum, tax_cols,'projection_factor')
	tax_share= (100.*tax_share/tax_share.sum())[tax_cols]

	obs_counts = df.groupby('clusters')['projection_factor'].agg([np.size,np.sum])
	obs_counts['sum'] = 100.0*obs_counts['sum']/obs_counts['sum'].sum()

	tab_df = pd.concat([mean_df, quantile_df, per_capita_df, tax_share, other_df, obs_counts],axis=1).transpose()
	tab_df.index = row_labels
	tab_df.columns.name=''
	return tab_df[col_order].copy()

def write_table1(tab_df, fn_out):
	as_lines = tab_df.to_latex(na_rep="", escape=False,float_format="%.2f").splitlines()
	# add some dividers
	as_lines[10:10] = ['\\midrule']
	as_lines[26:26] = ['\\midrule']
	as_lines[-9:-9] = ['\\midrule']
	as_lines[-5:-5] = ['\\midrule']

	# get # households as an integer
	as_lines[-4] = '\\# Households \t\t &' + ' & \t\t'.join(list(tab_df.loc['\# Households'].astype(int).astype(str))) + ' \\\\'

	out_text = '\n'.join(as_lines)

	write_tex_table(out_text, fn_table1)


df = pd.read_parquet(fn_clusters).query("panel_year == 2018")
tab_df = process_table(df)
write_table1(tab_df, fn_table1)


