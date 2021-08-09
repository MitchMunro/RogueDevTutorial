#!/usr/bin/env python3
# up to here, Part
import copy

import tcod
import traceback
import color
from engine import Engine
from procgen import generate_dungeon
import entity_factories

WindowWidth, WindowHeight = 1800, 1200  # Window pixel resolution (when not maximized.)
WindowFlags = tcod.context.SDL_WINDOW_RESIZABLE


def main() -> None:
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 43

    room_max_size = 12
    room_min_size = 4
    max_rooms = 30

    max_monsters_per_room = 2
    max_items_per_room = 2

    # tileset = tcod.tileset.load_tilesheet(
    #     "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    # )

    tileset = tcod.tileset.load_tilesheet(
        "Gold-plated-16x16-v2.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )

    # Creates the Player and Engine
    player = copy.deepcopy(entity_factories.player)
    engine = Engine(player=player)

    engine.game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        max_monsters_per_room=max_monsters_per_room,
        max_items_per_room=max_items_per_room,
        engine=engine,
    )
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", color.welcome_text
    )

    root_console = tcod.Console(screen_width, screen_height, order="F")

    with tcod.context.new(
        width=WindowWidth,
        height=WindowHeight,
        columns=root_console.width,
        rows=root_console.height,
        tileset=tileset,
        sdl_window_flags=WindowFlags
    ) as context:
        while True:
            root_console.clear()
            engine.event_handler.on_render(console=root_console)
            context.present(root_console)

            try:
                for event in tcod.event.wait():
                    context.convert_event(event)
                    engine.event_handler.handle_events(event)
            except Exception:  # Handle exceptions in game.
                traceback.print_exc()  # Print error to stderr.
                # Then print the error to the message log.
                engine.message_log.add_message(traceback.format_exc(), color.error)


if __name__ == "__main__":
    main()
