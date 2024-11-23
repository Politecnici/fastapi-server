import logging
import asyncio
logger = logging.getLogger('uvicorn.error')

async def main_loop():
    while True:
        logger.info("kek")
        await asyncio.sleep(1)  # Non-blocking sleep for 1 second