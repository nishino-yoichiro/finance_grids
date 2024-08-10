from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import json

app = Flask(__name__)
CORS(app)

def loadOrders (file):
    """
    Takes a csv file from Webull and turns the data into a dictionary with a new index
    variable as the key and a dictionary of the data as values.

    Args:
        file (str): The file path to the csv file.

    Returns:
        data_dict (dict): A dictionary with the new index variable as the key and a dictionary
        of the data as values.
    """
    df = pd.read_csv(file)
    df = df.reset_index()
    df = df[df['Status'] == 'Filled']
    data_dict = df.set_index('index').T.to_dict()
    return data_dict

def extract_date (date):
    """
    Extracts formatted date from extensive date string. "08/28/2023 13:58:39 EDT" -> "08/28/2023"

    Args:
        date (str): The extensive date string.

    Returns:
        str: The formatted date string.
    """
    return date.split(' ')[0]

def extract_time (date):
    """
    Extracts formatted time from extensive date string. "08/28/2023 13:58:39 EDT" -> "13:58:39"

    Args:
        date (str): The extensive date string.

    Returns:
        str: The formatted time string.
    """
    return date.split(' ')[1]

def getStockDict (data_dict):
    stock_dict = {}
    for key, value in data_dict.items():
        stock = value['Symbol'].split(' ')[0].upper()
        if stock not in stock_dict.keys():
            stock_dict[stock] = {}
        stock_dict[stock][key] = value
    return stock_dict

def getPLByStock(stock_dict):
    PLbyStock = {}
    for key, value in stock_dict.items():
        PLbyStock[key] = getPLOverall(value)
    return PLbyStock

def getPLOverall (data_dict):
    """
    Calculates the P&L of the data.

    Args:
        data_dict (dict): A dictionary with the new index variable as the key and a dictionary of data values

    Returns:
        float: The P&L of the data.
    """
    soldAmount = 0
    boughtAmount = 0
    for key, value in data_dict.items():
        print(round(float(value['Avg Price']) * float(value['Total Qty']) * 100, 2))
        if value['Side'] == 'Sell':
            soldAmount += round(float(value['Avg Price']) * float(value['Total Qty']) * 100, 2)
        else:
            boughtAmount += round(float(value['Avg Price']) * float(value['Total Qty']) * 100, 2)
    return soldAmount-boughtAmount

def getPLDaily (data_dict):
    """
    Calculates the P&L of the data for the day.

    Args:
        data_dict (dict): A dictionary with the new index variable as the key and a dictionary of data values

    Returns:
        dict: A dictionary with the date as the key and the P&L as the value.
    """
    dailyPL = {}
    for key, value in data_dict.items():
        date = extract_date(value['Filled Time'])
        if value['Side'] == 'Sell':
            dailyPL[date] = round(dailyPL.get(date, 0) + float(value['Avg Price']) * float(value['Total Qty']) * 100, 2)
        else:
            dailyPL[date] = round(dailyPL.get(date, 0) - float(value['Avg Price']) * float(value['Total Qty']) * 100, 2)
    return dailyPL

def getPLCumulative (data_dict):
    """
    Calculates the cumulative P&L of the data.

    Args:
        data_dict (dict): A dictionary with the new index variable as the key and a dictionary of data values

    Returns:
        dict: A dictionary with the date as the key and the cumulative P&L as the value.
    """
    cumulativePL = {}
    cumulative = 0
    for key, value in data_dict.items():
        date = extract_date(value['Filled Time'])
        if value['Side'] == 'Sell':
            cumulative += round(float(value['Avg Price']) * float(value['Total Qty']) * 100, 2)
        else:
            cumulative -= round(float(value['Avg Price']) * float(value['Total Qty']) * 100, 2)
        cumulativePL[date] = cumulative
    return cumulativePL

def getDaysPL (data_dict, date):
    """
    Calculates the P&L of the data for a specific date.

    Args:
        data_dict (dict): A dictionary with the new index variable as the key and a dictionary of data values
        date (str): The date to calculate the P&L for.

    Returns:
        list: A dictionary with the date as the key and the P&L as the value.
    """
    daysPL = []
    for key, value in data_dict.items():
        if extract_date(value['Filled Time']) == date:
            time = extract_date(value['Filled Time'])
            if value['Side'] == 'Sell':
                val = round(float(value['Avg Price']) * float(value['Total Qty']) * 100, 2)
                daysPL.append(val)
            else:
                val = round(float(value['Avg Price']) * float(value['Total Qty']) * 100, 2)
                daysPL.append(val * -1)
    return sum(daysPL)

def graphDict (dict, type='bar', timeframe = 'month'):
    """
    Graphs a dictionary.

    Args:
        dict (dict): A dictionary with the date as the key and the P&L as the value.
        type (str): The type of graph to be used. Default is 'bar'.
    """

    if timeframe == 'month':
        dates = [datetime.strptime(date, '%m/%d/%Y') for date in dict.keys()]
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
    elif timeframe == 'daily':
        dates = [datetime.strptime(date, '%H:%M:%S') for date in dict.keys()]
        start_of_day = datetime.strptime('00:00:00', '%H:%M:%S')
        dates_in_minutes = [(date - start_of_day).seconds / 60 for date in dates]
        intervalVal = round((max(dates_in_minutes) - min(dates_in_minutes)) / len(dates_in_minutes) / 10) * 10
        
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=intervalVal))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    profits = list(dict.values())

    if type == 'bar':
        colors = ['g' if profit >= 0 else 'r' for profit in profits]
        plt.bar(dates, profits, color=colors)
    elif type == 'line':
        plt.plot(dates, profits, color='black', linewidth=0.5)
        plt.fill_between(dates, profits, where=[profit >= 0 for profit in profits], color='g', interpolate=True)
        plt.fill_between(dates, profits, where=[profit < 0 for profit in profits], color='r', interpolate=True)

    plt.grid(True)
    plt.xlabel('Date')
    plt.ylabel('Profit/Loss')
    plt.title('Profit/Loss per day')
    plt.show()

def initializeAPI(file_name):
    """
    Initializes the retrieval variables.
    """
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, file_name)

    data = loadOrders(file_path)

    return data

@app.route('/api/pnl', methods=['GET'])
def get_pnl():
    file_name = request.args.get('file_name')
    data_dict = initializeAPI(file_name)
    pnl_by_day = getPLDaily(data_dict)
    total_pnl = getPLOverall(data_dict)
    cumulative_pnl = getPLCumulative(data_dict)
    result = {
        "PnL_By_Day": pnl_by_day,
        "Total_PnL": total_pnl,
        "Cumulative_PnL": cumulative_pnl
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)