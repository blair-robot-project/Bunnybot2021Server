import json
import os
import shutil
from queue import Queue

import dataconstants
import interface.printing as printing
from controllers import systemctl
from dataconstants import Fields, ABS_DATA_DIR, JSON_FILE, CSV_FILE, ORDER


class DataController:
    data_queue = Queue()
    data = dict()
    data_changed = True

    def __init__(self):
        self.data = load_json_file()
        self.drive = dataconstants.DRIVE

    def queue_data(self, data, source):
        self.data_queue.put((data, source))

    def update(self):
        # While there is data to add, parse it
        data = False
        while not self.data_queue.empty():
            data = True
            self.parse_data(*self.data_queue.get())

        if data:
            write_json(self.data)
            self.to_csv()
            self.data_changed = True

        # If there is a flash drive and there is new data for it, upload the data
        if self.data_changed:
            if self.drive:
                systemctl.copy(
                    os.path.join(ABS_DATA_DIR, CSV_FILE),
                    os.path.join(self.drive, os.path.sep + CSV_FILE),
                )
                self.data_changed = False
            elif systemctl.checkdev():
                self._update_drive()
                self.data_changed = False

    def _update_drive(self):
        """Writes data to a removable device (Linux-specific!)"""
        mount_point = systemctl.mount()
        if mount_point:
            systemctl.copy(os.path.join(ABS_DATA_DIR, CSV_FILE), os.path.join(mount_point, CSV_FILE))
            systemctl.unmount()

    def parse_data(self, data, source):
        if source not in self.data:
            self.data[source] = dict()
        if str(data[Fields.TIMESTAMP]) not in self.data[source]:
            self.data[source][str(data[Fields.TIMESTAMP])] = dict()
        self.data[source][str(data[Fields.TIMESTAMP])][
            str(data[Fields.REVISION])
        ] = data

    def to_csv(self):
        s = ",".join(ORDER) + "\n"
        for v in self.data.values():
            for id in v.values():
                m = id[str(max(map(int, id.keys())))]
                s += (
                    ",".join(
                        [
                            csv_safe(m, f)
                            if f in m
                            else missing_field(
                                f, m[Fields.TIMESTAMP], m[Fields.REVISION]
                            )
                            for f in ORDER
                        ]
                    )
                    + "\n"
                )
        write_file(CSV_FILE, s, mode="w")

    def sync_summary(self, client):
        return {
            i: max(map(int, revs.keys()))
            for i, revs in self.data.get(client, dict()).items()
        }

    def drive_update_request(self):
        self.data_changed = True

    def find_missing(self, schedule=None):
        teams_by_match = dict()
        for device in self.data.values():
            for m in device.values():
                match = m[max(m.keys(), key=int)]
                if match[Fields.MATCH] not in teams_by_match:
                    teams_by_match[match[Fields.MATCH]] = []
                teams_by_match[match[Fields.MATCH]].append(match[Fields.TEAM])

        max_match = max(teams_by_match.keys(), key=int)
        for i in range(1, int(max_match)):
            if str(i) not in teams_by_match:
                teams_by_match[str(i)] = []

        for match, teams in sorted(teams_by_match.items(), key=lambda x: int(x[0])):
            if int(match) <= int(max_match):
                if schedule:
                    expected = schedule[match]["red"] + schedule[match]["blue"]
                    missing = []
                    extra = []
                    for e in expected:
                        if e not in teams:
                            missing.append(e)
                    for t in teams:
                        if t not in expected:
                            extra.append(t)
                    if missing:
                        printing.printf(
                            f'{match:2}: missing data for team{"s" if len(missing) > 1 else ""} {", ".join(missing)}',
                            style=printing.YELLOW,
                        )
                    if extra:
                        printing.printf(
                            f'{match:2}: data for team{"s" if len(extra) > 1 else ""} not in match: {", ".join(extra)}',
                            style=printing.YELLOW,
                        )
                else:
                    if len(set(teams)) < 6:
                        printing.printf(
                            f'{match:2}: missing data, only have team{"s" if len(set(teams)) > 1 else ""} {", ".join(teams)}',
                            style=printing.YELLOW,
                        )
                    elif len(set(teams)) > 6:
                        printing.printf(
                            f'{match:2}: extra data, have teams {", ".join(teams)}',
                            style=printing.YELLOW,
                        )

                if len(set(teams)) != len(teams):
                    printing.printf(
                        f'{match:2}: duplicate data, have entries for: {", ".join(teams)}',
                        style=printing.YELLOW,
                    )
        printing.printf(f"Data found through match {max_match}", style=printing.TEAL)


def missing_field(f, t, r):
    printing.printf(
        f"Missing field {f} from data entry {t}.{r}",
        style=printing.ERROR,
        log=True,
        logtag="datactl.error",
    )
    return "ERROR"


def read_file(file):
    with open(ABS_DATA_DIR + file) as f:
        return f.read()


def write_file(file, s, mode="a"):
    with open(os.path.join(ABS_DATA_DIR, file), mode) as f:
        f.write(s)


def load_json_file():
    with open(os.path.join(ABS_DATA_DIR, JSON_FILE)) as f:
        return json.load(f)


def write_json(o):
    with open(os.path.join(ABS_DATA_DIR, JSON_FILE), "w") as f:
        json.dump(o, f)


def csv_safe(m, f):
    if f == Fields.COMMENTS or f == Fields.SCOUT_NAME:
        return '"' + m[f] + '"'
    else:
        return str(m[f])
