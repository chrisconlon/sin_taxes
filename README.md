# Replication for "Who Pays Sin Taxes? Understanding the Overlapping Burdens of Corrective Taxes"
[Review of Economics and Statistics](https://chrisconlon.github.io/site/sin_tax.pdf)  Conlon, Rao, Wang (2022)



## Github Install Instructions
To download the repo simply type:

```
git clone https://github.com/chrisconlon/sin_taxes
```

## Installation/Setup
1. This project runs almost entirely in Python (3.7 or above recommended).
2. The dependencies can be installed via:
```
    pip install -r ./code/requirements.txt
```
3. The only kiltsreader is the authors' own package:
```
    https://github.com/chrisconlon/kiltsnielsen
```

4. We anticipate most users will be running this replication package from within an Anaconda environment. To avoid making changes to your base environment you will want to create a separate environment for this replication package. To do that

```
    conda create --name sin_tax --file requirements.txt
    conda activate sin_tax
```

5. How to run the code

Change to the directory labeled ```code``` and run "./run_all.sh" on the terminal. The code should take approximately 20 minutes to run. Tables and figures will be produced as described below.

    cd code
    ./runall.sh

6. After the files numbered 0\_ through 3\_, the remaining files that generate tables and figures can be run in any order.

7. Memory Requirements: 0_read_nielsen_data.py is designed for speed not for memory usage. It can use over 32GB of RAM. You may want to separately process year by year to conserve memory. Comments are provided in the code. The remaining files use neglible amounts of memory.

### Kilts/NielsenIQ Data
- We cannot include the Kilts/NielsenIQ data directly in this package but information on acquiring the data for academic researchers is available at [https://www.chicagobooth.edu/research/kilts/datasets/nielseniq-nielsen](https://www.chicagobooth.edu/research/kilts/datasets/nielseniq-nielsen)
- You only need to download the Consumer Panelist Data and this project does not require any scanner data.
- You will need to modify the path in ```./code/0_read_nielsen_data.py``` to point the folder with your (unzipped) Kilts/NielsenIQ files
- You must have the ```pyarrow``` dependency installed to read and save the Kilts/NielsenIQ data.



### Author Constructed files

data/raw_data:

The below files are publicly available Excel files constructed by the authors. 

category_list.xlsx:  mapping from NielsenIQ product_group_code to our category assignemnt
nielsen_income_bins.xlsx: mapping from NielsenIQ income bin to income levels
state_alcohol_rates.xlsx: Tax Policy Center panel of state excise taxes.
state_cigarette_rates_5.xlsx Tax Policy Center panel of state excise taxes.


### File of origin for tables and figures

| Table/Figure Number   | Generating File           |
| --- |---|
| Table 1       | ```table1_revised.py```            |
| Table 2       | ```table2_odds_ratio.py```        |
| Table 3       | ```table3_by_year.py```         |
| Figure 1      | ```Figure1_cdfs.py```     |
| Figure 2      | ```Figure2_Correlation.py```      |
| Table A1     | ```tableA1_alcohol_usage.py```      |
| Table A2     | ```tableA2_ethanol_per_capita.py```    |
| Table A3     | ```tableA3_tobacco_useage.py```  |
| Figure A1    | ```FigureD1A1_DrinksperWeek.R```  |
| Table B2     | ```tableB2_state_taxes.py```     |
| Table D1     | ```tableD1_tax_burden_by_inc.py```     |
| Table D2     | ```tableD2_sin_tax_by_Race.py```      |
| Table D3     | ```tableD3_Regression.R```      |
| Table D4     | ```tableD4_tax_inc_ratio.py```     |
| Table D5       | ```table2_odds_ratio.py```        |
| Table D6     | ```tableD6multiNM.py```     |
| Table D7      | ```table2_odds_ratio.py```        |
| Figure D1    | ```FigureD1A1_DrinksperWeek.R```  |
| Table E1     | ```tableE1E2_Other_Cluster_Number.py```     |
| Table E2     | ```tableE1E2_Other_Cluster_Number.py```     |





### Description of .parquet file format

We use the parquet format for:

Large data inputs (above)
Most intermediary datasets
Parquet files are compressed columnar storage binaries that are readable by several software packages (R, Python, Stata, Julia, C++, etc.) and platforms. The goal of the parquet project is to maintain good performance for large datasets as well as interoperability.

The storage method is stable and maintained by the Apache Foundation. [https://parquet.apache.org/documentation/latest/](https://parquet.apache.org/documentation/latest/)

We use the python package ```pyarrow``` to read parquets and the package ```brotli``` for compression (listed in the requirements.txt).
