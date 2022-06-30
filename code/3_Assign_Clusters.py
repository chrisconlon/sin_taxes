import numpy as np
import pandas as pd
import pathlib as path

from common_import import data_dir
from cluster_helpers import (fit_only, predict_only, fit_all_years,
 	calc_external_damage, high, medium, low)

# Inputs
fn_panel = data_dir / 'panel_data_all_years.parquet'

# Outputs
fn_clusters = data_dir / 'cluster_data_all_years.parquet'

# # first fit 2018 only then use these centroids for all years
kmeans_2018, clusters_name, means, stdev = fit_only(fn_panel ,2018, n_clusters=8)
df = pd.concat([predict_only(fn_panel, y, kmeans_2018, clusters_name, means, stdev) for y in range(2007,2020+1)], ignore_index=True)

# # first fit k-means on 2018 data --> then that centroid for other years
#_, kmeans2, clusters_name2, = fit_all_years(2018, fitted_object = False)
df2 = pd.concat([fit_all_years(fn_panel, y)[0] for y in range(2007,2020+1)], ignore_index=True)

# Save both cluster assignments
df3=pd.merge(df, 
	df2[['household_code','panel_year','clusters']]\
	.rename(columns={'clusters':'cluster_by_year'}),
	on=['household_code','panel_year'])

df4=pd.merge(df3,
	df3.query('panel_year==2018')[['household_code','clusters']]\
	.rename(columns={'clusters':'cluster_2018'})
	,on='household_code',how='left')

df4['externality_med']  = calc_external_damage(df['ethanol']/df['Adult'],**medium)
df4['externality_high'] = calc_external_damage(df['ethanol']/df['Adult'],**high)
df4['externality_low']  = calc_external_damage(df['ethanol']/df['Adult'],**low)

df4.to_parquet(fn_clusters)