import pandas as pd
import numpy as np
import datetime as dt
import pathlib
import matplotlib
import matplotlib.pyplot as plt

### Liquor Project base directory
proj_dir = pathlib.Path.cwd().parent

# Our input files go here
raw_dir= proj_dir / 'raw_data'
data_dir = proj_dir / 'proc_data'
tab_dir = proj_dir / 'tables'
fig_dir = proj_dir / 'figures'
tax_dir = proj_dir / 'tax_data'

## Constants
# .06 fluid oz in L
# https://www.rethinkingdrinking.niaaa.nih.gov/how-much-is-too-much/what-counts-as-a-drink/whats-a-standard-drink.aspx
drinks_per_ethanol_L = .0177441177

oz_l = 0.0295735
qt_l = 0.946353
ml_l = 0.001
liters_per_gallon = 3.78541
l_oz = 33.814

wine_abv = 0.129
beer_abv = 0.045
liquor_abv = 0.411
race_map={1:'White',2:'Black',3:'Asian',4:'Other'}

# Tax Rates (2018)
FED_Beer = 0.58/liters_per_gallon
FED_Wine = 1.07/liters_per_gallon
FED_Spirits = 0.8*(13.5/liters_per_gallon) #per proof gallon
FED_cigarette = 1.0066
SSB_tax_rate = 0.01

# Default ABV%
ethanol_in_beer = 0.045
ethanol_in_wine = 0.129
ethanol_in_spirits = 0.4


# Can give these text names later
# mapping for nielsen fields to labels
inc_map={
	3:'<24,999',4:'<24,999',6:'<24,999',8:'<24,999',10:'<24,999',11:'<24,999',13:'<24,999',
	15:'25,000 - 44,999',16:'25,000 - 44,999',17:'25,000 - 44,999',18:'25,000 - 44,999',
	19:'45,000-69,999',21:'45,000-69,999',23:'45,000-69,999',26:'70,000-99,999',
	27:'> 100,000',28:'> 100,000',29:'> 100,000', 30:'> 100,000'
	}

age_map={
	1:'under_35', 2:'under_35', 3:'under_35',
	4:'35_to_44', 5:'35_to_44',
	6:'45_to_54', 7:'45_to_54',
	8:'55_to_64', 9:'over_65',
	}

edu_map={
	1:'High School or Less',
	2:'High School or Less',
	3:'High School or Less',
	4:'Some College',
	5:'Graduated College',
	6:'Post College Grad'
}

cluster_order = ['Everything','Smokers','Heavy Drinkers','Moderate Spirits','Mostly Wine','Moderate Beer','SSB only','Nothing']



def write_tex_table(tex, f_out):
    with open(f_out, "w") as text_file:
        print(tex, file=text_file)
    return

def np_wavg(df, col_list, weights):
    """Apply weighted average to each col in col_list using column ``weights'' Should correctly handle NaNs and missing values."""
    # convert to numpy
    x = df[col_list].values
    #w = np.nan_to_num(weights)
    w = np.nan_to_num(weights.values)
    W = np.tile(w, (x.shape[1], 1)).transpose()

    # mask nan values in x to get zero weight
    mask = np.isnan(x)
    W[mask] = 0
    tot_w = W.sum(axis=0)

    # take weighted average
    z = np.nansum(x * W, axis=0) / tot_w
    # if all weights zero assign NaN
    z[tot_w == 0] = np.nan

    out = pd.Series(z, col_list)
    return out

def np_wsum(df, col_list, weights):
    """Apply weighted sum to each col in col_list using column ``weights'' Should correctly handle NaNs and missing values."""
    # convert to numpy
    x = df[col_list].values
    w = np.nan_to_num(df[weights].values)
    W = np.tile(w, (x.shape[1], 1)).transpose()

    # mask nan values in x to get zero weight
    mask = np.isnan(x)
    W[mask] = 0
    tot_w = W.sum(axis=0)

    # take weighted average
    z = np.nansum(x * W, axis=0)

    # if all weights zero assign NaN
    z[tot_w == 0] = np.nan

    out = pd.Series(z, col_list)
    out["total_w"] = w.sum()
    return out


def weighted_quantile(values, quantiles, sample_weight=None, 
                      values_sorted=False, old_style=False):
    """ Very close to numpy.percentile, but supports weights.
    NOTE: quantiles should be in [0, 1]!
    :param values: numpy.array with data
    :param quantiles: array-like with many quantiles needed
    :param sample_weight: array-like of the same length as `array`
    :param values_sorted: bool, if True, then will avoid sorting of
        initial array
    :param old_style: if True, will correct output to be consistent
        with numpy.percentile.
    :return: numpy.array with computed quantiles.
    """
    values = np.array(values)
    quantiles = np.array(quantiles)
    if sample_weight is None:
        sample_weight = np.ones(len(values))
    sample_weight = np.array(sample_weight)
    assert np.all(quantiles >= 0) and np.all(quantiles <= 1), \
        'quantiles should be in [0, 1]'

    if not values_sorted:
        sorter = np.argsort(values)
        values = values[sorter]
        sample_weight = sample_weight[sorter]

    weighted_quantiles = np.cumsum(sample_weight) - 0.5 * sample_weight
    if old_style:
        # To be convenient with numpy.percentile
        weighted_quantiles -= weighted_quantiles[0]
        weighted_quantiles /= weighted_quantiles[-1]
    else:
        weighted_quantiles /= np.sum(sample_weight)
    return np.interp(quantiles, weighted_quantiles, values)
   