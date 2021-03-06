import pathlib
import pandas as pd
import numpy as np
import pyarrow.dataset as ds
import pyarrow as pa
from common_import import data_dir 
from kiltsreader import PanelReader

## This uses > 100GB of RAM: processing fewer years or categories at once advised on a smaller computer
# takes only 3-5 min on my iMac --> saving is slow

# Point this to the Kilts Nielsen data
kilts_dir = pathlib.Path('/Volumes/T7/nielsen-panelist')

# out files
fn_out_prods = data_dir / 'revision_products.parquet'
fn_out_panelists = data_dir / 'revision_panelists.parquet'
fn_out_purchases = data_dir / 'revision_purchases.parquet'

# save multiple files for purchase data -- to keep things manageable
out_dir = data_dir / "purchases"
out_dir.mkdir(exist_ok=True)


nr = PanelReader(kilts_dir)
nr.filter_years(keep=range(2007, 2020+1))
nr.read_products(keep_groups=[2510,5003,4510,507,1503,5001,4507,5002,1020,1508,2006])
nr.read_extra()
nr.read_variations()
nr.read_annual(add_household=True)
#nr.read_revised_panelists()
nr.process_open_issues()

# drop redundant cols from fixes
nr.df_panelists = nr.df_panelists.drop(columns=['Male_Head_Birth_revised', 'Female_Head_Birth_revised'])

# Write the data partitioned by panel_year (so we can partially read in later)
nr.df_products.to_parquet(fn_out_prods, compression='brotli')
nr.df_panelists.to_parquet(fn_out_panelists, compression='brotli')

# this is a horror show of memory usage and writing takes forever
# drop useless fields
purch_cols = ['trip_code_uc','household_code','upc','upc_ver_uc','quantity','total_price_paid','panel_year']
pa.concat_tables([tab.select(purch_cols) for tab in nr.df_purchases])\
	.to_pandas()\
	.to_parquet(fn_out_purchases, compression='brotli')