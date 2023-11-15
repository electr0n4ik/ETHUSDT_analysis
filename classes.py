import asyncio
import datetime
import json
import time
from datetime import datetime
import pandas as pd
import websockets
from sqlalchemy import (create_engine,
                        Column,
                        Integer,
                        String,
                        Numeric,
                        DateTime,
                        delete,
                        select)
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
            trade_entry = FuturesTrade(
                symbol=self.symbol,
                price=0,
                timestamp=datetime.utcnow()
            )
            self.session.add(trade_entry)
            self.session.commit()

    @staticmethod
    def create_session(engine):
        Session = sessionmaker(bind=engine)
        return Session()

    async def handle_trade(self, data):
        try:
            if data:
                data = json.loads(data)
                print(
                    f"Торговая пара ({self.symbol}): {data['s']}, Цена: {data['p']} {data['s']}")
                trade_symbol = data['s']
                trade_price = float(data['p'])

                engine = create_engine(
                    'postgresql://postgres:12345@localhost:5432/postgres')
                session = self.create_session(engine)

                # Вставка данных в таблицу
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

    async def delete_old_data(self):
        async with self.engine.begin() as conn:

            await conn.execute(
                delete(FuturesTrade)
                .where(FuturesTrade.timestamp < time.strftime(
                    '%Y-%m-%d %H:%M:%S',
                    time.gmtime(
                        time.time() - 3600)))
                .where(FuturesTrade.symbol == self.symbol)
            )

    async def price_change_alert(data, symbol, price_change_threshold=0.01,
                                 time_frame=60):
        try:
            data = json.loads(data)
            current_price = data["p"]
            timestamp = time.time()

            price_history.append((current_price, timestamp))

            while (price_history and timestamp -
                   price_history[0][1] > time_frame * 60):
                price_history.pop(0)

            # Рассчитываем изменение цены
            if len(price_history) >= 2:
                previous_price = price_history[0][0]
                percent_change = ((current_price - previous_price)
                                  / previous_price)

                if abs(percent_change) >= price_change_threshold:
                    if percent_change > 0:
                        movement = "Цена растет"
                    else:
                        movement = "Цена падает"

                    print(
                        f"Изменение цены на {abs(percent_change) * 100:.2f}% "
                        f"за последние {time_frame} минут. {movement}")

        except Exception as e:
            print(f"Произошла ошибка при обработке данных: {e}")

            await asyncio.sleep(10)  # Проверяем каждые 10 секунд

    async def create_dataframe(self):
        async with self.engine.begin() as conn:
            result = await conn.execute(
                select(FuturesTrade)
                .where(FuturesTrade.symbol == self.symbol)
            )

            rows = [dict(row) for row in result.fetchall()]

            df = pd.DataFrame(rows)

            return df

    async def run(self):
        async with websockets.connect(
                f"wss://stream.binance.com:9443/ws/{self.symbol}@trade") as ws:
            while True:
                response = await ws.recv()

                await self.handle_trade(response)
                # await self.delete_old_data()
                # await self.check_cointegration()
                # await self.price_change_alert(response,
                # self.symbol,
                # 'ethusdt')
