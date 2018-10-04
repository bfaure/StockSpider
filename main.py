
from urllib.request import urlopen,Request
import os,time,shutil

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
    try:
        url='https://finance.yahoo.com/quote/'+ticker+'?p='+ticker+'&.tsrc=fin-srch'
        q=Request(url) 
        q.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        q.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        text=urlopen(q,timeout=5).read().decode('utf-8')
        return text.split('Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)')[1].split(">")[1].split("<")[0]
    except:
        return False

def get_stock_price_marketwatch(ticker):
    try:
        url='https://www.marketwatch.com/investing/stock/'+ticker 
        q=Request(url) 
        q.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        q.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        text=urlopen(q,timeout=5).read().decode('utf-8')
        return text.split("h3 class=\"intraday__price")[1].split("bg-quote")[1].split(">")[1].split("<")[0]
    except:
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

def main():
    stocks=load_russell3000()
    delete_data()
    init_data(stocks)

    print("Collecting stock prices...")
    while True:
        start_iteration=time.time()
        for i,stock in enumerate(stocks):
            print("Number complete: %d, Ticker: %s"%(i,stock.ticker),end="\r")
            datetime=time.time()
            price=get_stock_price_yahoo(stock.ticker)
            if price==False:
                print("\nError getting price for %s"%stock.ticker)
            else:
                f=open('data/%s.tsv'%stock.ticker,'a')
                f.write("%d\t%s\n"%(datetime,price))
                f.close()
        print("Iteration complete in %d seconds"%(int(time.time())-int(start_iteration)))


print(get_stock_price_marketwatch('GE'))
print(get_stock_price_yahoo('GE'))
#main()








