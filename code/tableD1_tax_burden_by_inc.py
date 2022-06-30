import numpy as np
import pandas as pd
import pathlib as path

from common_import import raw_dir, data_dir,tab_dir,fig_dir,write_tex_table


fn_clusters = data_dir / 'cluster_data_all_years.parquet'
fn_table_out = tab_dir/'tableD1.tex'


df = pd.read_parquet(fn_clusters)

# Define a lambda function to compute the weighted mean:
wm = lambda x: np.average(x, weights=df.loc[x.index, "projection_factor"])

df = df.groupby('income_group').agg(Beer_Tax=("beer_tax", wm),Wine_Tax=("wine_tax", wm),
				Spirits_Tax=("spirits_tax", wm), Cigarette_Tax=("cigarette_tax", wm),
				SSB_Tax=("ssb_tax", wm),
				Existing_Tax=("total_tax_but_ssb", wm)).reset_index().round(2)

df = df.reindex([3,0,1,2,4]).reset_index(drop=True)
lst =['ratio',df.iloc[4]['Beer_Tax']/df.iloc[0]['Beer_Tax'],\
		df.iloc[4]['Wine_Tax']/df.iloc[0]['Wine_Tax'],\
		df.iloc[4]['Spirits_Tax']/df.iloc[0]['Spirits_Tax'],\
		df.iloc[4]['Cigarette_Tax']/df.iloc[0]['Cigarette_Tax'],\
		df.iloc[4]['SSB_Tax']/df.iloc[0]['SSB_Tax'],\
		df.iloc[4]['Existing_Tax']/df.iloc[0]['Existing_Tax']]

df.loc[-1] = lst
df.index = df.index+1
latex = df.round(2).sort_index().to_latex(index=False)
write_tex_table(latex, fn_table_out)

