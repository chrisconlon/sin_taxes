import numpy as np
import pandas as pd
import pyreadstat
import pathlib as path

from common_import import raw_dir, data_dir,tab_dir,fig_dir,write_tex_table

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 1000)

df_panel = pd.read_parquet(data_dir/'panel_data_all_years.parquet').query("panel_year==2018")

fn_table_out = tab_dir / 'tableA1.tex'

#A standard drink is any drink that contains about 14 grams of pure alcohol (about 0.6 fluid ounces) 
#0.6 Ounces = 0.017744118 Liters
covrt_drink  = 0.017744118


df_panel['drinks_per_week'] = ((df_panel['ethanol']/covrt_drink)/365)*7
df_panel['drinks_per_week_per_capita'] = df_panel['drinks_per_week'] / df_panel['Adult']



from_panel = []
from_panel1 = []

for c in range(1,10):
	from_panel.append(df_panel['drinks_per_week'].quantile(0.1*c))
	from_panel1.append(df_panel['drinks_per_week_per_capita'].quantile(0.1*c))

from_panel.append(df_panel['drinks_per_week'].max())
from_panel1.append(df_panel['drinks_per_week_per_capita'].max())
#Table A1
print("Household",from_panel)
print("Per capita",from_panel1)

NESARC = [0,0,0,0.01,0.07,.32,1.10,3.17,7.76,37.49]
per_cap = from_panel1
hh = from_panel
idx = ['10%','20%','30%','40%','50%','60%','70%','80%','90%','Max']
df = pd.DataFrame({'idx':idx,'NESARC':NESARC,'Nielsen per capita':per_cap,'Nielsen Household':hh})\
				.set_index('idx')
latex=df.to_latex(float_format="%.2f")
write_tex_table(latex, fn_table_out)

