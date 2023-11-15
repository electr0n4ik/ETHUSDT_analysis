import asyncio
import datetime
import json
import pandas as pd
from datetime import datetime

import websockets
from sqlalchemy import (create_engine,
                        Column,
                        Integer,
                        String,
                        Numeric,
                        DateTime)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

price_history = []

Base = declarative_base()


class FuturesTrade(Base):
    __tablename__ = 'futures_trades'

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    price = Column(Numeric)
    timestamp = Column(DateTime)


class FuturesProcessor:
    def __init__(self, symbol):
        self.symbol = symbol
        self.engine = create_engine(
            'postgresql://postgres:12345@localhost:5432/postgres'
        )

        self.session = self.create_session(self.engine)
        self.create_table(self.symbol)

    def create_table(self, table_name):
        if not self.engine.dialect.has_table(self.engine.connect(),
                                             table_name):
            Base.metadata.create_all(self.engine)

    @staticmethod
    def create_session(engine):
        Session = sessionmaker(bind=engine)
        return Session()

    async def handle_trade(self, data):
        try:
            if data:
                data = json.loads(data)
                print(
                    f"Торговая пара ({self.symbol}): "
                    f"{data['s']}, Цена: {data['p']} {data['s']}")
                trade_symbol = data['s']

                trade_price = float(data['p'])

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

    async def read_data_to_dataframe(self, symbol):
        trades = self.session.query(FuturesTrade).filter_by(
            symbol=symbol).all()
        data = {'ID': [], 'Symbol': [], 'Price': [], 'Timestamp': []}

        for trade in trades:
            data['ID'].append(trade.id)
            data['Symbol'].append(trade.symbol)
            data['Price'].append(trade.price)
            data['Timestamp'].append(trade.timestamp)

        df = pd.DataFrame(data)
        return df

    async def run(self):

        async with websockets.connect(
                f"wss://stream.binance.com:9443/ws/{self.symbol}@trade") as ws:
            while True:
                response = await ws.recv()

                await self.handle_trade(response)
                # await self.read_data_to_dataframe(self.symbol.upper())
