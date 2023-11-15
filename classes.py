import asyncio
import datetime
import json
from datetime import datetime

import pandas as pd
import websockets
from sqlalchemy import (create_engine,
                        Column,
                        Integer,
                        String,
                        Numeric,
                        DateTime)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from func import check_eth_price, ethusdt_regression

price_history = []

Base = declarative_base()


class FuturesTrade(Base):
    """
    Модель для таблицы futures_trades в базе данных.
    Содержит информацию о сделках по фьючерсам, такую как символ, цена и временная метка.
    """
    __tablename__ = 'futures_trades'

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    price = Column(Numeric)
    timestamp = Column(DateTime)


class FuturesProcessor:
    """
    Класс для обработки данных о торговле фьючерсами.
    Подключается к Binance WebSocket, обрабатывает сделки и сохраняет их в базу данных.
    Также вызывает функцию для проверки изменения цены ETH.
    """

    def __init__(self, symbol):
        """
        Инициализация объекта FuturesProcessor.

        Parameters:
            symbol (str): Символ для отслеживания торгов.
        """
        self.symbol = symbol
        self.engine = create_engine(
            'postgresql://postgres:12345@localhost:5432/postgres'
        )

        self.session = self.create_session(self.engine)
        self.create_table(self.symbol)

    def create_table(self, table_name):
        """
        Создает таблицу в базе данных, если она не существует.

        Parameters:
            table_name (str): Имя таблицы.
        """
        if not self.engine.dialect.has_table(self.engine.connect(),
                                             table_name):
            Base.metadata.create_all(self.engine)

    @staticmethod
    def create_session(engine):
        """
        Создает сеанс для взаимодействия с базой данных.

        Parameters:
            engine: Объект мотора SQLAlchemy.

        Returns:
            sqlalchemy.orm.Session: Объект сеанса.
        """
        Session = sessionmaker(bind=engine)
        return Session()

    async def handle_trade(self, data):
        """
        Обрабатывает данные о сделке, сохраняет их в базу данных
        и вызывает функцию для проверки изменения цены ETH.

        Parameters:
            data (str): JSON-строка данных о сделке.
        """
        try:
            if data:
                data = json.loads(data)
                if self.symbol == "ethusdt":
                    print(
                        f"Торговая пара ({self.symbol}): "
                        f"{data['s']}, Цена: {data['p']} {data['s']}")
                trade_symbol = data['s']

                trade_price = float(data['p'])

                await check_eth_price(trade_price)

                engine = create_engine(
                    'postgresql://postgres:12345@localhost:5432/postgres')
                session = self.create_session(engine)

                trade_entry = FuturesTrade(
                    symbol=trade_symbol,
                    price=trade_price,
                    timestamp=datetime.now()
                )
                session.add(trade_entry)
                session.commit()
                session.close()

                await asyncio.sleep(1)
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            await asyncio.sleep(10)

    async def read_data_to_dataframe(self):
        """
        Читает данные из базы данных и возвращает их в виде DataFrame.

        Returns:
            pd.DataFrame: DataFrame с данными о сделках.
        """
        trades = self.session.query(FuturesTrade).filter_by(
            symbol=self.symbol.upper()).all()
        data = {'ID': [], 'Symbol': [], 'Price': [], 'Timestamp': []}

        for trade in trades:
            data['ID'].append(trade.id)
            data['Symbol'].append(trade.symbol)
            data['Price'].append(trade.price)
            data['Timestamp'].append(trade.timestamp)

        df = pd.DataFrame(data)
        return df

    async def run(self):
        """
        Запускает подключение к WebSocket и цикл обработки сделок.
        """
        async with websockets.connect(
                f"wss://stream.binance.com:9443/ws/{self.symbol}@trade",
                ping_timeout=20,
                # Таймаут ожидания ответа на пинг (в секундах)
                close_timeout=60,
                # Таймаут на закрытие соединения (в секундах),
                # None - неограниченный
                max_queue=2 ** 5,  # Максимальный размер очереди сообщений
        ) as ws:
            while True:
                response = await ws.recv()

                await self.handle_trade(response)

                # await self.read_data_to_dataframe()
