import numpy as np
import pandas as pd
import pathlib as path

from common_import import raw_dir, data_dir,tab_dir,fig_dir,write_tex_table,weighted_quantile

fn_clusters = data_dir / 'cluster_data_all_years.parquet'
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)

df = pd.read_parquet(fn_clusters)
fn_table_out = tab_dir/"tableD2.tex"


def table(df,char,tax_cate):

    quantiles = [0.25,0.5,0.75,0.9,0.95]

    quantile_df=df.groupby(char).apply(lambda g: 
        pd.Series(weighted_quantile(g[tax_cate], quantiles, g.projection_factor), 
        index=['tax '+str(int(100*q))+'%' for q in quantiles]))

    mean_df=df.groupby(char).apply(lambda g:
        pd.Series(np.average(g[tax_cate], axis=0, weights=g['projection_factor']),
        index=['mean']))

    if char == 'race':
        idx = ['White','Black','Asian','Other']
        df = pd.concat([quantile_df,mean_df],axis=1).reindex(idx)
    else:
        idx = [True,False]
        df = pd.concat([quantile_df,mean_df],axis=1).reindex(idx).rename(columns={True:'Hispanic',False:'Nonhispanic'})
    return df


tb = table(df,'race','total_tax_but_ssb')
latex1 =tb.to_latex(float_format="%.2f").splitlines()
latex1.insert(2,'\\multicolumn{7}{l}{\\textbf{Panel A: Existing Sin Taxes on Alcohol and Tobacco}}'+ ' \\\\')
del latex1[4]

tb = table(df,'race','total_tax')
latex2 = tb.to_latex(float_format="%.2f").splitlines()
latex2.insert(2,'\\multicolumn{7}{l}{\\textbf{Panel B: Existing Sin Taxes + SSB Taxes}}'+ ' \\\\')
del latex2[4]

tb = table(df,'Hispanic_Origin','total_tax_but_ssb')
tb.index=['Hispanic','Nonhispanic']
latex3 = tb.to_latex(float_format="%.2f").splitlines()
latex3.insert(2,'\\multicolumn{7}{l}{\\textbf{Panel C: Existing Sin Taxes on Alcohol and Tobacco}}'+ ' \\\\')
# del latex3[4]

tb = table(df,'Hispanic_Origin','total_tax')
tb.index=['Hispanic','Nonhispanic']
latex4 = tb.to_latex(float_format="%.2f").splitlines()
latex4.insert(2,'\\multicolumn{7}{l}{\\textbf{Panel D: Existing Sin Taxes + SSB Taxes}}'+ ' \\\\')
# del latex4[4]

latex1 = latex1 + latex2 + latex3 + latex4

latex_new = '\n'.join(latex1)

write_tex_table(latex_new, fn_table_out)
