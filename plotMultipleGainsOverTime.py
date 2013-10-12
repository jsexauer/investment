import shelve
import matplotlib.pylab as plt



def pltAgainst(a, label, clr):
    X = a['X']
    low_25 = a['low_25']
    high_25 = a['high_25']
    medians = a['medians']

    plt.plot(X[:,1], low_25, ':', color=clr)
    plt.plot(X[:,1], high_25, ':', color=clr)
    plt.plot(X[:,1], medians, color=clr, label=label)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: '%0.2f%%' %(x*100)))
    
rnd = shelve.open("randomEntry.dat")
delay = shelve.open("delayedEntryStrat.dat")

pltAgainst(rnd, 'RandomEntry', 'k')
pltAgainst(delay, 'TimingStrat', 'b')
plt.legend()
plt.show()