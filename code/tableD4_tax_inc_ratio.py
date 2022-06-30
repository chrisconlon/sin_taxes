import numpy as np
import pandas as pd
import pathlib as path
from common_import import raw_dir, data_dir,tab_dir,fig_dir,cluster_order,write_tex_table,weighted_quantile


#Input
fn_clusters = data_dir / 'cluster_data_all_years.parquet'
df = pd.read_parquet(fn_clusters)
#Output
fn_table_out = tab_dir/"tableD4.tex"

def table2(df,tax_cate):

    df['inc/tax'] = 100*df[tax_cate]/df['median_income']

    quantiles = [0.25,0.5,0.75,0.9,0.95]

    quantile_df=df.groupby('clusters').apply(lambda g: 
        pd.Series(weighted_quantile(g['inc/tax'], quantiles, g.projection_factor), 
        index=['ratio '+str(int(100*q))+'%' for q in quantiles])).transpose()

    quantile_df.columns.name = ''

    mean_df=df.groupby('clusters').apply(lambda g:
        pd.Series(np.average(g['inc/tax'], axis=0, weights=g['projection_factor']),
        index=['mean'])).transpose()

    fnl = pd.concat([quantile_df,mean_df],axis=0)

    min_df=df.groupby('clusters').apply(lambda g:
        pd.Series(min(g['inc/tax']),
        index=['min'])).transpose()

    fnl = pd.concat([min_df,fnl],axis=0)

    max_df=df.groupby('clusters').apply(lambda g:
        pd.Series(max(g['inc/tax']),
        index=['max'])).transpose()
    fnl = pd.concat([fnl,max_df],axis=0)

    return fnl[cluster_order]

tb = table2(df,'total_tax_but_ssb')
latex1 =tb.to_latex(float_format="%.3f").splitlines()
latex1.insert(2,'\\multicolumn{9}{l}{\\textbf{Panel A: Existing Sin Taxes on Alcohol and Tobacco}}'+ ' \\\\')
    
tb = table2(df,'total_tax')
latex2 =tb.to_latex(float_format="%.3f").splitlines()
latex2.insert(2,'\\multicolumn{9}{l}{\\textbf{Panel B: Existing Sin Taxes Plus New Taxes on SSBs}}'+ ' \\\\')

###Potential extra $1 in cigarette
#Adjustment for panel A: existing sin taxes on alcohol and tobacco
df['total_tax_but_ssb'] = df['total_tax_but_ssb'] + 1*df['cigars']
df['total_tax'] = df['total_tax'] + 1*df['cigars']

tb = table2(df,'total_tax_but_ssb')
latex3 =tb.to_latex(float_format="%.3f").splitlines()
latex3.insert(2,'\\multicolumn{9}{l}{\\textbf{Panel A1: Existing Sin Taxes with potential \$1 increase in tobacco tax}}'+ ' \\\\')

# Adjustment for panel B: existing sin taxes plus new taxes on SSBs
tb = table2(df,'total_tax')
latex4 =tb.to_latex(float_format="%.3f").splitlines()
latex4.insert(2,'\\multicolumn{9}{l}{\\textbf{Panel B1: Existing Sin Taxes Plus New Taxes on SSBs with potential \$1 increase in tobacco tax}}'+ ' \\\\')



latex1 = latex1 + latex2 + latex3 + latex4

latex_new = '\n'.join(latex1)

write_tex_table(latex_new, fn_table_out)
