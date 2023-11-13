import asyncio
from classes import FuturesProcessor, FuturesTrade
from sqlalchemy import create_engine

async def main():
    engine = create_engine('postgresql://postgres:12345@localhost:5432/postgres')

    eth_processor = FuturesProcessor('ethusdt')
    btc_processor = FuturesProcessor('btcusdt')

    eth_task = asyncio.create_task(eth_processor.run(FuturesTrade, engine))
    btc_task = asyncio.create_task(btc_processor.run(FuturesTrade, engine))

    await asyncio.gather(eth_task, btc_task)

if __name__ == '__main__':
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)

    event_loop.run_until_complete(main())
