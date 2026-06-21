import asyncio

from td_game.app import run_async


async def main():
    await run_async([], exit_on_quit=False)


asyncio.run(main())
