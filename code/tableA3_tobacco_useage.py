import numpy as np
import pandas as pd
import pyreadstat
import pathlib as path
from common_import import raw_dir, data_dir,tab_dir,fig_dir,write_tex_table

#This table compares average daily cigarette consumption according to the Current Population Survey Tobacco Use Supplement (TUS) 
#https://cancercontrol.cancer.gov/brp/tcrb/tus-cps/questionnaires-data\#2018
# to average daily Nielsen purchases per adult and household. 

df_panel = pd.read_parquet(data_dir/'panel_data_all_years.parquet').query("panel_year==2018")

fn_table_out = tab_dir / 'tableA3.tex'

# # Read the sas7bdat file
# df, meta = pyreadstat.read_sas7bdat(raw_dir/tobacco_survey/'tobacco_survey.sas7bdat')
# df = df[['HRHHID','PTB1','PEB1A']]

# df['smoking']=df['PTB1']
# df.loc[df.PTB1 == -1, 'smoking'] = 0
# refused = df[(df.PTB1.isin([-3,-2,-9])) & (df.PEB1A.isin([-3,-2,-9]))]
# no_answer = refused['HRHHID'].to_list()
# print(df.shape)

# df = df[~df.HRHHID.isin(no_answer)]

# df.loc[df.PEB1A == 1, 'smoking'] = 40
# df.loc[df.PEB1A == 2, 'smoking'] = 10
# df.loc[df.PEB1A == 3, 'smoking'] = 20


temp = df_panel[df_panel.cigars == 0]
print(temp.shape)
print(df_panel.shape)
df_panel['smoking'] = np.round((df_panel['cigars']*20)/365,3)
df_panel['smoking per capita'] = np.round(((df_panel['cigars']*20)/df_panel['Adult'])/365,3)


to_compare = []
from_panel = []
from_panel1 = []
for c in [0.95,0.96,0.97,0.98,0.99,1]:
	to_compare.append(df_panel['smoking'].quantile(c))
	from_panel.append(df_panel['smoking per capita'].quantile(c))
        #from_panel1.append(df_panel['smoking per capita'].quantile(c))

print(to_compare)
print(from_panel)
# print(from_panel1)
TUS = [0,0,4,10,20,40]
adult = from_panel
hh = to_compare
idx = ['95%','96%','97%','98%','99%','Max']
df = pd.DataFrame({'idx':idx,'TUS':TUS,'Nielsen (per adult)':adult,'Nielsen (per Household)':hh})\
				.set_index('idx')
latex=df.to_latex(float_format="%.3f")
write_tex_table(latex, fn_table_out)
