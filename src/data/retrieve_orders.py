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

def getTrades (data_dict):
    """
    Returns a dict of trades executed based on the data.

    Args:
        data_dict (dict): A dictionary with the new index variable as the key and a dictionary of data values
    
    Returns:
        dict: A dictionary with the option contract as the key and the trade data as the value.
    """
    trades = {}
    for buy in data_dict.values():
        current_pnl = trades.get(buy['Symbol'], 0)
        if buy['Side'] == 'Buy':
            trades[buy['Symbol']] = current_pnl - float(buy['Avg Price']) * float(buy['Total Qty']) * 100
        else:
            trades[buy['Symbol']] = current_pnl + float(buy['Avg Price']) * float(buy['Total Qty']) * 100
    return trades

def getAverageContractSize(data_dict):
    """
    Calculates the average contract size of the data.

    Args:
        data_dict (dict): A dictionary with the new index variable as the key and a dictionary of data values

    Returns:
        float: The average contract size of the data.
    """
    contractSize = 0
    counter = 0
    for value in data_dict.values():
        if(value['Side'] == 'Buy'):
            contractSize += float(value['Avg Price'])
            counter += 1
    return round(contractSize / counter, 2)

def getAverageContractSizeFromPastYear(data_dict):
    """
    Calculates the average contract size of the data for the past year.

    Args:
        data_dict (dict): A dictionary with the new index variable as the key and a dictionary of data values

    Returns:
        float: The average contract size of the data for the past year.
    """
    contractSize = 0
    counter = 0
    for value in data_dict.values():
        if(value['Side'] == 'Buy' and datetime.strptime(extract_date(value['Filled Time']), '%m/%d/%Y') >= datetime.now() - pd.DateOffset(years=1)):
            contractSize += float(value['Avg Price'])
            counter += 1
    return round(contractSize / counter, 2)

def getAverageWinner (trades_dict):
    """
    Calculates the average winning trade of the data.

    Args:
        trades_dict (dict): A dictionary with the option contract as the key and the trade data as the value.
    
    Returns:
        float: The average winning trade of the data.
    """
    winnerAmount = 0
    winnerCount = 0
    for value in trades_dict.values():
        if value > 0:
            winnerAmount += value
            winnerCount += 1
    return round(winnerAmount / winnerCount, 2), winnerCount

def getAverageLoser (trades_dict):
    """
    Calculates the average winning trade of the data.

    Args:
        trades_dict (dict): A dictionary with the option contract as the key and the trade data as the value.
    
    Returns:
        float: The average winning trade of the data.
    """
    loserAmount = 0
    loserCount = 0
    for value in trades_dict.values():
        if value < 0:
            loserAmount += value
            loserCount += 1
    return round(loserAmount / loserCount, 2), loserCount

def getPLByStock(stock_dict):
    PLbyStock = {}
    for key, value in stock_dict.items():
        PLbyStock[key] = getPLOverall(value)
    return PLbyStock

def getPLOverall (trades_dict):
    """
    Calculates the P&L of the data.

    Args:
        data_dict (dict): A dictionary with the new index variable as the key and a dictionary of data values

    Returns:
        float: The P&L of the data.
    """
    return sum(trades_dict.values()), len(trades_dict)

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
    
    values_list = list(data_dict.values())
    values_list.reverse()

    for value in values_list:
        date = extract_date(value['Filled Time'])
        if value['Side'] == 'Sell':
            cumulative += round(float(value['Avg Price']) * float(value['Total Qty']) * 100, 2)
        else:
            cumulative -= round(float(value['Avg Price']) * float(value['Total Qty']) * 100, 2)
        cumulativePL[date] = cumulative
    return cumulativePL

def getMoneyInvestedDaily (data_dict):
    """
    Calculates the money invested of the data for the day.

    Args:
        data_dict (dict): A dictionary with the new index variable as the key and a dictionary of data values

    Returns:
        dict: A dictionary with the date as the key and the money invested as the value.
    """
    dailyInvested = {}
    for key, value in data_dict.items():
        date = extract_date(value['Filled Time'])
        if value['Side'] == 'Buy':
            dailyInvested[date] = round(dailyInvested.get(date, 0) + float(value['Avg Price']) * float(value['Total Qty']) * 100, 2)
    return dailyInvested

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
    trades_dict = getTrades(data_dict)
    pnl_by_day = getPLDaily(data_dict)
    total_pnl, total_trades = getPLOverall(trades_dict)
    cumulative_pnl = getPLCumulative(data_dict)
    average_contract_size = getAverageContractSizeFromPastYear(data_dict)
    if average_contract_size != 0:
        average_contract_size_change_from_past_year = round(average_contract_size / getAverageContractSize(data_dict), 2)
    else:
        average_contract_size_change_from_past_year = 0
    average_winner_amount, average_winner_total_trades = getAverageWinner(trades_dict)
    average_loser_amount, average_loser_total_trades = getAverageLoser(trades_dict)
    money_invested_by_day = getMoneyInvestedDaily(data_dict)

    result = {
        "PnL_By_Day": pnl_by_day,
        "Total_PnL": total_pnl,
        "Total_Trades": total_trades,
        "Cumulative_PnL": cumulative_pnl,
        "Average_Contract_Size": average_contract_size,
        "Average_Contract_Size_Change": average_contract_size_change_from_past_year,
        "Average_Winner": average_winner_amount,
        "Average_Winner_Total_Trades": average_winner_total_trades,
        "Average_Loser": average_loser_amount,
        "Average_Loser_Total_Trades": average_loser_total_trades,
        "Money_Invested_By_Day": money_invested_by_day
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)