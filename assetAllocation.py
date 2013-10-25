# Test out some asset allocation strategies
from holdingTimes import main as testPortfilo
from plotMultipleGainsOverTime import pltAgainst
from random import choice
import shelve
import matplotlib.pylab as plt
from numpy import linspace

ALLOCATION_STRATEGY = dict(
    aggresive = dict(
        largeCapG   = .3,
        midCapG     = .3,
        smallCapG   = .3,
        interBonds  = .1
    ),
    conservative = dict(
        largeCapV   = .3,
        midCapV     = .1,
        smallCapV   = .1,
        interBonds  = .4,
        muniBonds   = .1
    ),
    PABonds = dict(
        muniBonds = 1
    ),
    homeFund = dict(
        largeCapG   = .35,
        midCapV     = .2,
        muniBonds   = .15,
        interBonds  = .3,
    ),
    homeFund2 = dict(
        largeCapG   = .35,
        midCapV     = .2,
        interBonds  = .45,
    ),
    homeFund3 = dict(
        largeCapG   = .55,
        muniBonds   = .15,
        interBonds  = .3,
    ),
    homeFund4 = dict(
        largeCapG   = .7,
        interBonds  = .3,
    ),
    homeFund5 = dict(
        largeCapG   = .7,
        muniBonds   = .3,
    ),
    homeFund6 = dict(       # Like 1 (previous best), but all muni bonds
        largeCapG   = .35,
        midCapV     = .2,
        muniBonds   = .45,
    ),
    largeCapG = dict(
        largeCapG   = .33,
        largeCapG2  = .33,
        largeCapG3  = .34,
    ),
    largeCapV = dict(
        largeCapV   = .33,
        largeCapV2  = .33,
        largeCapV3  = .34,
    )
)

# From https://client.schwab.com/secure/cc/research/mutual_funds/mfs.html?path=/RESEARCH/CLIENT/MutualFunds/Screener/FindFunds
# All of these funds are:
#   * Expense Ration < 25% of market
#   * 4 or 5 star overall morningstar rating
#   * 3 year return > cat avg
#   * Min inital investment < $2.5k
#   * Open to new investors
#   * > 10 years ago inception date
FUNDS = dict(
    largeCapG   = ['TWGTX','TWCUX','BIAGX','FBGRX','FCNTX','FTQGX','FDSVX',
                   'FMILX','FOCPX','FTRNX','FKDNX','HCAIX','JRMSX','JAMRX',
                   'LGILX','LKEQX','STCAX','NASDX','TRBCX','PRGFX','PRWAX'],
    midCapG     = ['BUFTX','JAENX','NBGNX','NICSX'],
    smallCapG   = ['BSCFX','MRSCX','BCSIX','CCASX','JAVTX','ORIGX','RHJMX',
                   'WGROX'],
    largeCapV   = ['AAGPX','TWVLX','CFVLX','DHLAX','DODGX','LEXCX','STVTX',
                   'SWDSX','EQTIX','TRVLX'],
    midCapV     = ['NSEIX','TCMVX','VETAX'],
    smallCapV   = ['JASCX','NOSGX','QRSVX','SKSEX'],
    interBonds  = ['BTTTX','BCOSX','CFBNX','DODIX','FIIFX',
                   'JAFIX','JAHYX','LSBRX','MFDAX','MGFIX','MWTRX',
                   'PFODX','PRRDX','PTTDX','PIOBX','CPHYX','STHTX',
                   'SAMFX','TGFNX','TGMNX','THOPX','WTIBX'],
    # PA municipal bonds
    muniBonds  = ['APAAX','PTPAX','FPXTX','FRPAX','MFPAX','FPNTX','PTEPX'],
)
FUNDS['largeCapG2'] = FUNDS['largeCapG']
FUNDS['largeCapG3'] = FUNDS['largeCapG']
FUNDS['largeCapV2'] = FUNDS['largeCapV']
FUNDS['largeCapV3'] = FUNDS['largeCapV']

def createPortfolio(strategy):
    """Create a portfilo with the given strategy"""
    portfolio = []
    for category, pct in strategy.iteritems():
        portfolio.append((choice(FUNDS[category]), pct))
    return portfolio

def checkAllocationStrats():
    flag = False
    for name, allocation in ALLOCATION_STRATEGY.iteritems():
        for cat, pct in allocation.iteritems():
            if cat not in FUNDS.keys():
                print "Category '%s' of allocation %s bad." % (cat, name)
                flag = True
    return not flag

def plotResults(strategiesToPlot, numTests): 
    plt.xkcd()                   
    plt.figure()
    colors = plt.cm.rainbow(linspace(0, 1, len(strategiesToPlot) ))
    for nstrat, strategy in enumerate(strategiesToPlot):
        for n in xrange(numTests):
            if n == 0:
                title = '%s #%d'% (strategy, n)
            else:
                title = None
            f = shelve.open(r'data\%s_%d.dat' % (strategy, n))
            pltAgainst(f, title, colors[nstrat])
            f.close()
    plt.legend()
    plt.title('All Strategies')
    plt.show()
    
def testStrategies(strategies, numTests):
    """Main Function"""
    sDate = (2003,1,1)
    eDate = (2013,10,10)   
    maxDaysHeld = 365*7
    
    # Make sure our allocations are well formed
    if not checkAllocationStrats():
        raise Exception('Allocations are malformed.')
    
    # Colors for plotting
    colors = plt.cm.rainbow(linspace(0, 1, numTests))
    
    # Test each investment strategy
    for strategy in strategies.keys():
        print '\n===%s===' % strategy
        for n in xrange(numTests):
            # Test different versions of the same portfolio        
            portfolio = createPortfolio(strategies[strategy])
            
            print "Test portfilo %d: %s" % (n, portfolio)
            testPortfilo(portfolio,sDate,eDate,maxDaysHeld,
                         outputFilename=r'data\%s_%d.dat' % (strategy, n),
                         silent=True)
        
        # Plot the results
        plt.figure()
        for n in xrange(numTests):
            f = shelve.open(r'data\%s_%d.dat' % (strategy, n))
            pltAgainst(f, 'Portfolio %d'%n, colors[n])
            f.close()
        plt.legend()
        plt.title('Strategy: %s' % strategy)
        plt.show()
    
if __name__ == '__main__':
    numTests = 5
    strategies = {k:ALLOCATION_STRATEGY[k] for k in 
                    ['homeFund','homeFund2','homeFund3','homeFund4']}
    #testStrategies(strategies, numTests)
    
    # Plot all of them together
    strategiesToPlot = ALLOCATION_STRATEGY.keys()
    strategiesToPlot = ['conservative','homeFund','homeFund2']
    plotResults(strategiesToPlot, numTests)
