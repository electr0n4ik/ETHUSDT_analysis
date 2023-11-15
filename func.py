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


async def adjust_ethusdt_price(data_frame):
    """
    Adjusts the ethusdt price by excluding the influence of btcusdt.

    Parameters:
    - data_frame: DataFrame with 'Price_eth' and 'Price_btc' columns.

    Returns:
    - Adjusted ethusdt price.
    """
    # Находим коэффициент регрессии
    regression_coefficient = await find_regression_coefficient(data_frame,
                                                               'Price_btc',
                                                               'Price_eth')

    # Создаем копию данных для избежания изменения оригинального датафрейма
    adjusted_data = data_frame.copy()

    # Привести значения в столбцах к float
    adjusted_data['Price_eth'] = adjusted_data['Price_eth'].astype(float)
    adjusted_data['Price_btc'] = adjusted_data['Price_btc'].astype(float)

    # Применяем коэффициент регрессии
    adjusted_data['ethusdt_adjusted'] = adjusted_data['Price_eth'] - (
            adjusted_data['Price_btc'] * regression_coefficient)

    # Возвращаем скорректированную цену ethusdt
    return adjusted_data['ethusdt_adjusted']


async def ethusdt_regression(eth_df, btc_df):
    # TODO дошел до этой функции
    # TODO хочу ее сделать основной для вывода независимой цены ethusdt

    eth_df['Timestamp'] = eth_df['Timestamp'].dt.round('S')
    btc_df['Timestamp'] = btc_df['Timestamp'].dt.round('S')

    # Объединяем данные из двух DataFrame
    merged_df = pd.merge(eth_df, btc_df, on='Timestamp',
                         suffixes=('_eth', '_btc'))

    # Вызываем функцию для получения скорректированной цены ethusdt
    adjusted_price = await adjust_ethusdt_price(merged_df)

    print(adjusted_price)


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
