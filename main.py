import asyncio

import pygame  # Ensures Pygbag bundles the real pygame package for web builds.

from td_game.app import run_async


async def main():
    await run_async([], exit_on_quit=False)


asyncio.run(main())
