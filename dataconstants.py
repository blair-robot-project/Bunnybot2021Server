import json

LOCAL_CONSTANTS_FILE = "local_constants.json"
try:
    local_constants = json.load(open(LOCAL_CONSTANTS_FILE))
except FileNotFoundError:
    print("Please enter the following file names and directory locations:")
    local_constants = {
        "DATA_FILE_NAME": input("Data file base name (e.g. 'data') "),
        "ABS_DATA_DIR": input("Absolute data directory (e.g. '/home/user/Desktop') "),
        "TEAM": input("Team number (e.g. 449) "),
        "EVENT": input("TBA event id (e.g. '2020mdbet') "),
    }
    drive = input("Flash drive location (e.g. 'D:') (default none) ")
    local_constants["DRIVE"] = drive
    with open(LOCAL_CONSTANTS_FILE, "w") as f:
        json.dump(local_constants, f)

JSON_FILE = local_constants["DATA_FILE_NAME"] + ".json"
CSV_FILE = local_constants["DATA_FILE_NAME"] + ".csv"
ABS_DATA_DIR = local_constants["ABS_DATA_DIR"]
TEAM = local_constants["TEAM"]
EVENT = local_constants["EVENT"]
# The location of the removable device to copy data to
DRIVE = local_constants["DRIVE"]

TBA_SAVE_FILE = "tba.json"

MESSAGE_SIZE = 1024

LOG_FILE = "log"

column_names = [
    "TEAM_ID",
    "MATCH_ID",
    "ALLIANCE_COLOR",
    "NO_SHOW",
    "PRELOAD",
    "AUTO_MOVE",
    "HIT_PARTNER",
    "AUTO_INTAKE",
    "AUTO_CENTER",
    "AUTO_HIGH",
    "AUTO_LOW",
    "AUTO_MISS",
    "HIGH",
    "CENTER",
    "LOW",
    "MISS",
    "SPINNER_ROT",
    "SPINNER_POS",
    "ATTEMPTED_CLIMB",
    "PARK",
    "SOLO_CLIMB",
    "DOUBLE_CLIMB",
    "WAS_LIFTED",
    "CLIMB_TIME",
    "ENDGAME_SCORE",
    "LEVEL",
    "DEAD",
    "DEFENSE",
    "COMMENTS",
    "SCOUT_NAME",
    "REVISION",
    "TIMESTAMP",
    "MATCH",
    "TEAM",
    "SOLO_CLIMB_NYF",
    "DOUBLE_CLIMB_NYF",
    "WAS_LIFTED_NYF",
]


# TODO: do this in a less dumb way
def _create_fields_enum():
    """
    Returns a tuple containing an enum with column names and a list with the string values of the fields of that enum
    """

    def to_camel_case(snake):
        return "".join(part.title() for part in snake.split("_"))

    name_dict = {name: to_camel_case(name) for name in column_names}
    fields_enum = type("Enum", (), name_dict)
    order = [name_dict[snake] for snake in column_names]
    return fields_enum(), order


Fields, ORDER = _create_fields_enum()

MAC_DICT = {
    "00:FC:8B:3B:42:46": "R1 Demeter",
    "00:FC:8B:39:C1:09": "R2 Hestia",
    "78:E1:03:A3:18:78": "R3 Hera",
    "78:E1:03:A1:E2:F2": "B1 Hades",
    "78:E1:03:A4:F7:70": "B2 Poseidon",
    "00:FC:8B:3F:E4:EF": "B3 Zeus",
    "00:FC:8B:3F:28:28": "Backup 1",
}
