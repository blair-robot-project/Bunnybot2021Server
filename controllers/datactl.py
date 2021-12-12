import json
import os
from queue import Queue

import dataconstants
import interface.printing as printing
from controllers import systemctl
from dataconstants import JSON_FILE_NAME, CSV_FILE_NAME, GeneralFields


class DataController:
    data_queue = Queue()
    data = dict()
    data_changed = True

    def __init__(self, dataconsts: dataconstants.DataConstants):
        self.dataconsts = dataconsts
        self.data = load_json_file(dataconsts)
        self.drive = dataconsts.DRIVE

    def queue_data(self, data, source):
        self.data_queue.put((data, source))

    def update(self):
        # While there is data to add, parse it
        data = False
        while not self.data_queue.empty():
            data = True
            self.parse_data(*self.data_queue.get())

        if data:
            write_json(self.data, self.dataconsts)
            self.to_csv()
            self.data_changed = True

        # If there is a flash drive and there is new data for it, upload the data
        if self.data_changed and os.path.exists(self.dataconsts.CSV_FILE_PATH):
            if self.drive:
                systemctl.copy(
                    self.dataconsts.CSV_FILE_PATH,
                    os.path.join(self.drive, os.path.sep + CSV_FILE_NAME),
                )
                self.data_changed = False
            elif systemctl.checkdev():
                self._update_drive()
                self.data_changed = False

    def _update_drive(self):
        """Writes data to a removable device (Linux-specific!)"""
        mount_point = systemctl.mount()
        if mount_point:
            systemctl.copy(
                self.dataconsts.CSV_FILE_PATH,
                os.path.join(mount_point, CSV_FILE_NAME),
            )
            systemctl.unmount()

    def parse_data(self, data, source):
        if source not in self.data:
            self.data[source] = dict()
        if str(data[GeneralFields.TIMESTAMP.value]) not in self.data[source]:
            self.data[source][str(data[GeneralFields.TIMESTAMP.value])] = dict()
        self.data[source][str(data[GeneralFields.TIMESTAMP.value])][
            str(data[GeneralFields.REVISION.value])
        ] = data

    def to_csv(self):
        s = ",".join(self.dataconsts.ORDER) + "\n"
        for v in self.data.values():
            for id in v.values():
                m = id[str(max(map(int, id.keys())))]
                s += (
                        ",".join(
                            [
                                csv_safe(m, f)
                                if f in m
                                else missing_field(
                                    f, m[GeneralFields.TIMESTAMP.value], m[GeneralFields.REVISION.value]
                                )
                                for f in self.dataconsts.ORDER
                            ]
                        )
                        + "\n"
                )
        write_file(CSV_FILE_NAME, s, self.dataconsts, mode="w")

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
                if match[GeneralFields.MATCH.value] not in teams_by_match:
                    teams_by_match[match[GeneralFields.MATCH.value]] = []
                teams_by_match[match[GeneralFields.MATCH.value]].append(match[GeneralFields.TEAM.value])

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


def write_file(file, s, dataconsts: dataconstants.DataConstants, mode="a"):
    with open(os.path.join(dataconsts.abs_data_dir, file), mode) as f:
        f.write(s)


def load_json_file(dataconsts: dataconstants.DataConstants):
    path = os.path.join(dataconsts.abs_data_dir, JSON_FILE_NAME)
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("{}")
    with open(path) as f:
        return json.load(f)


def write_json(o, dataconsts: dataconstants.DataConstants):
    with open(os.path.join(dataconsts.abs_data_dir, JSON_FILE_NAME), "w") as f:
        json.dump(o, f)


def csv_safe(m, f):
    if f == GeneralFields.COMMENTS.value or f == GeneralFields.RECORDER_NAME.value:
        return '"' + m[f] + '"'
    else:
        return str(m[f])
