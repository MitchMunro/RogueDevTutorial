from typing import Tuple
from engine import Engine
import numpy as np  # type: ignore
from enum import Enum

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", np.bool),  # True if this tile can be walked over.
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("light", graphic_dt)  # Graphics for when the tile is in FOV.
    ]
)


def new_tile(
        *,  # Enforce the use of keywords, so that parameter order doesn't matter.
        walkable: int,
        transparent: int,
        dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
        light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types """
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)


# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (5, 0, 20)), dtype=graphic_dt)

floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("`"), (35, 0, 69), (5, 0, 20)),
    light=(ord("`"), (54, 44, 69), (15, 10, 30)),
)
down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (0, 0, 100), (50, 50, 150)),
    light=(ord(">"), (255, 255, 255), (200, 180, 50)),
)

wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("#"), (79, 74, 127), (5, 0, 20)),
    light=(ord("#"), (142, 134, 223), (15, 10, 30)),
)

test_tile = new_tile(
    walkable=True,
    transparent=False,
    dark=(ord("*"), (255, 255, 0), (0, 0, 0)),
    light=(ord("*"), (255, 255, 0), (0, 0, 0)),
)


def new_wall(char: str = None) -> tile_dt:
    if char is None:
        return wall
    else:
        w = new_tile(
            walkable=False,
            transparent=False,
            dark=(ord(char), (79, 74, 127), (5, 0, 20)),
            light=(ord(char), (142, 134, 223), (15, 10, 30)),
        )
        return w
