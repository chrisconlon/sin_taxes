import numpy as np
import pandas as pd
import pathlib as path
from common_import import raw_dir, data_dir,tab_dir, cluster_order, write_tex_table
from odds_helper import add_them_all, add_them_all1, bootstrap

#input
df = pd.read_parquet( data_dir / 'cluster_data_all_years.parquet').query("panel_year == 2018")

#output
fn_table_out = tab_dir / 'table2.tex'
fn_table_out1 = tab_dir / 'tableD5.tex'
fn_table_out2 = tab_dir / 'tableD7.tex'


tb = add_them_all(df)
# print(tb.round(2).to_latex())

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

def style_positive_bw(value):
	return bool_matrix_up.applymap(lambda x: 'cellcolor:[HTML]{C0C0C0}' if x else '')

def style_negative_bw(value):
	return bool_matrix_lw.applymap(lambda x: 'cellcolor:[HTML]{979797}' if x else '')


# Main Table
rslt_tb = tb.style.format("{:.2f}").apply(style_positive_bw, axis=None).apply(style_negative_bw, axis=None)
latex=rslt_tb.to_latex()
latex_list=latex.splitlines()
latex_list[2] = 'Baseline probability & 0.025 & 0.055 & 0.067 & 0.071 & 0.070 & 0.094 & 0.440 & 0.178' + ' \\\\'
# add some dividers
latex_list[2:2] = ['\\midrule']
latex_list[4:4] = ['\\midrule']
latex_new = '\n'.join(latex_list)
write_tex_table(latex_new, fn_table_out)


# Appendix D
tb = add_them_all1(df)
latex1 = tb.to_latex(float_format="%.2f").splitlines()
del latex1[3]
latex_new = '\n'.join(latex1)
write_tex_table(latex_new, fn_table_out1)
