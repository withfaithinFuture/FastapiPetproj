import uvicorn
import asyncio
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)-20s - %(levelname)-8s - %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler(), logging.FileHandler('app.log', encoding='utf-8')]
)


async def main() -> None:
    uvicorn.run('src.app.application:get_app', host='0.0.0.0', port=8000, reload=True, factory=True)

if __name__ == '__main__':
    asyncio.run(main())