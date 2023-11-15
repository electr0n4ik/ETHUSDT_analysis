import numpy as np
import pandas as pd


# from classes import FuturesTrade


async def check_eth_price(current_price):
    try:
        if check_eth_price.last_price > 0:
            # Проверяем изменение цены на 1%
            percent_change = ((current_price - check_eth_price.last_price) /
                              check_eth_price.last_price * 100)
            check_eth_price.last_price = current_price

            if abs(percent_change) >= 1:
                sign = '+' if percent_change > 0 else '-'
                print(
                    f"Price change: {sign}1% - "
                    f"Current Price: {current_price} USDT")

    except Exception as e:
        print(f"Error: {e}")


# Инициализируем статическую переменную для хранения предыдущей цены
check_eth_price.last_price = 0


async def find_regression_coefficient(df, btc, eth):
    """
    Находит коэффициент регрессии методом наименьших квадратов.


    Parameters:
    - df: DataFrame с данными
    - btc: Название столбца, представляющего независимую переменную (X)
    - eth: Название столбца, представляющего зависимую переменную (Y)

    Returns:
    - Коэффициент регрессии
    """
    independent_variable = df[btc].astype(float).values
    dependent_variable = df[eth].astype(float).values

    A = np.vstack([independent_variable, np.ones(len(independent_variable))]).T
    m, c = np.linalg.lstsq(A, dependent_variable, rcond=None)[0]

    return m


async def plot_ethusdt_regression(eth_df, btc_df):
    eth_df['Timestamp'] = eth_df['Timestamp'].dt.round('S')
    btc_df['Timestamp'] = btc_df['Timestamp'].dt.round('S')

    # eth_timestamps = set(eth_df['Timestamp'])
    # btc_timestamps = set(btc_df['Timestamp'])
    #
    # print("Timestamps unique to ETH:", eth_timestamps - btc_timestamps)
    # print("Timestamps unique to BTC:", btc_timestamps - eth_timestamps)

    # Объединяем данные из двух DataFrame
    merged_df = pd.merge(eth_df, btc_df, on='Timestamp',
                         suffixes=('_eth', '_btc'))

    # Находим коэффициент регрессии
    regression_coefficient = await find_regression_coefficient(merged_df,
                                                               'Price_btc',
                                                               'Price_eth')

    # Выбираем только нужные столбцы
    selected_data = merged_df[['Timestamp', 'Price_eth', 'Price_btc']].copy()

    selected_data.loc[:, 'Price_eth'] = pd.to_numeric(
        selected_data['Price_eth'])
    selected_data.loc[:, 'Price_btc'] = pd.to_numeric(
        selected_data['Price_btc'])
    selected_data['ethusdt_adjusted'] = pd.to_numeric(
        selected_data['Price_eth']) - (pd.to_numeric(
        selected_data['Price_btc']) * regression_coefficient)

    # Используем numpy для подготовки данных
    X = selected_data['Price_btc'].astype(float).values.reshape(-1, 1)
    y = selected_data['ethusdt_adjusted'].astype(float).values

    # Выполняем линейную регрессию
    A = np.vstack([X.flatten(), np.ones(len(X))]).T
    m, c = np.linalg.lstsq(A, y, rcond=None)[0]

    # # Предсказание значений
    # predicted_ethusdt = m * X.flatten() + c
    #
    # # Построим график
    # plt.figure(figsize=(10, 6))
    # plt.scatter(selected_data['Price_btc'], selected_data['ethusdt_adjusted'],
    #             label='ETHUSDT Adjusted')
    # plt.plot(X.flatten(), predicted_ethusdt, color='red', linewidth=2,
    #          label='Regression Line')
    # plt.xlabel('BTCUSDT Price')
    # plt.ylabel('ETHUSDT Adjusted Price')
    # plt.legend()
    # plt.title('ETHUSDT Regression Adjusted')
    #
    # # Save the plot to a file
    # plt.savefig('ethusdt_regression_plot.png')

# if __name__ == "__main__":
#
#     plot_ethusdt_regression(eth_df, btc_df)


# # Функция для создания подключения к базе данных PostgreSQL
# def create_postgresql_connection(database_url):
#     engine = create_engine(database_url)
#     Session = sessionmaker(bind=engine)
#     return engine, Session()
#
#
# # Функция для считывания и вывода данных из таблицы
# def read_and_print_data(session):
#     trades = session.query(FuturesTrade).all()
#     for trade in trades:
#         print(
#             f"ID: {trade.id}, "
#             f"Symbol: {trade.symbol}, "
#             f"Price: {trade.price}, "
#             f"Timestamp: {trade.timestamp}")
#
#
# # Функция для закрытия подключения к базе данных
# def close_database_connection(engine):
#     if engine:
#         engine.dispose()
#         print("Connection closed.")
