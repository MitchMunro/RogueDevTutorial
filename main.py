#!/usr/bin/env python3
# up to here, Part
import tcod
import traceback
import color
import exceptions
import input_handlers
import setup_game

WindowWidth, WindowHeight = 1800, 1200  # Window pixel resolution (when not maximized.)
WindowFlags = tcod.context.SDL_WINDOW_RESIZABLE


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active Engine then save it."""
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved.")


def main() -> None:
    screen_width = 80
    screen_height = 50

    # tileset = tcod.tileset.load_tilesheet(
    #     "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    # )

    tileset = tcod.tileset.load_tilesheet(
        "Gold-plated-16x16-v2.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )

    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

    root_console = tcod.Console(screen_width, screen_height, order="F")

    with tcod.context.new(
        width=WindowWidth,
        height=WindowHeight,
        columns=root_console.width,
        rows=root_console.height,
        tileset=tileset,
        sdl_window_flags=WindowFlags
    ) as context:
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit.
            save_game(handler, "savegame.sav")
            raise
        except BaseException:  # Save on any other unexpected exception.
            save_game(handler, "savegame.sav")
            raise
        # while True:
        #     root_console.clear()
        #     engine.event_handler.on_render(console=root_console)
        #     context.present(root_console)
        #
        #     try:
        #         for event in tcod.event.wait():
        #             context.convert_event(event)
        #             engine.event_handler.handle_events(event)
        #     except Exception:  # Handle exceptions in game.
        #         traceback.print_exc()  # Print error to stderr.
        #         # Then print the error to the message log.
        #         engine.message_log.add_message(traceback.format_exc(), color.error)


if __name__ == "__main__":
    main()
