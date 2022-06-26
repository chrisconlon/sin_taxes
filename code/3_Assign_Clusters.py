import numpy as np
import pandas as pd
import pathlib as path

from sklearn.cluster import KMeans
from scipy.stats import zscore
from common_import import raw_dir, data_dir
from cluster_helpers import fit_only, predict_only, fit_all_years, high, medium, low, calc_external_damage


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
	df2[['household_code','panel_year','clusters']].rename(columns={'clusters':'cluster_by_year'}),
	on=['household_code','panel_year'])
df4=pd.merge(df3,
	df3.query('panel_year==2018')[['household_code','clusters']]\
	.rename(columns={'clusters':'cluster_2018'})
	,on='household_code',how='left')


df4['externality_med'] =calc_external_damage(df['ethanol']/df['Adult'],**medium)
df4['externality_high']=calc_external_damage(df['ethanol']/df['Adult'],**high)
df4['externality_low'] =calc_external_damage(df['ethanol']/df['Adult'],**low)

df4.to_parquet(fn_clusters)


def stable_metric(Y1,Y2,df3):
	new_col_name = 'cluster_'+str(Y2)
	df4=pd.merge(df3,
	df3.query('panel_year==@Y2')[['household_code','clusters']]\
	.rename(columns={'clusters':new_col_name})
	,on='household_code',how='left')

	print("dropping ",df4[new_col_name].isna().sum()/df4.shape[0])

	# Junk at end
	x=pd.crosstab(df4.clusters, df4[new_col_name])
	y=x.sum()/x.sum().sum()
	print(np.dot(np.diag((100.*x.div(x.sum(axis=1),axis=0))),y))

	print("Start!")

	x2=pd.crosstab(df4.query('panel_year==@Y1').clusters, df4.query('panel_year==@Y1')[new_col_name])
	print((100.*x2.div(x2.sum(axis=0),axis=1)).round(2))
	print((100.*x2.div(x2.sum(axis=1),axis=0)).round(2))

# stable_metric(2019,2020,df3)

# # Junk at end
# 	x=pd.crosstab(df4.clusters, df4.cluster_2018)
# 	y=x.sum()/x.sum().sum()
# 	print(np.dot(np.diag((100.*x.div(x.sum(axis=1),axis=0))),y))

# 	print("Start!")
# 	print((100.*x.div(x.sum(axis=1),axis=0)).round(2))
# 	df_pivot= df3.pivot('household_code', columns='panel_year',values='clusters')


# 	x2=pd.crosstab(df4.query('panel_year==2007').clusters, df4.query('panel_year==2007').cluster_2018)
# 	print((100.*x2.div(x2.sum(axis=1),axis=0)).round(2))

# 	x2=pd.crosstab(df4.query('panel_year==2007').clusters, df4.query('panel_year==2019').clusters)
# 	print((100.*x2.div(x2.sum(axis=1),axis=0)).round(2))