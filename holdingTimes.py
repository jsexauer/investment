import multiprocessing
from investmentLib import calcInflation
import numpy as np
import pandas
inflate = calcInflation()
getInfl = inflate.calcInflation
#getInfl = lambda x, trash1, trash2: x   # Neglect inflation

class Worker(multiprocessing.Process):
    
    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill means we should exit
                print '%s: Exiting' % proc_name
                break
            #print '%s: %s' % (proc_name, next_task)
            answer = next_task()
            self.result_queue.put(answer)
        return


class Task(object):
    def __init__(self, daysHeld, nsim, df, cumulative):
        self.daysHeld = daysHeld
        self.gain = 0               # Value "returned" by run function
        self.df = df                # Dataframe of stock
        self.nsim = nsim
        self.cumulative = cumulative
        
        self.momementum = moving_average(df['adj_close'].diff(), 5)[0]
        self.momementum.index = self.df.index[4:]
        self.momementum = self.momementum.append(pandas.Series({a: 0 for a in df.index[:4]}))
        self.momementum = self.momementum.fillna(0)
        self.momementum = self.momementum.sort_index()
        self.wastedTime = 0
               
    def __str__(self):
        return 'Gains for Holding %d days' % self.daysHeld   
        
    def __call__(self):
        """Do analysis for a give number of days held"""
        gains = []
        numSim = self.nsim
        
        for n in range(numSim):
            gains.append(self.runDelayedEntryStrat())        
        # Average wasted time
        self.wastedTime = float(self.wastedTime) / numSim
        
        means = np.average(gains)
        medians = np.median(gains)
        low_25 = np.percentile(gains, 25)
        high_25 = np.percentile(gains, 75)
        '''
        freq,bins = np.histogram(gains, bins=25)
        freq = freq.astype('f')/sum(freq.astype('f'))
        
        
        if self.cumulative:
            
            bins_cp = np.array([(bins[a] + bins[a+1])/2.0 for a in range(len(bins)-1)])
            pos_freq = freq[bins_cp>=medians]
            neg_freq = freq[bins_cp<medians]
            pos_freq = np.array([sum(pos_freq[q:]) for q in range(len(pos_freq))])
            neg_freq = np.array([sum(neg_freq[q::-1]) for q in range(len(neg_freq))])
            freq = np.hstack([neg_freq, pos_freq])
        '''
        freq = []
        step = 1
        rng = range(0,51,step)[1:]
        freq += rng
        bins = np.percentile(gains, rng)
        
        rng = range(50,101,step)[1:]
        freq += [100 - a for a in rng]
        bins = np.hstack([bins, np.percentile(gains, rng)])
        freq = np.array(freq)
        
        """
        for a in range(0,51,step)[1:]:
            freq.append(a)
            bins.append(np.percentile(gains, a))
        for a in range(50,101,step)[1:]:
            freq.append(100 - a)
            bins.append(np.percentile(gains, a)) 
        bins = np.array(bins)
        freq = np.array(freq)
        """
        
        X = np.ones(len(bins))*self.daysHeld
        Y = bins
        C = freq
        
        return (means, medians, X, Y, C, self.daysHeld, low_25, high_25, self.wastedTime)
        
    def randomDays(self):
        """Figure out some start and end time"""
        flag = False
        while not flag:
            r = np.floor(np.random.rand() * len(self.df.index))
            start = self.df.index[r]
            if r+self.daysHeld < len(self.df.index)-1:
                end = self.df.index[r+self.daysHeld]
                flag = True
        return (start,end)
        
    def runRandomEntryStrat(self):
        """Run a simmulation of entering the market at random"""
        start, end = self.randomDays()
        
        gain = (self.df.adj_close[end] - getInfl(self.df.adj_close[start], start.year, end.year)) / \
                        getInfl(self.df.adj_close[start], start.year, end.year)
        if gain > 6:
            print "Windfall: ", start, end, gain
        return gain
    
    def runDelayedEntryStrat(self):
        """Run a simmulation where I only enter the market when the last
           30 days have 50% positive momentum upto half the time I plan to invest"""
        # Choose the first day I'd like to enter randomly
        start, end = self.randomDays()
        
        # Now wait for positive momentum
        flag = False
        trueStart = start
        while not flag:
            aWin = self.momementum[(start + pandas.DateOffset(days=-30)):start]
            if (aWin > 0).sum() > 30*.75:
                # I'm going to invest
                #print "Made it out!"
                flag = True
            else:
                # I'm going to wait another five days
                start = start + pandas.DateOffset(days=5)
                if (end-start).days < self.daysHeld/2:
                    # Screw it, I've waited too long I'm going to invest anyways
                    flag = True
                    #print "Screw it, I've only got %s of %s days left!" % ((end-start).days, self.daysHeld)
        
        #print "I wasted %d days" % (start-trueStart).days
        self.wastedTime = self.wastedTime + (start-trueStart).days        
        gain = (self.df.adj_close[end] - getInfl(self.df.adj_close[start], start.year, end.year)) / \
                        getInfl(self.df.adj_close[start], start.year, end.year)
        return gain               
        
        
def moving_average(a, n=3) :
    ret = a.cumsum()
    return (ret[n - 1:].reset_index() - ret[:1 - n].reset_index()) / n
    
if __name__ == '__main__':
    # My Stuff
    import matplotlib.pylab as plt
    from investmentLib import grabSymbol
    
    _startTime = pandas.datetime.now()
    
    symbol = '^GSPC' # 10-year T bill: '^TNX', S&P500: '^GSPC'
    sDate = (1950,1,1)
    eDate = (2013,12,31)
    
    maxDaysHeld = 10000
    numSim =  5000 # 5000 is best for convergence
    daySpacing = 10
    startDays = 10
    cumulative = True
    
    plt.close('all')
    
    df = grabSymbol(symbol, sDate, eDate)
    
    if 'X' in vars().keys():
        del X



    ###########
    # Multiprocessing Stuff
    #raise KeyError

    # Establish communication queues
    tasks = multiprocessing.Queue()
    results = multiprocessing.Queue()
    
    # Start Workers
    num_workers = multiprocessing.cpu_count() * 1
    print 'Creating %d workers' % num_workers
    consumers = [ Worker(tasks, results)
                  for i in xrange(num_workers) ]
    for w in consumers:
        w.start()
    
    # Enqueue jobs
    num_jobs = 0
    
    for daysHeld in range(startDays,maxDaysHeld,daySpacing):
        tasks.put(Task(daysHeld, numSim, df, cumulative))
        num_jobs += 1
    # Add a poison pill for each worker
    for i in xrange(num_workers):
        tasks.put(None)
        
        
    
    # Start printing results
    jobsTime = pandas.Series(pandas.datetime.now())
    means = np.zeros(num_jobs)
    medians = np.zeros(num_jobs)
    low_25 = np.zeros(num_jobs)
    high_25 = np.zeros(num_jobs)
    wastedTime = np.zeros(num_jobs)
    
    while num_jobs:
        (mn, mds, Xn, Yn, Cn, dH, l_25, h_25, w) = results.get()
        ix = (dH-startDays)/daySpacing
        means[ix] = mn
        medians[ix] = mds
        low_25[ix] = l_25
        high_25[ix] = h_25
        wastedTime[ix] = w
        
        if 'X' not in vars().keys():
            # Initalize results matrixes
            X = np.zeros([num_jobs, int(Xn.shape[0])])
            Y = np.zeros([num_jobs, int(Yn.shape[0])])
            C = np.zeros([num_jobs, int(Cn.shape[0])])        
        X[ix,:] = Xn
        Y[ix,:] = Yn
        C[ix,:] = Cn
            
        num_jobs -= 1
        jobsTime = jobsTime.append(pandas.Series(pandas.datetime.now()))
        print "Jobs left: %s (ETA %0.2f min)"% \
            (num_jobs, 
             np.average([(jobsTime.iloc[n] - jobsTime.iloc[n-1]).seconds 
                         for n in range(1,len(jobsTime))])*num_jobs/60.0 )
    
    
    # Plot Results
    # Convert time (X) to years
    X = X.astype('f')/365.25
    
    plt.pcolor(X, Y, C, cmap=plt.cm.YlOrRd)
    #means = pandas.rolling_mean(pandas.Series(means), 10)
    plt.plot(X[:,1], means, color='k', label='Mean')
    plt.plot(X[:,1], medians, color='b', label='Median')
    plt.plot(X[:,1], low_25, color='g', label='Low25')
    plt.plot(X[:,1], high_25, color='g', label='High25')
    plt.colorbar().set_label('Probability Higher/Lower than Median')    
    plt.legend(loc='upper left')
    plt.xlabel('Years')
    plt.ylabel('Return')
    plt.grid(axis='y')
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: '%0.2f%%' %(x*100)))
    plt.show()
       
    plt.figure()
    plt.plot(X[:,1], wastedTime)
    plt.title("Average number of days I lost waiting to invest")
    plt.show()
    
    print "Exporing data to file simulation.dat..."
    import shelve
    sh = shelve.open("simulation.dat")
    sh['X'] = X
    sh['Y'] = Y
    sh['C'] = C
    sh['means'] = means
    sh['medians'] = medians
    sh['low_25'] = low_25
    sh['high_25'] = high_25
    sh['wastedTime'] = wastedTime
    sh.close()
    
    print "Done.  Execution took ",  (pandas.datetime.now()- _startTime).seconds, " seconds"