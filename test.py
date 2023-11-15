from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import requests
from matplotlib.dates import date2num


def get_tradingview_data(symbol, interval, limit):
    url = f'https://scanner.tradingview.com/crypto/scan'
    params = {
        'symbol': symbol,
        'interval': interval,
        'range': limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data['data'][0]['d']


def plot_tradingview_ethusdt_last_hour(symbol, interval):
    # Определение времени начала последнего часа
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)

    # Получение данных за последний час
    data = get_tradingview_data(symbol, interval,
                                {'from': int(start_time.timestamp() * 1000),
                                 'to': int(end_time.timestamp() * 1000)})

    times = [datetime.utcfromtimestamp(entry[0] / 1000) for entry in data]
    prices = [entry[1] for entry in data]

    fig, ax = plt.subplots()
    ax.plot_date(date2num(times), prices, '-')
    ax.xaxis_date()
    ax.set_xlabel('Time')
    ax.set_ylabel('ETH/USDT Price')
    ax.set_title('ETH/USDT Price Chart for the Last Hour')

    plt.show()


if __name__ == "__main__":
    symbol = 'BINANCE:ETHUSDT'
    interval = '1m'  # Интервал свечей (1 минута в данном случае)

    plot_tradingview_ethusdt_last_hour(symbol, interval)
