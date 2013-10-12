# Test out some asset allocation strategies
from holdingTimes import main as testPortfilo
from plotMultipleGainsOverTime import pltAgainst
from random import choice
import shelve
import matplotlib.pylab as plt

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
        muniBonds  = .15,
        interBonds  = .3,
    ),
    homeFund2 = dict(
        largeCapG   = .35,
        midCapV     = .2,
        interBonds  = .45,
    ),
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
                
    

if __name__ == '__main__':
    from numpy import linspace
    sDate = (2003,1,1)
    eDate = (2013,10,10)   
    maxDaysHeld = 365*7
    numTests = 30
    
    # Make sure our allocations are well formed
    if not checkAllocationStrats():
        raise Exception('Allocations are malformed.')
    
    # Colors for plotting
    colors = plt.cm.rainbow(linspace(0, 1, numTests))
    
    # Test each investment strategy
    for strategy in ALLOCATION_STRATEGY.keys():
        print '\n===%s===' % strategy
        for n in xrange(numTests):
            # Test different versions of the same portfolio        
            portfolio = createPortfolio(ALLOCATION_STRATEGY[strategy])
            
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
    
    # Plot all of them together
    plt.figure()
    colors = plt.cm.rainbow(linspace(0, 1, len(ALLOCATION_STRATEGY.keys()) ))
    for nstrat, strategy in enumerate(ALLOCATION_STRATEGY.keys()):
        for n in xrange(numTests):
            f = shelve.open(r'data\%s_%d.dat' % (strategy, n))
            pltAgainst(f, '%s #%d'% (strategy, n), colors[nstrat])
            f.close()
    plt.legend()
    plt.title('All Strategies')
    plt.show()