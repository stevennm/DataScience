import yfinance as yf
import pandas as pd
import math
import streamlit as st

st.title('MACD strategy advisor on CEDEARs')

# yf accepts lists as well

ticks = '''AVY KOF LLY HL IBN ING ERIC NUE SNA TIIAY TEF TRV AAPL AMZN TSLA MELI GOLD WFC PBR KO
PFE MSFT VALE NFLX BBD V BA DIS HMY JPM NOK XOM INTC BABA GLOB ARCO WMT GOOGL C MCD FB AGRO ERJ AMD DESP AUY QCOM
T UN ABEV NVDA X MMM OGZPY AXP BG AZN GE MO PG PYPL ITUB SNE IBM JNJ AIG TWTR BBVA CSCO ABT EBAY GILD SNAP AMX CVX
TRIP COST RDSB.L HSBC PEP BP LMT NKE ORCL VZ CRM HD TOT BIDU CL SLB CHL GSK TX LVS HPQ LYG CS AMGN SBUX DE FDX CAT TXN
BCS NEM RIO UGP BSBR FCX JD BRFS XRX VOD TSU GGB CX GS MRK TSM ADBE BIIB YELP SID NVS BHP MDT INFY TGT TM USB SBS DD
NGG CBD BMY HNP FMX SAP PTR VIV SUZ HMC SNP CAR CDE YZCAY SIEGY CHA MSI GRMN TMO HON VRSN DEO KMB ADP BAC RTX'''

# si existe el archivo entonces no descargar. o googlear algun sistema de cache

st.text('Loading data...')
df = yf.download(tickers=ticks, period='200d')[['Close']]
df = df.set_index(pd.DatetimeIndex(df.index.values))
df.index.name = 'Dates'
st.text('Data loaded successfully')

# change Close to the 2nd level so i can the add MACD and Signal

df.dropna(axis=0)
df = df.swaplevel(axis='columns').round(2)
df.to_csv('cache.csv')

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df)

# i think i can shrink it a bit by creating a stocks list and iterating over it as strings and then using that in the
# loop

for i in range(len(df.columns.values)):
    ShortEMA = df[df.columns.values[i][0]].Close.ewm(span=12, min_periods=0, adjust=False).mean()
    LongEMA = df[df.columns.values[i][0]].Close.ewm(span=26, adjust=False).mean()
    MACD = (ShortEMA - LongEMA).round(2)
    signal = MACD.ewm(span=9, adjust=False).mean().round(2)
    df[df.columns.values[i][0], 'MACD'] = MACD
    df[df.columns.values[i][0], 'Signal'] = signal

# by default pandas puts new columns at the end so this is to rearrange
df = df.sort_index(axis=1)

stocks = []
for i in range(len(df.columns)):
    stocks.append(df.columns[i][0])

stocks = list(dict.fromkeys(stocks))


# advice when to buy according to macd

def buy_or_not(data, dif, buys=[], nothings=[]):
    for stock in stocks:
        signal1d = data[stock, 'Signal'][-1]
        macd1d = data[stock, 'MACD'][-1]
        signal2d = data[stock, 'Signal'][-2]
        macd2d = data[stock, 'MACD'][-2]
        if data[stock, 'Close'][-1] == 0 or math.isnan(signal1d):
            nothings.append('No values for ' + stock)
        elif signal1d > macd1d and math.isclose(signal1d, macd1d, rel_tol=dif):
            buys.append('Buy ' + stock)
        elif signal1d == macd1d and signal2d > macd2d:
            buys.append('Buy ' + stock)
        elif signal1d < macd1d and signal2d > macd2d:
            buys.append('Buy ' + stock)
        else:
            nothings.append('Nothing to do with  ' + stock)
    return nothings, buys


nothings, buys = buy_or_not(df, 0.1)

st.subheader('These are the results:')
st.write(buys)

st.sidebar.subheader('Tweaks')
rel_error = st.sidebar.slider('Relative error (default: 0.1)', min_value=0.0, max_value=1.0, value=0.1, step=0.1)

# ahora a plotear, la idea seria que plotee solamente el que yo elijo de la lista, solo macd (o tambien curva de
# precios?)

# plt.plot(df.ds, macd, label='GOLD MACD', color='#EBD2BE')
# plt.plot(df.ds, exp3, label='Signal Line', color='#E5A4CB')
# plt.legend(loc='upper left')
# plt.show()