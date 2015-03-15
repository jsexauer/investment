import pandas, sqlite3
from investmentLib import *
import matplotlib.pylab as plt
import operator

db = sqlite3.connect("transactions.db")
cur = db.cursor()

# skipping  'VMMXX', 'CLS1Z'
symbols = """
BTTTX
CLSPX
FDEWX
FGCKX
FPNTX
FRSPX
NASDX
TWCUX
VISGX
VMGIX
VOT
VPL
""".split('\n')[1:-1]
plt.close('all')

def plotVsCostBasis(gains):
    """gains is a pandas data frame with at least two columns.  One must be
    named 'CostBasis.'  All the others will be summed together, assumed to be
    stocks
    """
    symbols = list(gains.columns)
    symbols.remove('CostBasis')
    
    plt.figure()
    unrealizedGains = gains[symbols].sum(axis=1)
    unrealizedLosses = unrealizedGains.where(unrealizedGains < 0)
    unrealizedGains = unrealizedGains.where(unrealizedGains >= 0)
    unrealizedGains.add(gains['CostBasis']).plot(color='g', label='Unrealized Gains')
    unrealizedLosses.add(gains['CostBasis']).plot(color='r', label='Unrealized Losses')
    gains['CostBasis'].plot(label='Cost Basis', color='k')
    plt.fill_between(gains.index.to_pydatetime(), 
                     gains['CostBasis'].tolist(),
                     unrealizedGains.add(gains['CostBasis']).tolist(), color='g', alpha=.75)
    plt.fill_between(gains.index.to_pydatetime(), 
                     unrealizedLosses.add(gains['CostBasis']).tolist(),
                     gains['CostBasis'].tolist(), color='r', alpha=.75)
    plt.legend(loc='upper left')
    plt.show()

df = {}
# Grab market information for each stock
for s in symbols:
    cur.execute("SELECT * FROM transactions WHERE symbol = ?", (s, ))
    df[s] = pandas.DataFrame(cur.fetchall())
    df[s].columns = [a[0] for a in cur.description]
    df[s].index = pandas.to_datetime(df[s].TR_DATE)
    df[s] = df[s].sort_index()
    # Add in today
    df[s] = df[s].append(pandas.Series({'QTY': 0}, 
                         name=pandas.to_datetime(pandas.datetime.now().date().ctime())))
    df[s]['CostBasis'] = df[s].QTY.mul(df[s].PRICE).cumsum()
    df[s]['QTY'] = df[s].QTY.cumsum()
    df[s] = df[s].resample('1D', fill_method='pad')
    
    market = grabSymbol(s, df[s].index.min().timetuple(), 
                        df[s].index.max().timetuple())
    df[s]['MktValue'] = market.close.mul(df[s].QTY)
    df[s]['Gains'] = df[s]['MktValue'].sub(df[s]['CostBasis'])
    
    plotVsCostBasis(df[s][['Gains', 'CostBasis']])
    plt.title(s)

# Find longest history
lens = {len(v.index): k for k,v in df.iteritems()}
idx = df[lens[max(lens.keys())]].index

gains = pandas.DataFrame(columns=['CostBasis', ] + symbols, index=idx)
gains = gains.fillna(0)
for s, d in df.iteritems():
    gains['CostBasis'] = gains['CostBasis'].add(d['CostBasis'], fill_value=0)
    gains[s] = d['MktValue'].sub(d['CostBasis'])
plotVsCostBasis(gains)        







# Figure out principle and gains by stock
perUnit = True
if perUnit:
    for s in symbols:
        gains[s] = gains[s].div(df[s].CostBasis)


fillLow = pandas.DataFrame(columns=symbols, index=idx)
fillHigh = pandas.DataFrame(columns=symbols, index=idx)
for i in gains.index:
    d = {s: gains.fillna(0).get_value(i,s) for s in symbols}
       
    neg = {}
    pos = {}
    for k, v in d.iteritems():
        if v < 0:
            neg.update({k: v})
        elif v > 0:
            pos.update({k: v})
    pos = sorted(pos.iteritems(), key=operator.itemgetter(1))
    neg = sorted(neg.iteritems(), key=operator.itemgetter(1))[::-1]
    
    cum_sum = 0
    for k, v in neg:
        fillHigh.ix[i,k] = cum_sum
        cum_sum += v
        fillLow.ix[i,k] = cum_sum
    cum_sum = 0
    for k,v in pos:
        fillLow.ix[i,k] = cum_sum
        cum_sum += v
        fillHigh.ix[i,k] = cum_sum

plt.figure()
for i, s in enumerate(symbols):
    plt.fill_between(fillLow.index.to_pydatetime(), 
                     fillHigh[s].tolist(), fillLow[s].tolist(),
                     color=plt.cm.jet(float(i)/len(symbols)))
    plt.plot(fillLow.index.min().to_pydatetime().toordinal() - 100, 0, label=s,
             color=plt.cm.jet(float(i)/len(symbols)), linewidth=7)
plt.xlim(fillLow.index.min().to_pydatetime().toordinal(), 
         fillLow.index.max().to_pydatetime().toordinal())
plt.legend(loc='upper left')
plt.show()