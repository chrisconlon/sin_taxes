import numpy as np
import pandas as pd
import pathlib as path

from sklearn.cluster import KMeans
from scipy.stats import zscore
from common_import import raw_dir, data_dir, cluster_order, tab_dir, write_tex_table


# Input
fn_clusters = data_dir / 'cluster_data_all_years.parquet'

# Output
fn_table_out = tab_dir / 'table3.tex'

df =  pd.read_parquet(fn_clusters)
df['weighted_tax']=df['projection_factor']*df['total_tax_but_ssb']
df['weighted_ssb']=df['projection_factor']*df['ssb_tax']


x = df.groupby(['panel_year','clusters'])['projection_factor'].sum()
z = (100.*x/x.groupby(level=0).sum()).unstack().transpose().loc[cluster_order,:]
z.columns.name=None
z.index.name = None


x2 = df.groupby(['panel_year','clusters'])['weighted_tax'].sum()
z2 = (100.*x2/x2.groupby(level=0).sum()).unstack().transpose().loc[cluster_order,:]
z2.columns.name=None
z2.index.name = None

x3 = df.groupby(['panel_year','clusters'])['weighted_tax','projection_factor'].sum()
z3 = (x3['weighted_tax']/x3['projection_factor']).unstack().transpose().loc[cluster_order,:]
z3.columns.name=None
z3.index.name = None


x4= df.groupby(['panel_year','clusters'])['weighted_ssb','projection_factor'].sum()
z4 = (x4['weighted_ssb']/x4['projection_factor']).unstack().transpose().loc[cluster_order,:]
z4.columns.name=None
z4.index.name = None






def get_one(df, p=.99):
    return 1-df[df.pop_cum>p]['tax_cum'].min()

def one_year(df, y=2018, col = 'total_tax_but_ssb'):
    tmp = df.loc[df.panel_year==y].copy()
    tmp['tax_w']=tmp[col]*tmp['projection_factor']
    tmp = tmp.sort_values('tax_w')
    tmp['tax_cum']=(tmp['tax_w']/tmp['tax_w'].sum()).cumsum()
    tmp['pop_cum']=(tmp['projection_factor']/tmp['projection_factor'].sum()).cumsum()
    
    return pd.Series({'panel_year':y,
            'Top 1\%': get_one(tmp,.99),
            'Top 5\%': get_one(tmp,.95),
            'Top 10\%': get_one(tmp,.90),
            'Top 15\%': get_one(tmp,.85),
            'Less than \$10':tmp[tmp[col]<10]['projection_factor'].sum()/tmp['projection_factor'].sum(),
            'Between \$10-\$25':tmp[(tmp[col]>10)&(tmp[col]<25)]['projection_factor'].sum()/tmp['projection_factor'].sum(),
            'Between \$25-\$100':tmp[(tmp[col]>25)&(tmp[col]<100)]['projection_factor'].sum()/tmp['projection_factor'].sum(),
            'Between \$100-\$250':tmp[(tmp[col]>100)&(tmp[col]<250)]['projection_factor'].sum()/tmp['projection_factor'].sum(),
            'Greater than \$250':tmp[tmp[col]>250]['projection_factor'].sum()/tmp['projection_factor'].sum(),
       })

totals = pd.concat([one_year(df,y) for y in range (2007, 2020+1)],axis=1)
totals.columns = totals.loc['panel_year'].astype(int)
totals = totals.iloc[1:]*100

partition1 = """
\multicolumn{14}{c}{Fraction of Each Type}\\\\
\midrule"""

partition2 = """\midrule
\multicolumn{14}{c}{Average Taxes Per Year}\\\\
\midrule"""


partition2b = """\midrule
\multicolumn{14}{c}{Hypothetical SSB Taxes Per Year}\\\\
\midrule"""


partition3 = """\midrule
\multicolumn{14}{c}{Share of Taxes Paid by}\\\\
\midrule"""



partition4 ="""\midrule
\multicolumn{14}{c}{Fraction of Households By Annual Burden}\\\\
\midrule"""

latex=pd.concat([z,z3,z4,totals]).to_latex(float_format="%.1f", escape=False)
latex_list=latex.splitlines()
latex_list.insert(-7,partition4)
latex_list.insert(-12,partition3)
latex_list.insert(20,partition2b)
latex_list.insert(12,partition2)
latex_list.insert(4,partition1)

latex_new = '\n'.join(latex_list)
print(latex_new)
print('\n'*2)


write_tex_table(latex_new, fn_table_out)


totals2 = pd.concat([one_year(df,y,'total_tax') for y in range (2007, 2020+1)],axis=1)
totals2.columns = totals2.loc['panel_year'].astype(int)
totals2 = totals2.iloc[1:]*100
totals2.round(1)
