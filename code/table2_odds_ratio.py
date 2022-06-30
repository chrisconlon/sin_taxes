import numpy as np
import pandas as pd
import pathlib as path
from common_import import raw_dir, data_dir,tab_dir,cluster_order,write_tex_table
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)

main_dir = path.Path('/Users/yinanwang/Dropbox/sin_tax_project/proc_data/')
#input
df = pd.read_parquet( data_dir / 'cluster_data_all_years.parquet').query("panel_year == 2018")
#output
fn_table_out = tab_dir / 'table2.tex'
fn_table_out1 = tab_dir / 'tableD5.tex'
fn_table_out2 = tab_dir / 'tableD7.tex'

def char_odd_ratio(df,c):	
	fnl = pd.DataFrame()


	char_in_cluster = df.groupby(['clusters',c]).agg({'projection_factor': 'sum'})
	# print(char_in_cluster)


	char_pcts = char_in_cluster.groupby(level=0).apply(lambda x:
												  x / float(x.sum())).reset_index()
	# print(char_pcts)
	
	temp = df.groupby([c])['projection_factor'].sum().reset_index()
	temp['share'] = temp['projection_factor']/temp['projection_factor'].sum()


	temp = temp[[c,'share']]

	char_pcts = pd.merge(char_pcts,temp,on=[c])
	char_pcts['projection_factor'] =char_pcts['projection_factor'] /char_pcts['share']
	
	# print(char_pcts)

	char_pcts = pd.pivot_table(char_pcts, values='projection_factor',index = c,
						columns=['clusters'], aggfunc=np.mean)
	
	# clusters_lst.insert(0,c)
	# print(char_pcts)

	char_pcts = char_pcts.reset_index().rename(columns={c: "char"})
	char_pcts.index.name = None


	return char_pcts[['char']+cluster_order]

def add_them_all(df):
	x = df.groupby(['clusters'])['projection_factor'].sum()

	char_list = ['race','Hispanic_Origin','presence_child','age_group','income_group','edu_group']
	tb = pd.concat([char_odd_ratio(df,c) for c in char_list], ignore_index=True)
	
	tb = tb.reset_index().reindex([3,1,0,2,4,5,7,6,12,8,9,10,11,16,13,14,15,17,19,21,18,20])

	tb['index'] = ['Race: White (74.9\%)','Race: Black (12.5\%)','Race: Asian (4.4\%)','Race: Other (8.2\%)','Hispanic: No (86.8\%)','Hispanic: Yes (13.2\%)',
		'Children: Yes (31.3\%)','Children: No (68.7\%)',
	  'Age: $<$ 35 (12.9\%)', 'Age: 35 to 44 (18.0\%)', 'Age: 45 to 54 (21.8\%)', 'Age: 55 to 64 (22.7\%)','Age: $>$ 65 (24.6\%)',
	  'Income: $<$ 24,999 (20.4\%)','Income: 25,000 - 44,999 (17.7\%)',
	  'Income: 45,000-69,999 (18.2\%)','Income: 70,000-99,999 (15.5\%)','Income: $>$ 100,000 (28.1\%)',
	  'Edu: High School or less (27.4\%)','Edu: Some College (31.4\%)','Edu: Graduated College (26.3\%)',
	  'Edu: Post College Grad (14.9\%)']

	return tb.set_index(['index']).drop(columns=['char'])

tb = add_them_all(df)
# print(tb.round(2).to_latex())

def bootstrap(df,times = 1000):
	lsts = []

	
	for i in range(times):
		temp = df.sample(frac=1, replace=True)
		temp_rslt = add_them_all(temp)
		lsts.append(temp_rslt)
	
	rslt_CI = lsts[-1].copy().astype(str)
	rslt_mu = lsts[-1].copy()
	
	for c in range(8):
		for d in range(22):
			tt = []
			for i in range(times):

	
				tt.append(lsts[i].iloc[d][c])
			
			low = np.quantile(tt,0.025).round(2)
			high = np.quantile(tt,0.975).round(2)

			rslt_CI.iloc[d][c] = (low,high)
			rslt_mu.iloc[d][c] = np.mean(tt).round(2)

	# rslt_CI = rslt_CI[cls]
	# rslt_mu = rslt_mu[cls]
	

	return rslt_CI,rslt_mu

print("Start with bootstrap")
CI, MU = bootstrap(df,1000)
# print(CI.to_latex())
# print(MU.to_latex())
latex2=CI.to_latex(float_format="%.2f").splitlines()
del latex2[3]
latex_new = '\n'.join(latex2)
write_tex_table(latex_new, fn_table_out2)

bool_matrix_up = CI.applymap(lambda x: x[0]>1.1)
bool_matrix_lw = CI.applymap(lambda x: x[1]<0.9)

def style_positive(value):
# 	return bool_matrix_up.applymap(lambda x: 'background-color: lightblue' if x else '')
	return bool_matrix_up.applymap(lambda x: 'cellcolor:[HTML]{89CFF0}' if x else '')

def style_negative(value):
# 	return bool_matrix_lw.applymap(lambda x: 'background-color: lightcoral' if x else '')
	return bool_matrix_lw.applymap(lambda x: 'cellcolor:[HTML]{E4717A}' if x else '')

def style_positive_bw(value):
	return bool_matrix_up.applymap(lambda x: 'cellcolor:[HTML]{C0C0C0}' if x else '')

def style_negative_bw(value):
	return bool_matrix_lw.applymap(lambda x: 'cellcolor:[HTML]{979797}' if x else '')


rslt_tb = tb.style.format("{:.2f}").apply(style_positive_bw, axis=None).apply(style_negative_bw,axis=None)
latex=rslt_tb.to_latex()
latex_list=latex.splitlines()
latex_list[2] = 'Baseline probability & 0.025 & 0.055 & 0.067 & 0.071 & 0.070 & 0.094 & 0.440 & 0.178' + ' \\\\'
# add some dividers
latex_list[2:2] = ['\\midrule']
latex_new = '\n'.join(latex_list)
write_tex_table(latex_new, fn_table_out)

# print(rslt_tb.to_latex())
# print(rslt_tb)



def char_share(df,c):	
	fnl = pd.DataFrame()


	char_in_cluster = df.groupby(['clusters',c]).agg({'projection_factor': 'sum'})
	# print(char_in_cluster)


	char_pcts = char_in_cluster.groupby(level=0).apply(lambda x:
												  x / float(x.sum())).reset_index()

	
	temp = df.groupby([c])['projection_factor'].sum().reset_index()
	temp['share'] = temp['projection_factor']/temp['projection_factor'].sum() #share within sample


	temp = temp[[c,'share']]

	char_pcts = pd.merge(char_pcts,temp,on=[c])


	char_pcts = pd.pivot_table(char_pcts, values='projection_factor',index = c,
						columns=['clusters'], aggfunc=np.mean)
	

	char_pcts = char_pcts.reset_index().rename(columns={c: "char"})
	char_pcts.index.name = None


	return char_pcts[['char']+cluster_order]

def add_them_all1(df):
	x = df.groupby(['clusters'])['projection_factor'].sum()

	char_list = ['race','Hispanic_Origin','presence_child','age_group','income_group','edu_group']
	tb = pd.concat([char_share(df,c) for c in char_list], ignore_index=True)
	
	tb = tb.reset_index().reindex([3,1,0,2,4,5,7,6,12,8,9,10,11,16,13,14,15,17,19,21,18,20])

	tb['index'] = ['Race: White (74.9%)','Race: Black (12.5%)','Race: Asian (4.4%)','Race: Other (8.2%)','Hispanic: No (86.8%)','Hispanic: Yes (13.2%)',
		'Children: Yes (31.3%)','Children: No (68.7%)',
	  'Age: $<$ 35 (12.9%)', 'Age: 35 to 44 (18.0%)', 'Age: 45 to 54 (21.8%)', 'Age: 55 to 64 (22.7%)','Age: $>$ 65 (24.6%)',
	  'Income: $<$ 24,999 (20.4%)','Income: 25,000 - 44,999 (17.7%)',
	  'Income: 45,000-69,999 (18.2%)','Income: 70,000-99,999 (15.5%)','Income: $>$ 100,000 (28.1%)',
	  'Edu: High School or less (27.4%)','Edu: Some College (31.4%)','Edu: Graduated College (26.3%)',
	  'Edu: Post College Grad (14.9%)']
	

	return tb.set_index(['index']).drop(columns=['char'])

tb = add_them_all1(df)
latex1 = tb.to_latex(float_format="%.2f").splitlines()
del latex1[3]
latex_new = '\n'.join(latex1)
write_tex_table(latex_new, fn_table_out1)
