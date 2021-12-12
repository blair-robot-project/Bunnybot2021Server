import json
import os

from interface import printing

_LOCAL_CONSTANTS_FILE = "local_constants.json"
FIELD_NAMES_FILE = "fields.txt"
MAC_DICT_FILE = "mac.json"

JSON_FILE = "data.json"
CSV_FILE = "data.csv"
TBA_SAVE_FILE = "tba.json"

MESSAGE_SIZE = 1024


class DataConstants:
    def __init__(self, data_dir):
        self.abs_data_dir = os.path.abspath(data_dir)
        try:
            local_constants = json.load(open(_LOCAL_CONSTANTS_FILE))
        except FileNotFoundError:
            print("Please enter the following file names and directory locations:")
            local_constants = {"TEAM": input("Team number (e.g. 449) "),
                               "EVENT": input("TBA event id (e.g. '2020mdbet') "),
                               "DRIVE": input("Flash drive location (e.g. 'D:') (default none) ")}
            with open(_LOCAL_CONSTANTS_FILE, "w") as f:
                json.dump(local_constants, f)

        self.team = local_constants["TEAM"]
        self.event = local_constants["EVENT"]
        # The location of the removable device to copy data to
        self.drive = local_constants["DRIVE"]

        # Load the field names from fields.txt
        field_names_file = os.path.join(self.abs_data_dir, FIELD_NAMES_FILE)
        if not os.path.exists(field_names_file):
            printing.printf(f"{field_names_file} does not exist",
                            style=printing.ERROR,
                            log=True,
                            logtag="dataconstants.load_fields")
        with open(field_names_file) as field_names:
            line = next(field_names)
            column_names = [name.strip() for name in line.split(",")]
            # `fields` maps snake_case field names to camelCase field names (e.g. "TEAM_ID": "teamId")
            name_dict = {name: _camel_case(name) for name in column_names}
            self.field_names = type("Enum", (), name_dict)()
            self.order = GeneralFields.ORDER + list(name_dict.values())

        # Get MAC address of clients
        mac_file_path = os.path.join(self.abs_data_dir, MAC_DICT_FILE)
        if not os.path.exists(mac_file_path):
            printing.printf(f"{mac_file_path} does not exist",
                            style=printing.ERROR,
                            log=True,
                            logtag="dataconstants.load_mac_dict")
        with open(mac_file_path) as mac_file:
            self.mac_dict = json.load(mac_file)


class GeneralFields:
    """These fields will always be included in the app's messages regardless of the specific game"""
    TEAM_ID = "teamId"
    MATCH_ID = "matchId"
    ALLIANCE_COLOR = 'alliance'
    NO_SHOW = 'noShow'
    COMMENTS = 'comments'
    REVISION = 'revision'
    TIMESTAMP = 'timestamp'
    MATCH = 'match'
    TEAM = 'team'
    RECORDER_NAME = "recorderName"

    ORDER = [TEAM_ID, MATCH_ID, ALLIANCE_COLOR, NO_SHOW, COMMENTS, REVISION, TIMESTAMP, MATCH, TEAM, RECORDER_NAME]


def _camel_case(snake):
    return snake[0].lower() + ("_" + snake[1:].replace("_", "")).title()[1:]


Fields, ORDER = 0, 0

MAC_DICT = {
    "00:FC:8B:3B:42:46": "R1 Demeter",
    "00:FC:8B:39:C1:09": "R2 Hestia",
    "78:E1:03:A3:18:78": "R3 Hera",
    "78:E1:03:A1:E2:F2": "B1 Hades",
    "78:E1:03:A4:F7:70": "B2 Poseidon",
    "00:FC:8B:3F:E4:EF": "B3 Zeus",
    "00:FC:8B:3F:28:28": "Backup 1",
}
