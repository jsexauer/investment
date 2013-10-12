# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 18:37:23 2011

@author: jev
"""


from urllib import urlretrieve
from urllib2 import urlopen, HTTPError
from pandas import Index, DataFrame
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import shelve

def grabSymbol(symbol, sDate, eDate):
    urlStr = 'http://ichart.finance.yahoo.com/table.csv?s={0}&a={1}&b={2}&c={3}&d={4}&e={5}&f={6}'.\
    format(symbol.upper(),sDate[1]-1,sDate[2],sDate[0],eDate[1]-1,eDate[2],eDate[0])
    #print 'Downloading from ', urlStr
    try:
        lines = urlopen(urlStr).readlines()
    except HTTPError:
        raise RuntimeError("Yahoo does not have data for symbol'%s'" % symbol)
    
    
    dates = []
    data = [[] for i in range(6)]
    #high
    
    # header : Date,Open,High,Low,Close,Volume,Adj Close
    for line in lines[1:]:
        fields = line.rstrip().split(',')
        dates.append(datetime.strptime( fields[0],'%Y-%m-%d'))
        for i,field in enumerate(fields[1:]):
            data[i].append(float(field))
       
    idx = Index(dates)
    data = dict(zip(['open','high','low','close','volume','adj_close'],data))
    
    # create a pandas dataframe structure   
    df = DataFrame(data,index=idx).resample('1D', fill_method='pad').sort()
    return df

class calcInflation:
    def __init__(self, loadLUT=True):
        self.LUT = {}
        if loadLUT:
            self.openLUT()
    
    def calcInflation(self, amount, sYear, eYear):
        """Calc inflation from Look Up Table"""
        if self.LUT == {}:
            raise "Built Look Up Table first using buildLUT or openLUT method."
        try:
            return amount*self.LUT[sYear][eYear]
        except KeyError:
            raise "%s or %s not in LUT.  Build LUT using buildLUT" % (sYear, eYear)
    
    def buildLUT(self, sYear, eYear, fname="inflation.dat"):
        print "Building LUT"
        for y1 in range(sYear, eYear+1):
            print "  > %s" % y1
            self.LUT[y1] = {}
            for y2 in range(sYear, eYear+1):
                self.LUT[y1][y2] = self.calcInflationURL(1000000,y1,y2)/1000000.0
        print "Finished Building LUT"
        a = shelve.open(fname)
        a['LUT'] = self.LUT
        a.close()
        print "LUT saved to file."
    
    def openLUT(self, fname="inflation.dat"):
        """Open LUT built previously"""
        a = shelve.open(fname)
        self.LUT = a['LUT']
        a.close()
            
            
        

    def calcInflationURL(self, amount, sYear, eYear):
        """Find Inflation from CPI index from US BLS info"""
        try:
            import urllib2
            import re
        
        
       
            url = 'http://data.bls.gov/cgi-bin/cpicalc.pl?cost1=%f&year1=%d&year2=%d' % (amount, sYear, eYear)
            req = urllib2.Request(url)
            urllib2.urlopen(req)
        
            page_fetch = urllib2.urlopen(req)
            output = page_fetch.read()
        
            search = '<p><span id="answer">\$(.*?)</span></p>'
            result = re.findall(r'' + search, output, re.S)
        
            if len(result) == 1:
                amount = float(result[0].replace(',',''))
            else:
                print 'Unable to Convert CPI'
                print url
                amount = np.nan
            return amount
        except urllib2.URLError as e:
            print e    

if __name__ == '__main__':
    df = grabSymbol('F', (2005,1,1), (2013,8,2))