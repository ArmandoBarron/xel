from scipy.stats import ttest_1samp
import pandas as pd  
import numpy as np
import pickle
import sys,json

params = sys.argv[1]
params = json.loads(params)

score_file=  params['score_file']
variability= float(params['variability']) #allowed bariability (0 to 1) 
alpha= float(params['alpha'])  # alpha value is 0.05 or 5% (0 to 1)

########################################
### VALIDATING K-MEANS #################
########################################

array_scores = pickle.load( open( score_file, "rb" ) )
dataframe= pd.Series(array_scores)
print('datafame: ', dataframe.describe())

array_values_mean = np.mean(array_scores)
epsilon = array_values_mean - array_values_mean * variability
print('epsilon: ', epsilon)
tset, pval = ttest_1samp(array_scores, epsilon)
print('p-value: ', pval)

if pval < alpha:    # alpha value is 0.05 or 5%
   result = "[%s] - Null hypothesis rejected - There are not statistical difference. p-value: %s" % (score_file,pval)
else:
   result = "[%s] - Null hypothesis accepted - There are statistical difference. p-value: %s" % (score_file,pval)

print(result)
f = open(params['outputfile'],"w")
f.write(result)
f.close()