#from pydoc import help
import scipy
from scipy.stats.stats import pearsonr

from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import FloatVector

stats = importr('stats')

'''p_adjust = stats.p_adjust(FloatVector([0.03,0.01,0.2]), method = 'BH')

print(p_adjust)
quit()'''
#help(pearsonr)

import csv
import sys
import pandas as pd
import numpy as np


file = '/Volumes/GoogleDrive/My Drive/DATA/DrugBank/drug.csv'

drug = {}
with open(file) as csv_file:
	csv_reader = csv.DictReader(csv_file, delimiter=',')

	for row in csv_reader:

		drug[row['primary_key']] = row

file = '/Volumes/GoogleDrive/My Drive/DATA/DrugBank/drug_calculated_properties.csv'

with open(file) as csv_file:
	csv_reader = csv.DictReader(csv_file, delimiter=',')

	for row in csv_reader:

		if row['parent_key'] in drug:

			if row['kind'] == 'pKa (strongest basic)':

				drug[row['parent_key']]['pka'] = row['value']

			if row['kind'] == 'logP':

				if 'logP' not in drug[row['parent_key']]:

					drug[row['parent_key']]['logP'] = [float(row['value'])]

				else: 

					drug[row['parent_key']]['logP'].append(float(row['value']))

drug0 = {}
for k, v in drug.items():

	if 'logP' in v and 'pka' in v:

		drug0[v['name'].lower()] = {
			'logP' : np.mean(np.array(v['logP'])),
			'pka' : v['pka']
		}


file = '/Users/timpeterson/OneDrive-v3/Data/CADs/v2/DSigDB_path_tomics_gt2_path_gt1_foldchange (302 genes).txt'


with open(file) as csv_file:
	csv_reader = csv.DictReader(csv_file, delimiter='\t')

	for row in csv_reader:

		name = row['Term'].split()

		if name[0].lower() in drug0:

			if 'pval' not in drug0[name[0].lower()]:

				drug0[name[0].lower()]['pval'] = [float(row['Adjusted P-value'])]
			else:
				drug0[name[0].lower()]['pval'].append(float(row['Adjusted P-value']))

			if 'OR' not in drug0[name[0].lower()]:
				drug0[name[0].lower()]['OR'] = [float(row['Odds Ratio'])]
			else:
				drug0[name[0].lower()]['OR'].append(float(row['Odds Ratio']))


output = []
for key, value in drug0.items():

	if 'pval' in value and 'OR' in value:

		if len(value['pval']) == 1:
			continue

		p_adjust = stats.p_adjust(FloatVector(value["pval"]), method = 'BH')
		pval = scipy.stats.stats.combine_pvalues(p_adjust)

		result = (pval[1], np.mean(value['OR']), value['pka'], value['logP'])

		output.append(list((key,) + result)) 

#sort the output desc
output1 = sorted(output, key=lambda x: x[2], reverse=True)

import random

num_rand_to_generate = 2806 - len(output1)

def sample_floats(low, high, k=1):
    """ Return a k-length list of unique random floats
        in the range of low <= x <= high
    """
    result = []
    seen = set()
    for i in range(k):
        x = random.uniform(low, high)
        while x in seen:
            x = random.uniform(low, high)
        seen.add(x)
        result.append(x)
    return result

pvals = sample_floats(0,1, num_rand_to_generate)

ORs = sample_floats(0,2, num_rand_to_generate)

for idx, val in enumerate(pvals):
	output1.append(['', val, ORs[idx], '', ''])

with open('/Users/timpeterson/OneDrive-v3/Data/CADs/v2/DsigDB_all_pathogens_gt1_cell_line_w_rands.csv', 'w') as csvfile:
	spamwriter = csv.writer(csvfile, delimiter=',')

	spamwriter.writerow(['drug', 'pval', 'OR', 'pka', 'logP'])
	for row in output1:
		#if any(field.strip() for field in row):
		spamwriter.writerow(row)

	csvfile.close()
