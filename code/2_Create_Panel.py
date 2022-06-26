import pandas as pd
import numpy as np
from common_import import raw_dir, data_dir,tax_dir
from helper_functions import hh_consumption, prep_product_data, hh_cols, remove_outlier, tax_per_hh, get_ethanol_totals

#  Inputs
fn_bins =  raw_dir /'nielsen_income_bins.xlsx'
fn_category = raw_dir / 'category_list.xlsx'
fn_taxes = data_dir /'states_taxes.parquet'

# Nielsen Data
fn_purchases = data_dir /'purchases'
fn_hh = data_dir / 'revision_panelists.parquet'
fn_prod = data_dir /'revision_products.parquet'

# Outputs
fn_sin_data = data_dir / 'sin_goods_all_years.parquet'
fn_panel = data_dir / 'panel_data_all_years.parquet'

# Constants
ix_cols = ['household_code', 'panel_year']

## Read in Raw Data and aggregate to annual household level consumption
# Uses around 8GB and runs in around 3 min
# Mark all sin consumption + toilet tissue + yogurt
df_prod = prep_product_data(fn_prod, fn_category)

df = pd.concat([hh_consumption(fn_hh, fn_purchases, fn_bins, df_prod, year=y)
 		for y in range(2007,2020+1)], ignore_index=True)
df.to_parquet(fn_sin_data, compression='snappy')

# Can save if necessary --> everything below runs on laptop
# ## This part only takes 5 seconds
# drop the "other" categories
# Reshaping totals by HH/year
# adding taxes
df_panel = pd.merge(pd.merge(
	  df.query("category != 'other'")\
		.groupby(ix_cols+['subcate'])['total_volume'].sum()\
		.unstack()\
		.fillna(0)\
		.rename_axis(None, axis=1),
	get_ethanol_totals(df), on=ix_cols ,how='left'),
	df.groupby(ix_cols)[hh_cols].nth(0), on=ix_cols)\
	.pipe(remove_outlier, al_ub=73, tb_ub=1095)\
	.pipe(tax_per_hh, fn_cig_taxes, fn_al_taxes)

df_panel.to_parquet(fn_panel, compression='snappy')