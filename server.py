import base64
from datetime import datetime
from io import BytesIO
from itertools import chain
import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
from flask import Flask, request, jsonify
from matplotlib import cm
from flask_cors import CORS, cross_origin
from flask.helpers import send_from_directory

app = Flask(__name__, static_folder='client/build', static_url_path='')
cors=CORS(app)
#app.config['CORS_HEADERS'] = "Content-Type"
#web: gunicorn --bind 0.0.0.0:$PORT server:app

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



@app.route('/')
@cross_origin()
def serve():
    return send_from_directory(app.static_folder, 'index.html')



if __name__ == "__main__":
    app.run(debug=True)