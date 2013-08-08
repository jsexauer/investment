"""
Investigate the value of holding on to a security as long as you can
"""
import pandas
from investmentLib import *
import matplotlib.pylab as plt
import numpy as np
import multiprocessing

print "****Top of program"
_startTime = pandas.datetime.now()

symbol = '^GSPC'
sDate = (1950,1,1)
eDate = (2013,12,31)

maxDaysHeld = 10000
numSim = 5000
daySpacing = 100
cumulative = True
multiThread = False

plt.close('all')

df = grabSymbol(symbol, sDate, eDate)
o = pandas.DataFrame(columns=['DaysHeld','Gains'])
inflate = calcInflation()
getInfl = inflate.calcInflation

if 'X' in vars().keys():
    del X

means = []
medians = []


import threading
class playMarket(threading.Thread):
    def __init__(self, daysHeld, nsim, strategy='random', df=df):
        """Create a thread with a certain market entry strategy
        Validy strategies are:
            - random = Enter the market at a random time
        """
        threading.Thread.__init__(self)
        
        self.daysHeld = daysHeld
        self.gain = np.nan          # Value "returned" by run function
        self.df = df                # Dataframe of stock
        self.nsim = nsim
        
        # Set run function based on entry strategy
        if strategy == 'random':
            self.func = self.runRandomEntry
        else:
            raise "Invalid bidding strategy '%s'" % strategy
    
    def run(self):
        #print "Begin Thread"
        allGains = []
        for n in range(self.nsim):
            self.func()
            allGains.append(self.gain)
        self.gain = allGains
        #print "End Thread"
        
    def runRandomEntry(self):
        """Run a simmulation of entering the market at random"""
        flag = False
        while not flag:
            r = floor(np.random.rand() * len(self.df.index))
            start = self.df.index[r]
            if r+self.daysHeld < len(self.df.index)-1:
                end = self.df.index[r+self.daysHeld]
                flag = True
        
        #self.daysHeld = (end-start).days
        self.gain = (self.df.adj_close[end] - getInfl(self.df.adj_close[start], start.year, end.year)) / \
                        getInfl(self.df.adj_close[start], start.year, end.year)
        


for daysHeld in range(1,maxDaysHeld,daySpacing):
    print "Considering hold for %d days" % daysHeld
    gains = []
    
    if multiThread == True:
        threads = []
        nSubSims = 1000     # Num of simulations each thread runs
        # Create Threads
        for n in range(numSim/nSubSims):
            threads.append(playMarket(daysHeld, nSubSims))
            threads[-1].start()
        # Wait for thread to finish
        for n in range(numSim/nSubSims):
            threads[n].join()   
        # Append results
        for n in range(numSim/nSubSims):
            gains += threads[n].gain
            for g in threads[n].gain:
                o = o.append({'DaysHeld': daysHeld, 'Gains': g}, ignore_index=True)
    else:
        t = playMarket(daysHeld,1)
        for n in range(numSim):
            t.runRandomEntry()
            gains.append(t.gain)
            o = o.append({'DaysHeld': daysHeld, 'Gains': t.gain}, ignore_index=True)            
        
    
    freq,bins = np.histogram(gains, bins=25)
    freq = freq.astype('f')/sum(freq.astype('f'))
    means.append(np.average(gains))
    medians.append(np.median(gains))
    
    if cumulative:
        bins_cp = np.array([(bins[a] + bins[a+1])/2.0 for a in range(len(bins)-1)])
        pos_freq = freq[bins_cp>=medians[-1]]
        neg_freq = freq[bins_cp<medians[-1]]
        pos_freq = [sum(pos_freq[q:]) for q in range(len(pos_freq))]
        neg_freq = [sum(neg_freq[q::-1]) for q in range(len(neg_freq))]
        freq = hstack([neg_freq, pos_freq])
        
    
    if 'X' in vars().keys():
        X = np.vstack([X, np.ones(len(bins))*daysHeld])
        Y = np.vstack([Y, bins])
        C = np.vstack([C, freq])
    else:
        X = np.ones(len(bins))*daysHeld
        Y = bins
        C = freq
    
    
# Convert time (X) to years
X = X.astype('f')/365.25

plt.pcolor(X, Y, C, cmap=plt.cm.YlOrRd)
#means = pandas.rolling_mean(pandas.Series(means), 10)
plt.plot(X[:,1], means, color='k', label='Mean')
plt.plot(X[:,1], medians, color='b', label='Median')
plt.colorbar()
plt.legend(loc='upper left')
plt.xlabel('Years')
plt.ylabel('Return')
plt.grid(axis='y')
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: '%0.2f%%' %(x*100)))
plt.show()

plt.figure()
o.plot(style='.', x='DaysHeld', y='Gains')   

print "Done.  Execution took ",  (pandas.datetime.now()- _startTime ).seconds, " seconds"
