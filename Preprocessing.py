# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 22:50:02 2020

@author: koohaoming
"""
"""Fitting of data"""
 
from scipy import stats 
import numpy as np 
import matplotlib.pylab as plt
 
Raw = pd.read_csv('RPT.csv') #load the file with machine processing time
#Raw2 = Raw.dropna()
columns = list(Raw.columns.values)
 
#tempdf = (Raw2 - Raw2.mean())/Raw2.std(ddof=0)
#processed_df = Raw2[(np.abs(tempdf)<3)].dropna() #to do the z-scoring to remove outliers if needed
 
for y in columns:  #iterate the RPTs
    x= pd.DataFrame(Raw[columns[y]]).to_numpy()
    x=x[~np.isnan(x)]
   
    plt.hist(x, bins=20,density=True)
   
    xt = plt.xticks()[0] 
    xmin, xmax = min(xt), max(xt) 
    lnspc = np.linspace(xmin, xmax, len(x))
   
    m, s = stats.norm.fit(x) # get mean and standard deviation 
    pdf_g = stats.norm.pdf(lnspc, m, s) # now get theoretical values in our interval 
    plt.plot(lnspc, pdf_g, label="Norm") # plot it
   
    ag,bg,cg = stats.gamma.fit(x) 
    pdf_gamma = stats.gamma.pdf(lnspc, ag, bg, cg) 
    plt.plot(lnspc, pdf_gamma, label="Gamma")
   
    ab,bb,cb,db = stats.beta.fit(x) 
    pdf_beta = stats.beta.pdf(lnspc, ab, bb,cb, db) 
    plt.plot(lnspc, pdf_beta, label="Beta")
    plt.legend()
    plt.title(columns[y])
    plt.xlabel('RPT in Minutes')
    plt.ylabel('Density')
    plt.show() 
    
    print('Normal Distribution')
    print('mean =',m)
    print('std =',s)
   
    print('Gamma Distribution')
    print('shape =',ag)
    print('scale =',bg)
   
    print('Beta Distribution')
    print('alpha =',ab)
    print('beta =',bb)
 
 #%%
"""Plotting of Hot Lots"""
 #An extension to the simpy_master file. Paste to the bottom to use for ploting of distributions 

database_gr2 = database_gr.copy()
database_gr2['TOTAL_QTIME_BREACHED'] = database_gr2[['S1_2_QTIME_BREACHED', 'S2_3_QTIME_BREACHED',
       'S3_4_QTIME_BREACHED', 'S4_5_QTIME_BREACHED']].sum(axis = 1)
database_gr2=database_gr2[database_gr2['TOTAL_QTIME_BREACHED']==0]
database_gr2= database_gr2.sort_values('TOTAL_LOTS_MOVED',ascending=False).reset_index(drop=True)
 
def filtering(df,GR1,GR2,GR3,GR4,GR5):
    if 'GR1' in df.columns:
        filtered_df = df[(df['GR1'] == GR1) & (df['GR2'] == GR2) &
                              (df['GR3'] == GR3) & (df['GR4'] == GR4) &
                              (df['GR5'] == GR5)]
    else:
        filtered_df = df[(df['Gating Ratio 1'] == GR1) & (df['Gating Ratio 2'] == GR2) &
                              (df['Gating Ratio 3'] == GR3) & (df['Gating Ratio 4'] == GR4) &
                              (df['Gating Ratio 5'] == GR5)]
    return filtered_df
 
GR1 , GR2, GR3, GR4, GR5 = database_gr2.iloc[5092,:5]
 
hotlots_bestcr = filtering(database_hot_qt,GR1,GR2,GR3,GR4,GR5)
normallots_bestcr = filtering(database_qt,GR1,GR2,GR3,GR4,GR5).loc[~database_qt.lotid.isin(hotlots_bestcr['lotid'].tolist())]
 
hotlots_best_cr_mean = hotlots_bestcr.groupby('step').mean()['Q-time actual']
hotlots_best_cr_std = hotlots_bestcr.groupby('step').std()['Q-time actual']
 
normallots_bestcr_mean = normallots_bestcr.groupby('step').mean()['Q-time actual']
normallots_bestcr_std = normallots_bestcr.groupby('step').std()['Q-time actual']
#%% Q- Time Lots Boxplot
fig, ax = plt.subplots()
ind = np.arange(4)
width = 0.35
ax.bar(ind,hotlots_best_cr_mean,width,yerr=hotlots_best_cr_std, label = 'Hot Lots')
ax.bar(ind+width,normallots_bestcr_mean,width,yerr=normallots_bestcr_std, label = 'Normal Lots')
ax.set_title('GR1 = {:.1f}, GR2 = {:.1f},GR3 = {:.1f}, GR4 = {:.1f},GR5 = {:.1f}'.format(GR1,GR2,GR3,GR4,GR5))
ax.set_xticklabels(('1-2', '2-3', '3-4', '4-5'))
ax.set_xticks(ind + width / 2)
ax.set_xlabel('Between Steps')
ax.set_ylabel('Q-time in Minutes')
ax.set_ylim(bottom=0)
 
ax.legend()
ax.autoscale_view()
 
plt.show()
 
 
#%% Q-time Distribution
plt.figure(figsize=(8,6))
plt.hist(database_hot_qt[database_hot_qt['step']=='4-5']['Q-time actual'],bins=50,range=[1,800], alpha=0.5,density = True, label="Hot Lots")
plt.hist(database_qt[database_qt['step']=='4-5']['Q-time actual'], bins=50, range=[1,800],alpha=0.5,density = True, label="Normal Lots")
plt.xlabel("Q-time", size=14)
plt.ylabel("Desnity Distribution", size=14)
plt.title("Simulation Data Distribution Step 4-5")
plt.legend(loc='upper right');