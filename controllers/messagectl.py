import json
from enum import Enum

from dataconstants import GeneralFields
from interface import printing


class MsgTypes(Enum):
    DATA = "DATA"
    MULTI = "MULTI"
    SYNC = "SYNC"
    SCHEDULE = "SCHEDULE"
    TEAM_LIST = "TEAM_LIST"
    ERROR = "ERROR"
    SYNC_SUMMARY = "SYNC_SUMMARY"


def make_message(msg_type, body):
    return json.dumps({"type": msg_type.name, "body": body})


def messages_to_json(msgs):
    if not msgs:
        return None
    full = "".join(msgs)
    try:
        msg = json.loads(full)
        if "type" in msg and "body" in msg:
            msg["type"] = MsgTypes(msg["type"])
            return msg
        else:
            raise json.JSONDecodeError
    except json.JSONDecodeError:
        return messages_to_json(msgs[1:])


def invalid_msg(msg, client):
    printing.printf(
        "Invalid message from",
        client.name,
        ":",
        str(msg),
        style=printing.YELLOW,
        log=True,
        logtag="msgctl.invalid_msg",
    )


# TODO: move to datactl
def summarize_data(data, client_name):
    printing.printf(
        ("Data" if data[GeneralFields.REVISION.value] == 0 else "Edit")
        + " from "
        + data[GeneralFields.RECORDER_NAME.value]
        + " on "
        + client_name
        + " for team "
        + str(data[GeneralFields.TEAM.value])
        + " in match "
        + str(data[GeneralFields.MATCH.value]),
        style=printing.NEW_DATA,
        log=True,
        logtag="msgctl.handle_msg",
    )


class MessageController:
    msg_strings = dict()

    def __init__(self, datactl):
        self.datactl = datactl

    def handle_msg(self, msg, client):
        if client not in self.msg_strings:
            self.msg_strings[client] = []
        self.msg_strings[client].append(msg)
        msg = messages_to_json(self.msg_strings[client])
        if msg is not None:
            if msg["type"] == MsgTypes.DATA:
                self.datactl.queue_data(msg["body"], client.name)
                summarize_data(msg["body"], client.name)

            elif msg["type"] == MsgTypes.MULTI:
                for data in msg["body"]:
                    self.datactl.queue_data(data, client.name)
                    summarize_data(data, client.name)

            elif msg["type"] == MsgTypes.SYNC:
                client.send(
                    make_message(
                        MsgTypes.SYNC_SUMMARY, self.datactl.sync_summary(client.name)
                    )
                )

            elif msg["type"] == MsgTypes.ERROR:
                # TODO: Resend message?
                print("invalid message sent to", client.name)

            else:
                invalid_msg(msg, client)
