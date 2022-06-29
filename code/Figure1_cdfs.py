import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from common_import import raw_dir, data_dir,tab_dir,fig_dir
from plot_helper import initialize_plot, draw_cdf

# Plot Configuration (use black_white or not?)
black_white = True
initialize_plot()

# Read in Data
df = pd.read_parquet(data_dir/'panel_data_all_years.parquet')
df['alcohol_tax'] = df['beer_tax'] + df['spirits_tax'] +df['wine_tax']


# Top Figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20,10))
sin_labels=draw_cdf(df, ax1, ax2, taxes=False, use_bw=black_white)
legend_info = {'loc':"center",'borderaxespad':0.1,'bbox_to_anchor':(0.5,0.1),'ncol':3}
fig.legend(labels=sin_labels,**legend_info)

# Create the legend and save
plt.subplots_adjust(bottom=0.3)
plt.savefig(fig_dir/'Figure1A.pdf',bbox_inches="tight")

# Bottom Figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20,10))
tax_labels=draw_cdf(df, ax1, ax2, taxes=True, use_bw=black_white)
fig.legend(labels=tax_labels, **legend_info)

# Create the legend and save
plt.subplots_adjust(bottom=0.3)
plt.savefig(fig_dir/'Figure1B.pdf',bbox_inches="tight")