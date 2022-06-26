import numpy as np
import pandas as pd
import pathlib as path
import statsmodels.api as sm
from common_import import data_dir,tab_dir,write_tex_table
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)



df = pd.read_parquet(data_dir / 'cluster_data_all_years.parquet').query("panel_year==2018")
fn_table_out = tab_dir/'tableD6.tex'

d = {'Nothing':0, 'Everything':1, 'Smokers':2, 'Heavy Drinkers':3,'Moderate Spirits':4, 'Mostly Wine':5,  'Moderate Beer':6, 'SSB only':7}
# df['clusters'] = pd.Categorical(df['clusters'])
# d = dict(enumerate(df['clusters'].cat.categories))
# df['clusters'] = df['clusters'].cat.codes
# print (df.dtypes)
df['clusters'] = df['clusters'].map(d).astype(int)


logit_model=sm.MNLogit.from_formula(formula="clusters~ C(edu_group,Treatment(reference='Graduated College'))+C(race,Treatment(reference='White'))+C(Hispanic_Origin,Treatment(reference=False))+C(age_group,Treatment(reference='over_65'))\
								+C(presence_child,Treatment(reference=False))+C(income_group,Treatment(reference='45,000-69,999'))"
									,data= df).fit(method='powell')


stats1=logit_model.summary()
# print(stats1)

# print(stats1.as_latex())

tb_coeff = logit_model.params.round(4)
tb_se = logit_model.bse.round(3)

idx = ['Intercept','Edu: High School or Less','Edu: Post College Grad','Edu: Some College',
		'Race: Asian','Race: Black','Race: Other','Hispanic: Yes','Age: 35 - 44',
		'Age: 45 - 54','Age: 55 - 64','Age: Under 35 ','Children: Yes',
		'Income: 25,000 - 44,999','Income: 70,000 - 99,999','Income: $<$ 24,999','Income: $>$ 100,000']

tb_coeff.index = idx
tb_se.index = idx
col_dict1 = {0:'Everything coef',1:'Smokers coef',2:'Heavy Drinkers coef',3:'Moderate Spirits coef',
				4:'Mostly Wine coef',5:'Moderate Beer coef',6:'SSB only coef'}

col_dict2 = {0:'Everything se',1:'Smokers se',2:'Heavy Drinkers se',3:'Moderate Spirits se',
				4:'Mostly Wine se',5:'Moderate Beer se',6:'SSB only se'}

tb_coeff = tb_coeff.rename(columns=col_dict1)
tb_se = tb_se.rename(columns=col_dict2)

all_tb = pd.concat([tb_coeff, tb_se], axis=1)
top_panel = all_tb[['Everything coef','Everything se','Smokers coef','Smokers se','Heavy Drinkers coef','Heavy Drinkers se',
						'Moderate Spirits coef','Moderate Spirits se']]
bottom_panel = all_tb[['Mostly Wine coef','Mostly Wine se','Moderate Beer coef','Moderate Beer se','SSB only coef','SSB only se']]


latex1 = top_panel.to_latex().splitlines()
latex1[0] = '\\begin{tabular}{l|cc| cc| cc| cc}'
latex1.insert(2,'& \\multicolumn{2}{c}{\textbf{cluster = Everything} } &\\multicolumn{2}{c}{\textbf{cluster = Smokers} } \
						&  \\multicolumn{2}{c}{\textbf{cluster = Heavy Drinkers} } &\\multicolumn{2}{c}{\textbf{cluster = Moderate Spirits} }'+ ' \\\\')
latex1[3] = '& coef & std err & coef & std err & coef & std err & coef & std err'+ ' \\\\'
latex1[-2] = '\\midrule'
del latex1[-1]

latex2 = bottom_panel.to_latex().splitlines()
latex2[0] = '& \\multicolumn{2}{c}{\textbf{cluster = Mostly Wine} } &\\multicolumn{2}{c}{\textbf{cluster = Moderate Beer} } &  \\multicolumn{2}{c}{\textbf{cluster = SSB only} }'+ ' \\\\'
latex2[1] = '& coef & std err & coef & std err & coef & std err'+ ' \\\\'
del latex2[2]

latex_new = '\n'.join(latex1+latex2)
write_tex_table(latex_new, fn_table_out)

