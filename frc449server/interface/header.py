from shutil import get_terminal_size
from textwrap import TextWrapper

from frc449server import dataconstants
from frc449server.interface import printing


def print_header(width=None):
    # Fill width of screen
    if not width:
        width = get_terminal_size(fallback=(100, 24))[0]

    printing.printf(
        ("{:^" + str(width) + "}").format("FRC Team 449: The Blair Robot Project"),
        style=printing.HEADER,
    )
    printing.printf("=" * width, style=printing.HEADER)
    printing.printf(
        ("{:^" + str(width) + "}").format("Bluetooth Scouting Server"),
        style=printing.TITLE,
    )
    printing.printf()
    printing.printf(
        ("{:^" + str(width) + "}").format("Runs with Python3 on Linux"),
        style=printing.INSTRUCTIONS,
    )
    printing.printf("-" * width + "\n", style=printing.INSTRUCTIONS)

    tw = TextWrapper(width=width)
    printing.printf(
        tw.fill("Commands:")
        + "\n"
        + tw.fill("q:\tquit")
        + "\n"
        + tw.fill(
            "d:\trequest drive update (should be automatic when you insert a drive)"
        )
        + "\n"
        + tw.fill("tba:\tupdate team list and match schedule from tba")
        + "\n"
        + tw.fill("st:\tsend team list to all connected devices")
        + "\n"
        + tw.fill("ss:\tsend match schedule to all connected devices")
        + "\n"
        + tw.fill("s m:\tget strat summary for match m")
        + "\n"
        + tw.fill("s t t ...: get strat summary for teams")
        + "\n"
        + tw.fill("m:\tcheck for missing and duplicate data")
        + "\n"
        + "\n"
        + "If there are any issues, try restarting the server first",
        style=printing.INSTRUCTIONS,
    )
    printing.printf("-" * width + "\n\n", style=printing.UNDERLINE)

    printing.printf("Before starting, make a folder where all the configuration files and data will go.\n"
                    f"In it should be a '{dataconstants.FIELD_NAMES_FILE}' with a comma-separated list of fields"
                    "that the app sends over\n"
                    f"There should also be a '{dataconstants.MAC_DICT_FILE}' mapping MAC addresses to client names",
                    style=printing.INSTRUCTIONS)
