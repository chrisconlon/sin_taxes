import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from scipy.stats import zscore
from common_import import np_wavg

# Global options
consumption_cols = ['beer','wine','liquor','cigars','carbonated','ethanol']

# externality levels from Griffiths et al
low ={'phi_0': 3.1730, 'phi_1': 0.0435}
medium ={'phi_0':1.298, 'phi_1':.0615}
high ={'phi_0': 0.8177, 'phi_1':0.0695}

# Dict for labels based on old estimates of centroids
means_dict = {
'beer': {0: 2.1060834790514527, 1: 3.514667427629032, 2: 100.01477931106137, 3: 1.2129664436079024, 4: 16.756275618818137, 5: 70.41480412535472, 6: 4.039233244554953, 7: 154.11392062874478},
'wine': {0: 0.7413031151557578, 1: 2.210674702886248, 2: 38.93894573036356, 3: 1.7332894925515814, 4: 49.999252528564625, 5: 2.061445348506401, 6: 3.5717339762909384, 7: 22.9058249651325},
'liquor': {0: 0.7206001666083304, 1: 0.9055927232597623, 2: 30.61805444894524, 3: 0.42825677320162514, 4: 1.9713232125684361, 5: 1.2917574847083926, 6: 10.929364043399637, 7: 22.91794231520223},
'cigars': {0: 139.32070476023802, 1: 0.23530755517826826, 2: 0.23135424147217237, 3: 0.18170564805225842, 4: 0.35602178052844563, 5: 0.28441500711237555, 6: 0.23784207353827608, 7: 158.66543654114366},
'carbonated': {0: 158.91546920230311, 1: 4.053692393103141, 2: 85.37417999517481, 3: 110.21910713459498, 4: 40.13120076595572, 5: 97.64989635452578, 6: 105.49089467242294, 7: 156.12856879756276},
'ethanol': {0: 0.3244796831936472, 1: 0.6387621032585866, 2: 18.84667487792292, 3: 0.35390502737173984, 4: 7.760392219412514, 5: 3.7227898077248884, 6: 3.017582455904511, 7: 16.454732195476222}
}
model_means = pd.DataFrame(means_dict)
model_means.index = ['Smokers', 'Nothing', 'Heavy Drinkers', 'SSB only','Mostly Wine','Moderate Beer','Moderate Spirits','Everything']



def calc_external_damage(z, phi_0=1.298, phi_1=.0615):
    return phi_0 * (np.exp(z*phi_1)-1)



def name_clusters(cluster_new, model_means, n_clusters=8):
	rslt_dist = {}

	for idx1, row1 in cluster_new.iterrows():
		to_comp = np.tile(np.array(row1),(n_clusters,1))
		# rslt_dist[idx1] = np.sum(to_comp!=np.array(model_means),axis=1) 
		rslt_dist[idx1] = np.sum(np.abs(to_comp - np.array(model_means)),axis=1)
	
	rslt_df = pd.DataFrame(rslt_dist, index=model_means.index).idxmin()

	return {v: k for v, k in enumerate(rslt_df)}

def inv_hyper_sine(x):
	return np.log(x+np.sqrt(x**2+1))

# Use df mean and std or provided one (from a different sample)
def standardize_columns(df, means=pd.Series(dtype='float64'), stdev=pd.Series(dtype='float64'), cluster_cols=consumption_cols):
	X = inv_hyper_sine(df[consumption_cols])
	if means.empty:
		means = np_wavg(X, consumption_cols,df['projection_factor'])
		stdev = np.sqrt(np_wavg((X-means)**2, consumption_cols,df['projection_factor']))
	return  (X-means)/stdev, means, stdev


def fit_all_years(fn_panel, y, fitted_object = False, clusters_name=None, n_clusters=8):
	df = pd.read_parquet(fn_panel).query("panel_year == @y")
	
	# split the zeros
	zeros_mask = (df[['beer','wine','liquor','cigars']]>0).any(axis=1)
	df_c = df[zeros_mask].copy()
	temp0 = df[~zeros_mask].copy()

	X, means, stdev = standardize_columns(df_c)

	if not fitted_object:
		fitted_object = KMeans(n_clusters=n_clusters, random_state=42).fit(X, sample_weight=df_c.projection_factor)
	
	

	df_c['clusters'] =  fitted_object.predict(X, sample_weight=df_c.projection_factor)

	# Assign cluster names
	all_means = df_c.groupby(['clusters'])[consumption_cols].mean()
	clusters_name = name_clusters(all_means, model_means)
	# all_means.index = all_means.index.map(clusters_name)
	# df_c['clusters'] = df_c['clusters'].map(clusters_name).astype('category')

	df['clusters'] =  fitted_object.predict(standardize_columns(df, means, stdev)[0], sample_weight=df.projection_factor)
	df['clusters'] =df['clusters'].map(clusters_name).astype('category')

	# # Add zeros back
	# divider = df_c[df_c['clusters'] == 'Nothing'].carbonated.max()
	
	# # CC: this would be the MSE minimizing choice --> we should probably use this instead
	# alt_divider = all_means[all_means.index.isin(['SSB only','Nothing'])]['carbonated'].mean()

	# temp0['clusters'] = 'SSB only'
	# temp0.loc[temp0.carbonated <= divider,'clusters'] = 'Nothing'

	# return pd.concat([df_c, temp0], ignore_index = True), fitted_object, clusters_name
	return df,fitted_object, clusters_name

def fit_only(fn_panel, y, n_clusters=8):
	# split the zeros
	df = pd.read_parquet(fn_panel).query("panel_year == @y")
	zeros_mask = (df[['beer','wine','liquor','cigars']]>0).any(axis=1)
	df_c = df[zeros_mask].copy()

	X, means, stdev = standardize_columns(df_c)
	fitted_object = KMeans(n_clusters=n_clusters, random_state=42).fit(X, sample_weight=df_c.projection_factor)
	df_c['clusters'] =  fitted_object.predict(X,df_c.projection_factor)

	all_means = df_c.groupby(['clusters'])[consumption_cols].mean()
	clusters_name = name_clusters(all_means, model_means)
	all_means.index = all_means.index.map(clusters_name)
	print(all_means.round(2))
	return  fitted_object, clusters_name, means, stdev


def predict_only(fn_panel, y, fitted_object, clusters_name, means, stdev):
	df = pd.read_parquet(fn_panel).query("panel_year == @y")
	df['clusters'] =  fitted_object.predict(standardize_columns(df, means, stdev)[0], sample_weight=df.projection_factor)
	df['clusters'] = df['clusters'].map(clusters_name).astype('category')
	return df




