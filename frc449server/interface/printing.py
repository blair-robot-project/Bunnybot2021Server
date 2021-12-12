from frc449server.interface.logger import log as log_

BASE = "\033[9"
BASE_END = "m"

ENDC = "\033[0m"

NORMAL = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
HIGHLIGHT = "\033[7m"


def _makecolor(i):
    return BASE + str(i) + BASE_END


DARKGRAY, RED, GREEN, YELLOW, BLUE, PURPLE, TEAL, LIGHTGRAY, DEFAULT = [
    _makecolor(i) for i in range(9)
]

CONNECTED = GREEN
DISCONNECTED = RED
STATUS = YELLOW
NEW_DATA = BLUE
EDIT = YELLOW
DATA_OUTPUT = PURPLE
FLASH_DRIVE = TEAL
WARNING = (YELLOW, BOLD)
ERROR = (RED, BOLD)
QUIT = (RED, HIGHLIGHT)
FLASH_DRIVE_SUCCESS = (GREEN, HIGHLIGHT)

LOGO = (RED, BOLD)
HEADER = RED
TITLE = (DEFAULT, BOLD)
INSTRUCTIONS = DEFAULT


# Prints with color and font styles
# Wrapper of print, so you can still use any kwargs that print understands
# Also has built in logging
def printf(
    *args, style=(DEFAULT, NORMAL), log=False, logtag="printing.printf", **kwargs
):
    # Handel the style being just a color/font style, or a tuple of both
    if type(style) == tuple:
        style = "".join(style)
    elif not type(style) == str:
        print(*args, **kwargs)
    # End the style so things printed after don't have it
    end = ENDC + kwargs.pop("end", "\n")
    # Start the style
    print(style, end="")
    # Print the stuff
    print(*args, **kwargs, end=end)

    if log:
        log_(logtag, kwargs.get("sep", " ").join(args))
