import matplotlib.pyplot as plt
import seaborn as sns; sns.set()  # for plot styling
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.cm as cm
import pathlib as path
from common_import import raw_dir, data_dir,tab_dir,fig_dir


df = pd.read_parquet(data_dir/'panel_data_all_years.parquet')
###GINI PLOT###
#GINI consumption plot- CDF of Sin Good Consumption

from cycler import cycler
import matplotlib

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
plt.rc('axes', prop_cycle=cycler(color=['008fd5', 'fc4f30', 'e5ae38', '6d904f', '8b8b8b', '810f7c']))
#plt.rc('axes',prop_cycle=cycler(color=['c', 'm', 'y', 'k'], lw=[1, 2, 3, 4]))
#plt.rc('axes',prop_cycle=cycler(color=['#008fd5', '#fc4f30', '#e5ae38', '#6d904f', '#8b8b8b','purple','navy']))
plt.rc('lines', linewidth=3)

#plt.rc('text', usetex=True)
#sns.color_palette("Paired")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20,10))

def creat_legend(df):
	leg = []
	sin_goods = ['carbonated','cigars','beer','wine','liquor','ethanol']
	normal_goods = ['toilet_tissue','yogurt']
	for s in (sin_goods+normal_goods):
		_,_, gini_val = G(df[s])

		if s == 'carbonated':
			s = 'SSB'
		elif s == 'toilet_tissue':
			s = 'toilet tissue'
		elif s == 'ethol':
			s = 'ethanol'
		elif s == 'cigars':
			s = 'cigarette'
			# gini_val = '0.900'
		elif s == 'liquor':
			s = 'spirits'
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
	sin_goods = ['carbonated','cigars','beer','wine','liquor','ethanol']
	normal_goods = ['toilet_tissue','yogurt']
	
	#     fig = plt.figure(figsize=(16,6))
	#     ax = fig.add_subplot(1, 2, 1)
	x1 = np.linspace(0,1,101)
	x2 = np.linspace(0.9,1,11)
	for s in sin_goods:
		lst_y =  get_list_to_draw(df,s)
		lst_y_09 =  get_list_to_draw_09(df,s)
		_,_, gini_val = G(df[s])
		ax1.plot(x1, lst_y)
		ax2.plot(x2, lst_y_09)


	# for n in normal_goods:
	lst_y =  get_list_to_draw(df,'toilet_tissue')
	lst_y_09 =  get_list_to_draw_09(df,'toilet_tissue')
	_,_, gini_val = G(df['toilet_tissue'])
	ax1.plot(x1, lst_y,'-.')
	ax2.plot(x2, lst_y_09,'-.')

	lst_y =  get_list_to_draw(df,'yogurt')
	lst_y_09 =  get_list_to_draw_09(df,'yogurt')
	_,_, gini_val = G(df['yogurt'])
	ax1.plot(x1, lst_y,'-.',color='coral')
	ax2.plot(x2, lst_y_09,'-.',color='coral')



	ax1.set_ylabel("percentage of total purchases")
	ax1.set_xlabel("purchase percentile")
	ax2.set_xlabel("purchase percentile")
	ax1.set_title("Panel A: Sin Good Purchases")
	ax2.set_title("Panel B: Top Decile Sin Good Purchases")


draw_cdf(df,ax1,ax2)



# Create the legend
leg = creat_legend(df)
fig.legend(
		   labels=leg,   # The labels for each line
		   loc="center",   # Position of legend
		   borderaxespad=0.1,    # Small spacing around legend box
		   #title="Consumption Type",  # Title for the legend
		   bbox_to_anchor=(0.5,0.1),
           ncol=3
		   )
plt.subplots_adjust(bottom=0.3)
# plt.tight_layout()
# plt.savefig(fig_dir/'gini_consumption.pdf',bbox_inches="tight")

plt.savefig(fig_dir/'Figure1A.pdf',bbox_inches="tight")
