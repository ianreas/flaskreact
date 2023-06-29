import base64
from datetime import datetime, timedelta
from io import BytesIO
from itertools import chain
import matplotlib

import plotly.express as px

import plotly.io

import requests 

from bs4 import BeautifulSoup

from sec_api import InsiderTradingApi

insiderTradingApi = InsiderTradingApi("860b7c1c0047049ae6f787034217d581a563fb763e4c8deb8422304d27cbd7da")

import json


from yahoofinancials import YahooFinancials

import pandas as pd

import re

import os

import psycopg2



#import datetime

from waitress import serve


matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
from flask import Flask, request, jsonify
from matplotlib import cm
from flask_cors import CORS, cross_origin
from flask.helpers import send_from_directory
from plotly.graph_objs import *

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scipy import interpolate



app = Flask(__name__, static_folder='client/build', static_url_path='')
cors=CORS(app)
#app.config['CORS_HEADERS'] = "Content-Type"
#web: gunicorn --bind 0.0.0.0:$PORT server:app

@app.route('/getNewThreeDGraph', methods=['POST', 'GET'])
@cross_origin()
def threeD():
    pickedticker = request.args.get("ticker")
    stock = yf.Ticker(pickedticker)
    # store maturities
    lMaturity = list(stock.options)

    #print(lMaturity)



    today = datetime.now().date()
    # empty list for days to expiration
    lDTE = []
    # empty list to store data for calls
    lData_calls = []

    # loop over maturities
    for maturity in lMaturity:
        # maturity date
        maturity_date = datetime.strptime(maturity, '%Y-%m-%d').date()
        # DTE: difference between maturity date and today
        lDTE.append((maturity_date - today).days)
        # store call data
        lData_calls.append(stock.option_chain(maturity).calls)

    # print(lData_calls)

    # create empty lists to contain unlisted data
    lStrike = []
    lDTE_extended = []
    lImpVol = []
    for i in range(0, len(lData_calls)):
    # append strikes to list
        lStrike.append(lData_calls[i]["strike"])
        # repeat DTE so the list has same length as the other lists
        lDTE_extended.append(np.repeat(lDTE[i], len(lData_calls[i])))
        # append implied volatilities to list
        lImpVol.append(lData_calls[i]["impliedVolatility"])

    # print(lImpVol)
    # print(lStrike)

    # unlist list of lists
    lStrike = list(chain(*lStrike))        #x
    lDTE_extended = list(chain(*lDTE_extended))     #y
    lImpVol = list(chain(*lImpVol))  #z

    #np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)


    mydata = {'Strikes': lStrike, 'Days until Expiration': lDTE_extended, 'Implied Volatility': lImpVol}
    #mydata = {lStrike, lDTE_extended, lImpVol}

    df = pd.DataFrame(mydata)

    #print(df)



    column1 = df['Strikes'].values

    column2 = df["Days until Expiration"].values

    column3 = df['Implied Volatility'].values

    pivot_table = df.pivot_table(values='Implied Volatility', index='Days until Expiration', columns='Strikes')

    surface_data = pivot_table.values.tolist()

    surface_json = json.dumps(surface_data)

    surface_array = np.array(surface_data)

    nan_mask = np.isnan(surface_array)

    x_coords = np.arange(surface_array.shape[1])
    y_coords = np.arange(surface_array.shape[0])

    # Create a meshgrid of coordinate arrays
    x_mesh, y_mesh = np.meshgrid(x_coords, y_coords)

    # Flatten the coordinates and values
    x_flat = x_mesh[~nan_mask]
    y_flat = y_mesh[~nan_mask]
    z_flat = surface_array[~nan_mask]

    # Perform linear interpolation
    interp = interpolate.LinearNDInterpolator((x_flat, y_flat), z_flat)
    z_interp = interp(x_mesh, y_mesh)

    surface_array[nan_mask] = z_interp[nan_mask]

    default_value = 0.0  # Replace with the desired default value
    surface_array[np.isnan(surface_array)] = default_value



    # Convert the modified numpy array back to a list
    surface_modified = surface_array.tolist()

    # Convert the modified surface_data to JSON
    surface_json = json.dumps(surface_modified)



    #two_dim_array = np.column_stack((column1, column2, column3))

    # Reshape the 2D array into nested arrays
    #nested_array = two_dim_array.tolist()

    #json_data = json.dumps([nested_array])

    # Convert the nested array to JSON
    #json_data = json.dumps(nested_array)

    return surface_json

#@cross_origin
@app.route("/acceptStockTicker", methods=['POST', 'GET'])
@cross_origin()
def members():
    #ticker = request.get_json('ticker')
    pickedticker = request.args.get("ticker")
    data = send_imp_vol_graph(pickedticker)   #include ticker variable in this function
    return data
    

#@cross_origin
#@app.route("/sendimpvolgraph", methods=['GET'])
def send_imp_vol_graph(pickedticker):
    


    # choose a ticker and get data via yfinance
    sTicker = pickedticker
    stock = yf.Ticker(sTicker)
    # store maturities
    lMaturity = list(stock.options)
    # print(stock.options)

    # get current date
    today = datetime.now().date()
    # empty list for days to expiration
    lDTE = []
    # empty list to store data for calls
    lData_calls = []

    # loop over maturities
    for maturity in lMaturity:
        # maturity date
        maturity_date = datetime.strptime(maturity, '%Y-%m-%d').date()
        # DTE: difference between maturity date and today
        lDTE.append((maturity_date - today).days)
        # store call data
        lData_calls.append(stock.option_chain(maturity).calls)

    # print(lData_calls)

    # create empty lists to contain unlisted data
    lStrike = []
    lDTE_extended = []
    lImpVol = []
    for i in range(0, len(lData_calls)):
    # append strikes to list
        lStrike.append(lData_calls[i]["strike"])
        # repeat DTE so the list has same length as the other lists
        lDTE_extended.append(np.repeat(lDTE[i], len(lData_calls[i])))
        # append implied volatilities to list
        lImpVol.append(lData_calls[i]["impliedVolatility"])

    # print(lImpVol)
    # print(lStrike)

    # unlist list of lists
    lStrike = list(chain(*lStrike))        #x
    lDTE_extended = list(chain(*lDTE_extended))     #y
    lImpVol = list(chain(*lImpVol))  #z

    aStrike = np.array(lStrike)
    aDTE_extended = np.array(lDTE_extended)
    aImpVol = np.array(lImpVol)

    #print(len(set(aStrike)))
    #print(len(set(lDTE_extended)))





    #myX = np.reshape(aStrike, (87, 34))
    #myY = np.reshape(aDTE_extended, (87, 34))
    #myZ = np.reshape(aImpVol, (87, 34))

    #surfaceP = plt.figure()

    #aX = surfaceP.add_subplot(111, projection='3d')

    #aX.plot_surface(myX, myY, myZ)

    #aX.set_xlabel('Strike Price')
    #aX.set_ylabel('DTE')
    #aX.set_zlabel('Implied Volatility')
    #plt.title("Volatility Surface for $" + sTicker + ": IV as a Function of K and T")

    #plt.show()


    #print(lImpVol)

    # initiate figure
    fig = plt.figure(figsize=(7, 7))
    # # set projection to 3d
    axs = plt.axes(projection="3d")
    #
    # # use plot_trisurf from mplot3d to plot surface and cm for color scheme
    axs.plot_trisurf(lStrike, lDTE_extended, lImpVol, cmap=cm.jet)
    # # change angle
    axs.view_init(22, 140)
    # # add labels
    plt.xlabel("Strike")
    plt.ylabel("DTE")
    plt.title("Volatility Surface for $" + sTicker + ": IV as a Function of K and T")
    #plt.show()

    tmpfile = BytesIO()
    plt.savefig(tmpfile, format='png')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

    #with open('test.html', 'r') as file:
        # read a list of lines into data
        #data = file.readlines()

    data = '<img src=\'data:image/png;base64,{}\'>'.format(encoded)

    return jsonify({"data": data})


def makespygraph(ticker):
    df = yf.download(ticker, period='1mo', interval='60m')

    df = df.rename(columns={'Close':"Stock Price"})

    fig = px.area(df, y='Stock Price')

    #fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(xaxis=dict(showgrid=False), yaxis_range=[360, 400]) # 

    return plotly.io.to_html(fig, include_plotlyjs='cdn', full_html=False)

def makempldgraph(ticker):
    df = yf.download(ticker, period='1mo', interval='60m')

    df = df.rename(columns={'Close':"Stock Price"})

    plt.plot(df['Date'], df['Stock Price'])



@app.route("/acceptSpy", methods=['POST', 'GET'])
@cross_origin()
def spy():
    #ticker = request.get_json('ticker')
    ticker = request.args.get("ticker")
    data = makespygraph(ticker)   #include ticker variable in this function
    return jsonify({"data": data})

@app.route('/')
@cross_origin()
def serve():
    return send_from_directory(app.static_folder, 'index.html')



def downloadData(ticker):
    df = yf.download(ticker, period='1mo', interval='60m')

    df = df.rename(columns={'Close':"value"})
    df = df[['value']]

    df = df.to_json(orient='index')
    return df


@app.route('/acceptData', methods=['POST', 'GET'])
@cross_origin()
def acceptData():
    ticker=request.args.get('ticker')
    data = downloadData(ticker)
    return data

@app.route("/getTopMovers", methods=['POST', 'GET'])
@cross_origin()
def scrapeTopMovers():
   url = "https://www.quiverquant.com/"
   response = requests.get(url) 
   soup = BeautifulSoup(response.content, 'html.parser')
   movers_list = soup.find('ul', class_='movers-list')

   listTopMovers = []

   for li in movers_list.find_all('li'):
       percentage_span = li.find('span', class_='positive')
       stock_percentage = []
       if percentage_span:
           percentage = percentage_span.text.strip()
           stock_percentage.append(percentage)
       stock_span = li.find('span', class_='stock')
       if stock_span:
           stock = stock_span.text.strip()
           stock_percentage.append(stock)
       listTopMovers.append(stock_percentage)
   return listTopMovers


@app.route("/getCongressTraders", methods=['POST', 'GET'])
@cross_origin()
def scrapeCongressTraders():
    url = "https://www.quiverquant.com/"
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')

    congressTable = soup.find('table', class_="table-congressional-trades dataset-table")

    congressTableBody = congressTable.find('tbody')

    congressTableBodyRows = congressTableBody.find_all('tr')

    listCongressDataSetHTML = []

    for tr in congressTableBodyRows:
        tds = tr.find_all('td')
        infoFromTDs = []
        infoFromTDs.append(tds[0].find('a').text.strip())
        infoFromTDs.append(tds[1].find('p').text.strip())
        infoFromTDs.append(tds[1].find('span').text.strip())
        infoFromTDs.append(tds[2].find('div').find('strong').text.strip())
        infoFromTDs.append(tds[2].find('span').text.strip())
        infoFromTDs.append(tds[3].find('p').text.strip())
        infoFromTDs.append(tds[3].find('span').text.strip())

        listCongressDataSetHTML.append(infoFromTDs)
        

    print(listCongressDataSetHTML)
    return listCongressDataSetHTML

@app.route('/wsbMentions', methods=['POST', 'GET'])
@cross_origin()
def wsbMentions():
    url = 'https://apewisdom.io/api/v1.0/filter/all-stocks'
    response = requests.get(url)
    data = response.json()
    return data

""" @app.route("/getInsiderTradingData", methods=['POST', 'GET'])
@cross_origin()
def getInsiderTrading():
    insider_trades = insiderTradingApi.get_data({
    "query": {"query_string": {"query": "issuer.tradingSymbol:TSLA"}},
    "from": "0",
    "size": "50",
    "sort": [{ "filedAt": { "order": "desc" } }]
    })
    return insider_trades """

@app.route("/getInsiderTradingData", methods=['POST', 'GET'])
@cross_origin()
def getInsiderTrading():
    url = "https://www.quiverquant.com/insiders/"
    response = requests.get(url)



    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table', class_='insider-trading-table')

    tableBody = table.find('tbody')

    tableBodyRows = tableBody.find_all('tr')

    rowsData = []



    for tr in tableBodyRows:
        eachRowInfo = []
        cells = tr.find_all('td')
        for cell in cells:
            if cell.find('div'):
                
                if cell.find('span'):
                    spans = cell.find_all('span')
                    for span in spans:
                        eachRowInfo.append(span.text.strip())
                    #eachRowInfo.append(cell.find('span').text.strip())
                else: 
                    eachRowInfo.append(cell.find('div').text.strip())
            elif cell.find('a'):
                eachRowInfo.append(cell.find('a').text.strip())
            else:
                eachRowInfo.append(cell.text.strip())
        rowsData.append(eachRowInfo)
    return rowsData

@app.route('/getSectorPerformance', methods=['POST', 'GET'])
@cross_origin()
def getSectorPerformance():
    options = Options()

    # You will need to specify the binary location for Heroku 
    options.binary_location = os.getenv('GOOGLE_CHROME_BIN')

    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path=os.getenv('CHROME_EXECUTABLE_PATH'), options=options)


    options.headless = True  # Set headless mode to True to hide the browser window
    #driver = webdriver.Chrome(options=options)

    url = "https://www.quiverquant.com/"
    #response = requests.get(url)

    driver.get(url)

    driver.implicitly_wait(20)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    sector_performance_div = soup.find("ul", {"class": "sector-performance-list"})
    sectorList = sector_performance_div.find_all("li")

    sectorPerformanceList = []

    for li in sectorList:
        listInfo = []

        sectorName = li.find("strong").text.strip()
        listInfo.append(sectorName)

        percentage = li.find('span').text.strip()

        listInfo.append(percentage)

        sectorPerformanceList.append(listInfo)
    driver.close()
    return sectorPerformanceList
    

@app.route("/getOptionsChainData", methods=['POST', 'GET'])
@cross_origin()
def getOptionsChainData():
    ticker=request.args.get('ticker')

    arrayIndex = request.args.get('index')

    optionType = request.args.get('type')



    
    arrayIndex = int(arrayIndex)

    sTicker = ticker

    stock = yf.Ticker(sTicker)

    # store maturities
    lMaturity = list(stock.options)
    # print(stock.options)

    # get current date
    today = datetime.now().date()
    # empty list for days to expiration
    lDTE = []
    # empty list to store data for calls
    lData = []

    # loop over maturities
    if (optionType=='call'):
        for maturity in lMaturity:
            # maturity date
            maturity_date = datetime.strptime(maturity, '%Y-%m-%d').date()
            # DTE: difference between maturity date and today
            lDTE.append((maturity_date - today).days)
            # store call data
            lData.append(stock.option_chain(maturity).calls)
    else:
        for maturity in lMaturity:
            # maturity date
            maturity_date = datetime.strptime(maturity, '%Y-%m-%d').date()
            # DTE: difference between maturity date and today
            lDTE.append((maturity_date - today).days)
            # store call data
            lData.append(stock.option_chain(maturity).puts)

    

    #print(lData_calls[0])

    return lData[arrayIndex].to_json(orient='records')



@app.route('/getOptionChainDates', methods=['POST', 'GET'])
@cross_origin()
def getOptionDates():
    ticker=request.args.get('ticker')

    sTicker = ticker

    stock = yf.Ticker(sTicker)

    # store maturities
    lMaturity = list(stock.options)
    # print(stock.options)

    # get current date
    

    today = datetime.now().date()
    # empty list for days to expiration
    lDTE = []
    # empty list to store data for calls
    lData_calls = []

    # loop over maturities
    for maturity in lMaturity:
        # maturity date
        maturity_date = datetime.strptime(maturity, '%Y-%m-%d').date()
        # DTE: difference between maturity date and today
        lDTE.append((maturity_date - today).days)
        # store call data
        lData_calls.append(stock.option_chain(maturity).calls)

    #print(lData_calls[0])

    listOfDates = []

    for df in lData_calls:
        unformatString = df.iloc[0].values[0]
        """ unformatDate = unformatString[-6:]

        year = int(unformatDate[:2]) + 2000  # Assuming years are represented as two digits
        month = int(unformatDate[2:4])
        day = int(unformatDate[4:])

        readable_date = f"{year}-{month:02d}-{day:02d}" """

        match = re.search(r'\d{6}', unformatString)

        if match:
            date_str = match.group()
            year = int(date_str[:2]) + 2000
            month = int(date_str[2:4])
            day = int(date_str[4:])
            date = f"{year}-{month:02d}-{day:02d}"
            listOfDates.append(date)
        else:
            listOfDates.append(None)


        

    #return listOfDates
    return jsonify({"dates": listOfDates})





@app.route('/getTheCurrentPrice', methods=['POST', 'GET'])
@cross_origin()
def getTheCurrentPrice():
    ticker=request.args.get('ticker')
    yahoo_financials = YahooFinancials(ticker)
    return yahoo_financials.get_stock_price_data(reformat=True)


@app.route('/getOptionsChainCallsAll', methods=['POST', 'GET'])
@cross_origin()
def getOptionsChainCallsAll():
    sTicker = 'SPY'

    stock = yf.Ticker(sTicker)

    # store maturities
    lMaturity = list(stock.options)
    # print(stock.options)

    # get current date
    #today = datetime.now().date()

    today = datetime.date.today()
    # empty list for days to expiration
    lDTE = []
    # empty list to store data for calls
    lData_calls = []

    # loop over maturities
    for maturity in lMaturity:
        # maturity date
        maturity_date = datetime.strptime(maturity, '%Y-%m-%d').date()
        # DTE: difference between maturity date and today
        lDTE.append((maturity_date - today).days)
        # store call data
        lData_calls.append(stock.option_chain(maturity).calls)

    #print(lData_calls[0])

    json_data = [df.to_json(orient='records') for df in lData_calls]

    # Convert the list of JSON strings to a list of DataFrames
    """ array_of_dataframes = [pd.read_json(df_json) for df_json in json_data] """

    return json_data

def truncate(n, decimals=0): #rounds numbers
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def CRRBinomial(OutputFlag, AmeEurFlag, CallPutFlag, S, X, T, r, c, v, n):

    # This functions calculates CRR price, delta and gamma for of American and European options

    # This code is based on "The complete guide to Option Pricing Formulas" by Espen Gaarder Haug (2007)

    # Translated from a VBA code

    # OutputFlag:

    # "P" Returns the options price

    # "d" Returns the options delta

    # "a" Returns an array containing the option value, delta and gamma

    

    # AmeEurFlag:

    # "a" Returns the American option value

    # "e" Returns the European option value

    

    # CallPutFlag:

    # "C" Returns the call value

    # "P" Returns the put value



    # S is the share price at time t = 0 = today = price of option

    # X is the strike price

    # T is the time to maturity in years (days/365)

    # r is the risk-free interest rate

    # c is the cost of carry rate

    # v is the volatility

    # n determines the stepsize



    # Creates a list with values from 0 up to n (which will be used to determine to exercise or not)

    n_list = np.arange(0, (n + 1), 1)



    # Checks if the input option is a put or a call, if not it returns an error

    if CallPutFlag == 'C':

        z = 1

    elif CallPutFlag == 'P':

        z = -1

    else:

        return 'Call or put not defined'



   

    # Calculates the stepsize in years

    dt = T / n



    # The up and down factors

    u = np.exp(v*np.sqrt(dt))

    d = 1./u

    p = (np.exp((c)*dt)-d) / (u-d) 

    

    df = np.exp(-r * dt)

   



    # Creates the most right column of the tree

    max_pay_off_list = []

    for i in n_list:

        i = i.astype('int')

        max_pay_off = np.maximum(0, z * (S * u ** i * d ** (n - i) - X))

        max_pay_off_list.append(max_pay_off)



    # The binominal tree

    for j in np.arange(n - 1, 0 - 1, -1):

        for i in np.arange(0, j + 1, 1):

            i = i.astype(int)  # Need to be converted to a integer

            if AmeEurFlag == 'e':

                max_pay_off_list[i] = (p * max_pay_off_list[i + 1] + (1 - p) * max_pay_off_list[i]) * df

            elif AmeEurFlag == 'a':

                max_pay_off_list[i] = np.maximum((z * (S * u ** i * d ** (j - i) - X)),

                                                 (p * max_pay_off_list[i + 1] + (1 - p) * max_pay_off_list[i]) * df)

        if j == 2:

            gamma = ((max_pay_off_list[2] - max_pay_off_list[1]) / (S * u ** 2 - S * u * d) - (

                    max_pay_off_list[1] - max_pay_off_list[0]) / (S * u * d - S * d ** 2)) / (

                            0.5 * (S * u ** 2 - S * d ** 2))

        if j == 1:

            delta = ((max_pay_off_list[1] - max_pay_off_list[0])) / (S * u - S * d)

    price = max_pay_off_list[0]



    # Put all the variables in the list

    variable_list = [delta, gamma, price]



    # Return values

    if OutputFlag == 'P':

        return price

    elif OutputFlag == 'd':

        return delta

    elif OutputFlag == 'g':

        return gamma

    elif OutputFlag == 'a':

        return variable_list

    else:

        return 'Indicate if you want to return P, d, g or a'

@app.route('/getOptionsPriceMatrix', methods=['POST', 'GET'])
@cross_origin()
def getOptionsPriceMatrix():
    optionPrice = float(request.args.get('price'))

    optionType = request.args.get('type')

    optionSymbol = request.args.get('symbol')

    optionStrike = float(request.args.get('strike'))

    optionVolatility = float(request.args.get('volatility'))

    stockPrice = float(request.args.get('stockPrice'))

    def calculateFuturePossiblePrices(todayPrice, breakevenPrice):
        futurePricesArray = [todayPrice]

        step = (breakevenPrice-todayPrice)/15
        n = 1
        while(n<=15):
            futurePricesArray.append(todayPrice+(step*n))
            n+=1

        z = 1
        while(z<=15):
            futurePricesArray.insert(0, todayPrice-(step*z))
            z+=1

        for number in futurePricesArray:
            if (number<0.01):
                futurePricesArray.remove(number)

        futurePricesArray = [round(num, 2) for num in futurePricesArray]
        

            
        return futurePricesArray
    
    breakevenPrice = optionStrike + optionPrice

    possiblePrices = calculateFuturePossiblePrices(stockPrice, breakevenPrice)

    match = re.search(r'\d{6}', optionSymbol)

    if match:
        date_str = match.group()
        future_date = datetime.strptime(date_str, "%y%m%d").date()

        # Get the current date
        current_date = datetime.now().date()

        # Calculate the difference in days
        difference = future_date - current_date

        # Extract the number of days from the difference
        daysUntilExpiration = difference.days
    else:
        print('coudnt convert symbol to days')

    # Calculate the interval between each date
    interval = daysUntilExpiration // 9


    last_date = current_date + timedelta(days=daysUntilExpiration)

    dates = []

    dates.append([current_date.strftime("%B %d, %Y"), daysUntilExpiration])

    # Calculate and print the 9 equidistant dates
    for i in range(1, 10):
        date = current_date + timedelta(days=i * interval)
        difference = last_date - date
        readable_date = date.strftime("%B %d, %Y")
        dates.append([readable_date, difference.days])

    
    dates.append([last_date.strftime("%B %d, %Y"), 1])

    optionMatrixDatesByPrices = []

    if (optionType=='call'):
        for price in possiblePrices:
            rowWithDifferentDatesSamePrices = []
            for date in dates:
                if price and optionStrike and date[1]/365 and optionVolatility:
                    rounded = truncate((CRRBinomial('P', 'a', 'C', price, optionStrike, date[1]/365, 0.05, 0.05, optionVolatility, 100)), decimals=2)
                    rowWithDifferentDatesSamePrices.append(rounded)
            optionMatrixDatesByPrices.append(rowWithDifferentDatesSamePrices)
    else: 
        for price in possiblePrices:
            rowWithDifferentDatesSamePrices = []
            for date in dates:
                rounded = truncate((CRRBinomial('P', 'a', 'P', price, optionStrike, date[1]/365, 0.05, 0.05, optionVolatility, 100)), decimals=2)
                rowWithDifferentDatesSamePrices.append(rounded)
            optionMatrixDatesByPrices.append(rowWithDifferentDatesSamePrices)
    

    return [optionMatrixDatesByPrices, dates, possiblePrices]



@app.route('/getInsiderTradersFromDB', methods=['POST', 'GET'])
@cross_origin()
def getInsiderTradersFromDB():
    # Database connection details
    host = 'database-1.cnsms1pducc9.us-east-2.rds.amazonaws.com'
    port = '5432'
    database = 'postgres'
    user = 'postgres'
    password = 'muhammedik10'

    # Establish a connection to the RDS database
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )

    # Create a cursor to execute SQL queries
    cursor = conn.cursor()

    # Execute a query to retrieve the data
    query = "SELECT * FROM insider_trading"
    cursor.execute(query)

    # Fetch the data and convert it to JSON
    data = cursor.fetchall()
    json_data = json.dumps(data)

    # Close the cursor and database connection
    cursor.close()
    conn.close()

    # Print the data as JSON
    return json_data

    



    



 





if __name__ == "__main__":
    app.run(debug=True)
    #serve(app, host='0.0.0.0', port=5000)