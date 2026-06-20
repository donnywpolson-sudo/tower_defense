"""Rendering boundary for future extraction.

Drawing currently remains in td_game.app so the cleanup does not change draw
order or gameplay behavior. Terrain, tower, enemy, and UI rendering can move
here incrementally after the state object owns the runtime lists.
"""
