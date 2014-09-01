"""
Parsing functions for CSV files from various institutions
"""




def parseFidelity(csvFile,db):
    """
    Fidelity files have the following structure:
    Date = As MM/DD/YYYY
    Investment = Name of fund (not ticker)
    Transaction Type = {CONTRIBUTION/DIVIDEND}
    Amount = Total ammount contributed
    Shares/Unit = Volume of shares purchased
    
    Other notes:
    Lines 1-5: File Header
    Line 6: Column Header
    Line 7+: Data
    Amount is in quotes
    Shares/Units is in quotes
    
    Ex:
    07/30/2013,FID GROWTH CO K,CONTRIBUTION,"355.29","3.141"
    """
    # Define mapping between Fiedlity terms and my terms
    actionMap = {
        'CONTRIBUTION':     'Buy',
        'DIVIDEND':         'Reinv Div'
        }
    symbolMap = {
        'FID GROWTH CO K':          'FGCKX',
        'FID FRDM INDX 2055 W':     'FDEWX'
        }
    
    
    # Actually Parse File
    import csv
    f = csv.reader(open(csvFile))
    
    # Advance to data
    for l in f:
        if l == ['Date', 'Investment', 'Transaction Type', 'Amount', 'Shares/Unit']:
            break
    
    for d in f:
        print "Parsing line ", d
        try:
            action = actionMap[d[2]]
        except KeyError:
            raise parseException('Action "%s" not in actionMap for Fidelity files' % d[2])
        try:
            symbol = symbolMap[d[1]]
        except KeyError:
            raise parseException('Symbol "%s" not in symbolMap for Fidelity files' % d[1])
            
        do = insertTransaction(db=db, date=d[0], 
                          action=action, 
                          symbol=symbol, 
                          qty=float(d[4].replace(',','')), 
                          price=float(d[3].replace(',',''))/float(d[4].replace(',','')), 
                          fees=0, 
                          sourceLine=str(d),
                          account='PJM 401k')
        if do != True:
            print "   > " + do
    db.commit()
    print "Done."
                        

        

    
def parseSchwab(csvFile,db):
    """
    Schwab files have the following strucutre:
    Date = As MM/DD/YYYY
    Action = {BUY/SELL/(Blank)}
    Quantity = Volume of shares purchased
    Symbol = Symbol
    Description
    Price = Price of asset in $/share
    Amount = Amount of transaction [Price*Quantity]
    Fees&Comm = Ammount for fees and commision
    
    OtherNotes:
    Line 1 = File Header
    Line 2 = Column Header
    Line 3+ = Data
    All fields are in quotes
    Currency values have a "$"
    
    Ex:
    "12/18/2012","Buy",".68","TWCUX","AMERICAN CENTURY ULTRA  FD INV CL type: REINVEST DIVIDEND","$26.37","-$17.94",""
    """
    # Define mapping between fidelity terms and my terms
    actionMap = {
        'Buy':     'Buy',
        'Sell':    'Sell'
    }
    
    f = open(csvFile)
    f.next()
    if f.next() != '"Date","Action","Quantity","Symbol","Description","Price","Amount","Fees & Comm"\n':
        raise parseException("Cannot read file.  Schwab appears to have changed their format.")
    for l in f:
        print "Parsing line ", l.strip()[0:45] + "..."
        d = l.split(',')
        d = [a.replace('"','').replace("$",'') for a in d]
        
        if d[1] == "":
            print "   > Skipping this transaction.  No action take"
            continue
        
        try:
            action = actionMap[d[1]]
        except KeyError:
            raise parseException('Action "%s" not in actionMap for Schwab files' % d[1])
        
        if d[4].find('REINVEST DIVIDEND') != -1:
            action = "Reinv Div"
        
        if d[7].strip() == '':
            d[7] = 0
        
        do = insertTransaction(db=db, date=d[0], 
                          action=action, 
                          symbol=d[3], 
                          qty=float(d[2]), 
                          price=float(d[5]), 
                          fees=float(d[7]), 
                          sourceLine=l,
                          account='Schwab')    
        if do != True:
            print "   > " + do
    db.commit()
    print "Done."    
    
def parseVanguard(csvFile,db):
    """
    Vanguard files have 4 parts:
        - First, description of current holdings in IRA
        - Second, transaction in IRA
        - Third, description of current holdings in IRA-Trading
        - Fourth, transactions in IRA-Trading
    
    IRA has the following structure:
    Account Number
    Trade Date = As MM/DD/YYYY
    Process Date
    Transaction Type = {Buy/Distribution/Sell/Exchange}
    Transaction Description
    Investment Name = Must be parsed into a symbol
    Share Price = $/Share
    Shares = Volumn of shares
    Gross Amount = Cost of transaction, including fees
    Net Amount = Cost of transaction, not including fees (SharePrice*Shares)
    Ex:
    88062994095,2013-07-01,2013-07-01,Buy,2013 EMPLOYEE CONTRIBUTION,Mid-Cap Growth Index Inv,30.98,96.837,3000.0,3000.0
    
    IRA-Trading has the following structure:
    Account Number
    Trade Date
    Settlement Date
    Transaction Type = {Dividend/Sweep/Buy/Sell}
    Transaction Description
    Investment Name
    Symbol
    Shares
    Share Price
    Prinicipal Amount
    commission Fees
    Net Amount
    Accrued Intrest
    Account Type
    Ex:
    66949649,2013-06-28,2013-06-28,Dividend,DIVIDEND PAYMENT,VANGUARD FTSE PACIFI,VPL,0.0,0.0,7.95,0.0,7.95,0.0,CASH,
    
    Other Notes:
    Some lines end in a trailing quote
    Sells are negative
    """
    # Define mapping between Fiedlity terms and my terms
    actionMap = {
        'Buy':          'Buy',
        'Sell':         'Sell',
        'Distribution': 'Reinv Div',
        'Dividend':     'Reinv Div'
        }
    symbolMap = {
        'Prime Money Mkt Fund':         'VMMXX',
        'Small-Cap Growth Idx Inv':     'VISGX',
        'Mid-Cap Growth Index Inv':     'VMGIX'
        }
    
    
    # Actually Parse File
    f = open(csvFile)
    
    # Advance to first data block
    for l in f:
        if l == "Account Number, Trade Date, Process Date, Transaction Type, Transaction Description, Investment Name, Share Price, Shares, Gross Amount, Net Amount,\n":
            break
        
    for l in f:
        if l == '\n':
            break   # Move to next data block
        print "Parsing line ", l.strip()[0:45] + "..."
        d = l.split(',')
        
        
        if d[3] == 'Exchange':
            if float(d[7]) < 0:
                # This is a "Sell" exchange
                d[3] = 'Sell'
            else:
                d[3] = 'Buy'

        
        try:
            action = actionMap[d[3]]
        except KeyError:
            raise parseException('Action "%s" not in actionMap for Vanguard files' % d[3])
            
        try:
            symbol = symbolMap[d[5]]
        except KeyError:
            raise parseException('Symbol "%s" not in symbolMap for Vanguard files' % d[5])
        
        
        do = insertTransaction(db=db, date=d[1], 
                          action=action, 
                          symbol=symbol, 
                          qty=float(d[7]), 
                          price=float(d[6]), 
                          fees=0, 
                          sourceLine=l,
                          account='IRA')    
        if do != True:
            print "   > " + do        
    
    ######
    # Advance to second data block
    print "Now looking in second data block..."
    for l in f:
        if l == "Account Number,Trade Date,Settlement Date,Transaction Type,Transaction Description,Investment Name,Symbol,Shares,Share Price,Principal Amount,Commission Fees,Net Amount,Accrued Interest,Account Type,\n":
            break
        
    for l in f:
        if l == '\n':
            break   # Move to next data block
        print "Parsing line ", l.strip()[0:45] + "..."
        d = l.split(',')
        
        
        if d[3] == 'Sweep':
            print "   > Skipping line.  Sweep transaction."
            continue
        if d[4] == 'DIVIDEND PAYMENT':
            print "   > Skipping line.  Dividend payment."
            continue
    
        if d[3] == 'Dividend':
            # In vanguard files, for dividend transactions, Share Price is 0
            # We must re-derive the share price
            d[8] = -float(d[11])/float(d[7])
        
        
        try:
            action = actionMap[d[3]]
        except KeyError:
            raise parseException('Action "%s" not in actionMap for Vanguard files' % d[3])
        
        
        do = insertTransaction(db=db, date=d[1], 
                          action=action, 
                          symbol=d[6], 
                          qty=float(d[7]), 
                          price=float(d[8]), 
                          fees=float(d[10]), 
                          sourceLine=l,
                          account='IRA-Trading')    
        if do != True:
            print "   > " + do
    
    db.commit()



from mint_api import Mint
from pprint import pprint
def parseMint(accounts_map, db):
    raise NotImplementedError('Unable to pair transactions :(')
    mint = Mint('genericcarbonlifeform@gmail.com', raw_input('Mint Password:'))
    mint.login()
    
    # Define mapping between mint terms and my terms
    account_map = {
        'House Account':        'Schwab',
        'PJM INTERCONNECTION':  'PJM 401k',
        'Jason M. Sexauer Roth IRA Brokerage Account': 'IRA-Trading',
        'Vanguard Account':     'IRA',
    }
    def _process_symbol(t):
        if t['symbol'] != '':
            return t['symbol']
        else:
            try:
                ans = {'FID GROWTH CO K':           'FGCKX',
                       'FID FRDM INDX 2055 W':      'FDEWX',
                       'FID FRDM INDX 2055':        'FDEWX',
                       'NUVEEN PA MUNI BOND CL A':  'FPNTX',
                       'SHELTON NASDAQ 100 INDEX FD':'NASDX',
                       'Mid-Cap Growth Index Inv - Dividend': 'VMGIX',
                       'Small-Cap Growth Idx Inv - Dividend': 'VISGX',
                       'BANK INT 011614-021514': '',
                       'Tfr AMERICAN HERITAGE, JASON SEXAUER': '',
                       'AMERICAN CENTURY ZERO COUPON 2020 INV': 'BTTTX',
                       'COLUMBIA MID CAP GROWTH CL Z':  'CLSPX',
                       'AMERICAN CENTURY ULTRA FD INV CL':  'TWCUX',
                       
                       }[t['omerchant']]
            except KeyError:
                pprint(t)
                raise Exception('No Symbol: %s'%t['omerchant'])
            return ans

    trans = []
    expecting_reinvest = []
    for t in mint.get_transactions(investment=True):
        for k in ('odate','category','symbol','omerchant','shares','amount','txnType','isBuy','isSell','isDebit'):
            print "  {0:<20}: {1}".format(k, t[k])
        print '-'*15
        
        qty = float(t['shares'])
        amount = float(t['amount'].replace('$','').replace(',',''))
        symbol = _process_symbol(t)
        
        if qty == 0:
            # Hopefully a "Buy" transaction comes along which matches this
            # transaction.
            expecting_reinvest.append((symbol, amount))
        else:
            trans.append({
                'date':     pandas.Timestamp(t['date']),
                'action':   'Sell' if t['isDebit'] else 'Buy',
                'symbol':   symbol,
                'qty':      qty,
                'price':    amount/qty,
                'fees':     0,
                'sourceLine':str(t),
                'account':  account_map[t['account']]
            
            })

    for e in expecting_reinvest:
        # Make sure we can find a transaction
        d = filter(lambda x:x['symbol']==e[0] and x['qty']==e[1], trans)
        if len(d) == 0:
            raise Exception("Expected to find reinvest for %s,%s" % e)
        if len(d) > 1:
            raise Exception("Multiple canidates found for %,%ss" % e)
        d[0]['action'] = 'Reinv Div'

    pprint(t)
    
    
    
    
    
class parseException(Exception):
    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, message)
    
    
def insertTransaction(db, date, action, symbol, qty, price, fees, sourceLine, account):
    # See if this already exists
    cur = db.cursor()
    cur.execute("""SELECT * FROM transactions WHERE 
        TR_DATE = ?
        and ACTION = ?
        and SYMBOL = ?
        and QTY = ?""", (date, action, symbol, qty))
    if len(cur.fetchall()) > 0:
        return "Skipping this transaction as it appears to already be in the database."
    
    db.execute("""INSERT INTO transactions 
        (TR_DATE, ACTION, SYMBOL, QTY, PRICE, FEES, SOURCE_LINE, ACCOUNT) VALUES
        (?,         ?,      ?,      ?, ?    , ?     , ?,        ?)""",
        (date, action, symbol, qty, price, fees, sourceLine, account))
    return True
    
    
    
    
if __name__ == '__main__':
    import sqlite3
    db = sqlite3.connect("transactions.db")
    parseFidelity("sensitive_data/fidelity.csv",db)
    parseSchwab("sensitive_data/schwabMod.csv",db)
    parseVanguard("sensitive_data/vanguard.csv", db)
    
    
    