import asyncio
from sqlalchemy import create_engine
from classes import FuturesProcessor
from func import create_postgresql_connection, read_and_print_data, \
    close_database_connection


async def main():
    engine = create_engine(
        'postgresql://postgres:12345@localhost:5432/postgres')

    eth_processor = FuturesProcessor('ethusdt')
    btc_processor = FuturesProcessor('btcusdt')

    eth_task = asyncio.create_task(eth_processor.run())
    btc_task = asyncio.create_task(btc_processor.run())

    await asyncio.gather(eth_task, btc_task)


if __name__ == '__main__':
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)

    event_loop.run_until_complete(main())

    # database_url = (
    #     'postgresql://postgres:12345@localhost:5432/postgres')
    # engine, session = create_postgresql_connection(database_url)
    #
    # if session:
    #     read_and_print_data(session)
    #
    # close_database_connection(engine)
