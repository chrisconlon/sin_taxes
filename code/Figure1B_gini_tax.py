import matplotlib.pyplot as plt
import seaborn as sns; sns.set()  # for plot styling
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.cm as cm
import pathlib as path
from common_import import raw_dir, data_dir,tab_dir,fig_dir

df = pd.read_parquet(data_dir/'panel_data_all_years.parquet')
df['alcohol_tax'] = df['beer_tax']+df['wine_tax']+df['spirits_tax']
###GINI PLOT###
#GINI consumption plot

from cycler import cycler
import matplotlib
# Plot Configuration
matplotlib.style.use('seaborn-whitegrid')
matplotlib.rcParams.update({'font.size': 24})
plt.rc('font', size=24)          # controls default text sizes
plt.rc('axes', titlesize=24)     # fontsize of the axes title
plt.rc('axes', labelsize=24)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=24)    # fontsize of the tick labels
plt.rc('ytick', labelsize=24)    # fontsize of the tick labels
plt.rc('legend', fontsize=24)    # legend fontsize
plt.rc('figure', titlesize=24)
#plt.rc('axes', prop_cycle=cycler(color=['008fd5', 'fc4f30', 'e5ae38', '6d904f', '8b8b8b', '810f7c']))
#plt.rc('axes',prop_cycle=cycler(color=['c', 'm', 'y', 'k'], lw=[1, 2, 3, 4]))
#plt.rc('axes',prop_cycle=cycler(color=['#008fd5', '#fc4f30', '#e5ae38', '#6d904f', '#8b8b8b','purple','navy']))
plt.rc('lines', linewidth=3)

#plt.rc('text', usetex=True)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20,10))

def G(v):
	bins = np.linspace(0., 100., 11)
	total = float(np.sum(v))
	yvals = []
	for b in bins:
		bin_vals = v[v <= np.percentile(v, b)]
		bin_fraction = (np.sum(bin_vals) / total) * 100.0
		yvals.append(bin_fraction)
	# perfect equality area
	pe_area = np.trapz(bins, x=bins)
	# lorenz area
	lorenz_area = np.trapz(yvals, x=bins)
	gini_val = ((pe_area - lorenz_area) / float(pe_area)).round(3)
	return bins, yvals, gini_val


def creat_legend(df):
	leg = []
	sin_tax = ['ssb_tax','cigarette_tax','alcohol_tax','total_tax_but_ssb','total_tax']
	#sin_tax = ['beer_tax','spirits_tax','wine_tax','cigarette_tax','ssb_tax','total_tax','total_tax_but_ssb']
	for s in sin_tax:
		_,_, gini_val = G(df[s])
		if s == 'beer_tax':
			s = 'beer tax'
		elif s == 'spirits_tax':
			s = 'spirits tax'
		elif s == 'alcohol_tax':
			s = 'alcohol tax'
		elif s == 'cigarette_tax':
			s = 'cigarette tax'
			# gini_val = '0.900'
		elif s == 'ssb_tax':
			s = 'SSB tax'
		elif s == 'total_tax':
			s = 'SSB + existing sin tax'

		elif s== 'total_tax_but_ssb':
			s = 'existing sin tax'
		l = s+': '+str(gini_val)
		leg.append(l)
	return leg


def get_list_to_draw(df,key):
	temp = df[key]
	lst_y = []
	for i in range(101):
		c = 0.01*i
		consumed = df[df[key]<=temp.quantile(c)][key].sum()
		lst_y.append(consumed/df[key].sum())
	return lst_y

def get_list_to_draw_09(df,key):
	temp = df[key]
	lst_y = []
	for i in range(11):
		c = 0.9+0.01*i
		consumed = df[df[key]<=temp.quantile(c)][key].sum()
		lst_y.append(consumed/df[key].sum())
	return lst_y 

def draw_cdf(df,ax1,ax2):
	sin_taxes = ['ssb_tax','cigarette_tax','alcohol_tax','total_tax_but_ssb','total_tax']
	
	x1 = np.linspace(0,1,101)
	x2 = np.linspace(0.9,1,11)
	for s in sin_taxes:
		lst_y =  get_list_to_draw(df,s)
		lst_y_09 =  get_list_to_draw_09(df,s)
		_,_, gini_val = G(df[s])
		ax1.plot(x1, lst_y)
		ax2.plot(x2, lst_y_09)

	ax1.set_ylabel("percentage of tax")
	ax1.set_xlabel("tax percentile")
	ax2.set_xlabel("tax percentile")
	ax1.set_title("Panel C: Sin Taxes")
	ax2.set_title("Panel D: Top Decile Sin Taxes")


draw_cdf(df,ax1,ax2)

#Create the legend
# Create the legend
leg = creat_legend(df)
fig.legend(
		   labels=leg,   # The labels for each line
		   loc="center",   # Position of legend
		   borderaxespad=0.1,    # Small spacing around legend box
		   #title="Consumption Type",  # Title for the legend
		   bbox_to_anchor=(0.55,0.1),
           ncol=3
		   )
plt.subplots_adjust(bottom=0.3)
# plt.savefig(fig_dir/'gini_tax.pdf',bbox_inches="tight")
plt.savefig(fig_dir/'Figure1B.pdf',bbox_inches="tight")