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
    interBonds  = ['AGD1Z','BTTTX','BCOSX','BHYSZ','CFBNX','DODIX','FIIFX',
                   'JAFIX','JAHYX','LSBRX','MFDAX','MGFIX','MWTRX','MFB1Z',
                   'PFODX','PRRDX','PTTDX','PIOBX','CPHYX','CMP1Z','STHTX',
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

numTests = 5
for n in xrange(numTests):
    # Test different versions of the same portfolio
    strategy = 'aggresive'
    sDate = (2003,1,1)
    eDate = (2013,10,10)   
    maxDaysHeld = 365*7
    
    portfolio = createPortfolio(ALLOCATION_STRATEGY[strategy])
    
    print "Test portfilo %d: %s" % (n, portfolio)
    testPortfilo(portfolio,sDate,eDate,maxDaysHeld,
                 outputFilename='test_%d.dat' % n,
                 silent=True)

# Plot the results
colors = 'bgrcmykw'
for n in xrange(numTests):
    with shelve.open('test_%d.dat' % n) as f:
        pltAgainst(f, 'Portfolio %d'%n, colors[n])
plt.legend()
plt.show()