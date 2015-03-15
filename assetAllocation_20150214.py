"""
Asset Allocation Update
14 Feb 2015

Doing some benchmarking on how well my investment strategies sussed out.

"""
import shelve

from assetAllocation import (ALLOCATION_STRATEGY, testStrategies, 
                             plotResults, testPortfilo)

maxDaysHeld = 365*7 # Hold for 7 years

if __name__ == '__main__':
    '''
    # First, unzip HomeFundInvestmentData_Oct29 into data directory
    # Here were the top 3 portfolios from last time, plus #61.
    #  #61 was an underperformer but I want to see how well it does with updated
    #  data.
    best = [78,101,108,61]
    plotResults(['homeFund3'],199, best)
    
    # Print out their allocations
    for d in best:
        f = shelve.open(r'data\%s_%d.dat' % ('homeFund3', d))
        print d, ':', f['portfolio']
    '''
    
    new_portfolios = {
        1: [('NASDX', 0.55), ('FPNTX', 0.15), ('BTTTX', 0.3)], # Best (#108)
        2: [('BIAGX', 0.55), ('PTPAX', 0.15), ('BTTTX', 0.3)],
        3: [('FKDNX', 0.55), ('FPNTX', 0.15), ('BTTTX', 0.3)],
        99: [('PRGFX', 0.55), ('MFPAX', 0.15), ('JAHYX', 0.3)] # Worst (#61)
    }
    
    '''
    # Rebuild test data just to verify I still remember how functions work
    sDate = (2003,1,1)
    eDate = (2013,10,10)
    for label, portfolio in new_portfolios.iteritems():
        print "Test portfilo %s: %s" % (label, portfolio)
        testPortfilo(portfolio,sDate,eDate,maxDaysHeld,
                     outputFilename=r'data\2013_%s.dat' % label,
                     silent=True)
    
    plotResults(['2013'], 999, new_portfolios.keys())
    '''
    
    # Ok, the above plot results gave the portfolios in the expected order,
    #  let's see what they look like now that about 1.5 years have passed
    '''
    sDate = (2003,1,1)
    eDate = (2014,12,31)
    for label, portfolio in new_portfolios.iteritems():
        print "Test portfilo %s: %s" % (label, portfolio)
        testPortfilo(portfolio,sDate,eDate,maxDaysHeld,
                     outputFilename=r'data\latest_%s.dat' % label,
                     silent=True)
    '''
    plotResults(['2013'], 999, new_portfolios.keys())
    plotResults(['latest'], 999, new_portfolios.keys())  
    
    # Asset allocation order held!  Looks like strategy is still valid.