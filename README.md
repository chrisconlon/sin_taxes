### Replication for "Who Pays Sin Taxes? Understanding the Overlapping Burdens of Corrective Taxes" 
Review of Economics and Statistics
Conlon, Rao, Wang (2022)


## Github Install Instructions
To download the repo simply type:

```
git clone https://github.com/chrisconlon/sin_taxes
```

# Installation/Setup
1. This project runs almost entirely in Python (3.7 or above recommended).
2. The dependencies can be installed via:
```
    pip install r ./code/requirements.txt
```
3. The only "custom" dependency is found on the author's GitHub below:
    https://github.com/chrisconlon/kiltsnielsen

# Kilts/NielsenIQ Data
- We cannot include the Kilts/NielsenIQ data directly in this package but information on acquiring the data for academic researchers is available at https://www.chicagobooth.edu/research/kilts/datasets/nielseniq-nielsen
- You only need to download the Consumer Panelist Data and this project does not require any scanner data.
- You will need to modify the path in ./code/0_read_nielsen_data.py to point the folder with your (unzipped) Kilts/NielsenIQ files
- You must have the pyarrow dependency installed to read and save the Kilts/NielsenIQ data.

# 

