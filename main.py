
from datetime import datetime as dt
from urllib.request import urlopen,Request
import os,time,shutil,signal
#import pymongo
stop=False
db_host='localhost'
db_port=27017
log=None

def sig_handler(sig,frame):
    global stop 
    resp=input("\nWould you like to quit [y/N]: ")
    if (resp in ["Y","y","yes"]): stop=True

# def download_file(url,fname):
#     url='https://www.ftserussell.com/files/support-documents/membership-russell-3000'
#     text=urlopen(url,timeout=5).read()
#     f=open(fname,'wb')
#     f.write(text)
#     f.close()

#data_url='https://www.ishares.com/us/products/239714/ishares-russell-3000-etf/1521942788811.ajax?fileType=xls&fileName=iShares-Russell-3000-ETF_fund&dataType=fund'
#download_file(data_url,'data')

class stock:
    def __init__(self,name,ticker):
        self.name=name 
        self.ticker=ticker
        self.db_id=None
    def __repr__(self):
        return "%s (%s)"%(self.name,self.ticker)

def load_russell3000():
    fname='iShares-Russell-3000-ETF_fund.csv'
    f=open(fname,'r')
    lines=f.read().split('\n')
    stocks=[]
    found_start=False
    for line in lines:
        items=line.split(',')
        if found_start and len(items)==15 and items[0]!='--':
            stocks.append(stock(items[1],items[0]))
        else:
            if items[0]=='Ticker':
                found_start=True
    return stocks

def get_stock_price_yahoo(ticker):
    global log
    try:
        url='https://finance.yahoo.com/quote/'+ticker+'?p='+ticker+'&.tsrc=fin-srch'
        q=Request(url) 
        q.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        q.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        text=urlopen(q,timeout=5).read().decode('utf-8')
        return text.split('Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)')[1].split(">")[1].split("<")[0]
    except Exception as e:
        try: log.write(str(e)+"\n")
        except: log.write("Couldn't write get_stock_price_yahoo error.\n")
        return False

def get_stock_price_marketwatch(ticker):
    global log
    try:
        url='https://www.marketwatch.com/investing/stock/'+ticker 
        q=Request(url) 
        q.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        q.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        text=urlopen(q,timeout=5).read().decode('utf-8')
        return text.split("h3 class=\"intraday__price")[1].split("bg-quote")[1].split(">")[1].split("<")[0]
    except Exception as e:
        try: log.write(str(e)+"\n")
        except: log.write("Couldn't write get_stock_price_marketwatch error.\n")
        return False

def init_data(tickers):
    os.mkdir('./data')
    for stock in tickers:
        f=open('data/%s.tsv'%stock.ticker,'w')
        f.write('Datetime\tPrice\n')
        f.close()
def delete_data():
    try: shutil.rmtree('data')
    except: pass

# # not being used currently
# def init_db(stocks):
#     client=pymongo.MongoClient(db_host,db_port)
#     db=client['data']
#     collection=db['stocks']
#     for stock in stocks:
#         obj={'Company':stock.name,
#              'Ticker':stock.ticker,
#              'Price':[],
#              'Timestamp':[]}
#         stock.db_id=collection.insert_one(obj).inserted_id
#     return stocks,collection

#stocks=load_russell3000()
#stocks,db=init_db(stocks)

def main():
    global log
    stocks=load_russell3000()
    delete_data()
    init_data(stocks)
    log=open('log.txt','w')

    print("Starting price collection...")
    total_iterations=0
    while not stop:
        print("Waiting for hour to begin...")
        while True:
            a=dt.now()
            if a.minute in [0,1,2]: 
                print("Starting iteration at %s"%str(a))
                log.write("Starting iteration at %s\n"%str(a))
                break
            else: time.sleep(10)
        total_iterations+=1
        print("Starting iteration number: %d"%total_iterations)
        log.write("Iteration number: %d\n"%total_iterations)
        start_iteration=time.time()
        for i,stock in enumerate(stocks):
            if stop: break
            print("Number complete: %d, Ticker: %s"%(i,stock.ticker),end="\r")
            datetime=time.time()
            price=get_stock_price_yahoo(stock.ticker)
            if price==False:
                print("\nFailed retrieving price data from Yahoo for %s, trying MarketWatch"%stock.ticker)
                price=get_stock_price_marketwatch(stock.ticker)
                if price==False:
                    print("Total error getting price for %s"%stock.ticker)
                    continue
            f=open('data/%s.tsv'%stock.ticker,'a')
            f.write("%d\t%s\n"%(datetime,price))
            f.close()
        log.write("Iteration complete in %d seconds\n"%(int(time.time())-int(start_iteration)))            
        print("Iteration complete in %d seconds"%(int(time.time())-int(start_iteration)))


signal.signal(signal.SIGINT,sig_handler)
main()








