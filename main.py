import asyncio

import pygame  # Ensures Pygbag bundles the real pygame package for web builds.

from td_game.app import run_async, write_current_crash_log


async def main():
    try:
        await run_async([], exit_on_quit=False)
    except Exception as exc:
        write_current_crash_log(exc)
        raise


asyncio.run(main())
