from __future__ import annotations

import copy
from typing import Iterable, Iterator, Optional, TYPE_CHECKING
import numpy as np  # type: ignore
from tcod.console import Console
from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
    from entity import Entity
    from engine import Engine


class GameMap:
    def __init__(
        self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        self.tile_layout = np.full((width, height), fill_value=1, order="F")   # 2D array of numbers representing floor layout. 0=floor, 1=wall
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")
        self.visible = np.full((width, height), fill_value=False, order="F")  # Tiles the player can currently see
        self.explored = np.full((width, height), fill_value=False, order="F")  # Tiles the player has seen before
        self.explorable = np.full((width, height), fill_value=False, order="F")  # Tiles the player could currently explore and view
        self.entities = set(entities)
        self.downstairs_location = (0, 0)

    @property
    def gamemap(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(self, location_x: int, location_y: int,) -> Optional[Entity]:
        for entity in self.entities:
            if (
                    entity.blocks_movement
                    and entity.x == location_x
                    and entity.y == location_y
            ):
                return entity

        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Renders the map.
        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" color
        Otherwise, the default is "SHROUD".

        If element 1 in condlist is true, do the thing in choicelist 1.
        Else if element 2 in condlist is true, do the thing in choicelist 2.
        """

        self.draw_tile_graphics(self.tile_layout, self.engine)

        game_array = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        # self.draw_tile_graphics(self.tile_layout, self.engine)

        console.tiles_rgb[0: self.width, 0: self.height] = game_array

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )
        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            if self.visible[entity.x, entity.y]:
                console.print(
                    x=entity.x, y=entity.y, string=entity.char, fg=entity.color
                )

    def draw_tile_graphics(self, layout: np.ndarray, engine: Engine):
        for (x, y), t in np.ndenumerate(layout):
            if t == 0:
                self.tiles[x, y] = tile_types.floor
            elif t == 1:
                mask = 0
                '''
                KEEP IN MIND: layout array starts at (0,0) in the top left corner.
                - As you go DOWN the y value increases.
                - As you go LEFT the X value increases.
                '''
                if self.is_wall_and_visible(x, y - 1):  # Above
                    mask += 1
                if self.is_wall_and_visible(x, y + 1):  # Below
                    mask += 2
                if self.is_wall_and_visible(x - 1, y):  # Left
                    mask += 4
                if self.is_wall_and_visible(x + 1, y):  # Right
                    mask += 8

                if mask == 0:
                    self.tiles[x, y] = tile_types.new_wall("○")  # Pillar because we can't see neighbors
                elif mask == 1:
                    self.tiles[x, y] = tile_types.new_wall("║")  # Wall only to the north
                elif mask == 2:
                    self.tiles[x, y] = tile_types.new_wall("║")  # Wall only to the south
                elif mask == 3:
                    self.tiles[x, y] = tile_types.new_wall("║")  # Wall to the north and south
                elif mask == 4:
                    self.tiles[x, y] = tile_types.new_wall("═")  # Wall only to the west
                elif mask == 5:
                    self.tiles[x, y] = tile_types.new_wall("╝")  # Wall to the north and west
                elif mask == 6:
                    self.tiles[x, y] = tile_types.new_wall("╗")  # Wall to the south and west
                elif mask == 7:
                    if self.is_wall_and_visible(x-1, y+1) or self.is_wall_and_visible(x-1, y-1):
                        self.tiles[x, y] = tile_types.new_wall("║")
                    elif self.is_wall_and_visible(x-1, y+1):
                        self.tiles[x, y] = tile_types.new_wall("╝")
                    elif self.is_wall_and_visible(x-1, y-1):
                        self.tiles[x, y] = tile_types.new_wall("╗")
                    else:
                        self.tiles[x, y] = tile_types.new_wall("╣")  # Wall to the north, south and west
                elif mask == 8:
                    self.tiles[x, y] = tile_types.new_wall("═")  # Wall only to the east
                elif mask == 9:
                    self.tiles[x, y] = tile_types.new_wall("╚")  # Wall to the north and east
                elif mask == 10:
                    self.tiles[x, y] = tile_types.new_wall("╔")  # Wall to the south and east
                elif mask == 11:
                    if self.is_wall_and_visible(x+1, y+1) or self.is_wall_and_visible(x+1, y-1):
                        self.tiles[x, y] = tile_types.new_wall("║")
                    elif self.is_wall_and_visible(x+1, y+1):
                        self.tiles[x, y] = tile_types.new_wall("╚")
                    elif self.is_wall_and_visible(x+1, y-1):
                        self.tiles[x, y] = tile_types.new_wall("╔")
                    else:
                        self.tiles[x, y] = tile_types.new_wall("╠")  # Wall to the north, south and east
                elif mask == 12:
                    self.tiles[x, y] = tile_types.new_wall("═")  # Wall to the east and west
                elif mask == 13:
                    if self.is_wall_and_visible(x-1, y-1) and self.is_wall_and_visible(x+1, y-1):
                        self.tiles[x, y] = tile_types.new_wall("═")
                    elif self.is_wall_and_visible(x-1, y-1):
                        self.tiles[x, y] = tile_types.new_wall("╚")
                    elif self.is_wall_and_visible(x+1, y-1):
                        self.tiles[x, y] = tile_types.new_wall("╝")
                    else:
                        self.tiles[x, y] = tile_types.new_wall("╩")  # Wall to the east, west, and south
                elif mask == 14:
                    if self.is_wall_and_visible(x-1, y+1) or self.is_wall_and_visible(x+1, y+1):
                        self.tiles[x, y] = tile_types.new_wall("═")
                    elif self.is_wall_and_visible(x-1, y+1):
                        self.tiles[x, y] = tile_types.new_wall("╔")
                    elif self.is_wall_and_visible(x+1, y+1):
                        self.tiles[x, y] = tile_types.new_wall("╗")
                    else:
                        self.tiles[x, y] = tile_types.new_wall("╦")  # Wall to the east, west, and north
                elif mask == 15:
                    self.tiles[x, y] = tile_types.new_wall("╬")  # ╬ Wall on all sides
                else:
                    self.tiles[x, y] = tile_types.new_wall()

    # TODO
    '''
    TODO write a new fuction that checks the whole map and what is visible and then draws it
    Then only need to update it when something changes self.tile_layout
    Call it something like is_visible_to_player
    '''

    def is_wall_and_visible(self, x: int, y: int) -> bool:
        if x < 0 or y < 0 or x > self.width - 1 or y > self.height - 1:
            return False
        if self.tile_layout[x, y] == 1 and self.explorable[x, y]:
            return True
        else:
            return False

    # def check_diagonal(self, x:int, y:int) -> bool:
    #     if self.tile_layout[x, y] == 1:





class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.
    """

    def __init__(
        self,
        *,
        engine: Engine,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        current_floor: int = 0
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.current_floor = current_floor

    def generate_floor(self) -> None:
        from procgen import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            engine=self.engine,
        )
