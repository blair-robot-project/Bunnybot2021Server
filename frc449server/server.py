# noinspection PyProtectedMember
from os import _exit as osexit

import sys

from frc449server import dataconstants
from frc449server.controllers import datactl
from frc449server.controllers.messagectl import MessageController
from frc449server.controllers.socketctl import SocketController
from frc449server.interface import printing
from frc449server.interface.header import print_header
from frc449server.interface.input_handler import InputHandler
from frc449server.interface.logger import log
from frc449server.tba.tba_saver import TBASaver


class Server:
    def __init__(self):
        log("server.main", "+" * 20)
        log("server.main", "Server started")

        print_header()
        if len(sys.argv) > 1:
            data_dir = sys.argv[1]
        else:
            data_dir = input("Absolute data directory (e.g. '/home/user/Desktop') ")
        self.dataconsts = dataconstants.DataConstants(data_dir)
        self.input_handler = InputHandler(self)

        self.data_controller = datactl.DataController(self.dataconsts)
        msgctl = MessageController(self.data_controller)
        self.socketctl = SocketController(msgctl.handle_msg)

        self.tba = TBASaver(self.dataconsts.EVENT)

    def run(self):
        self.input_handler.start_listening()

        printing.printf(
            "Waiting for connections",
            style=printing.STATUS,
            log=True,
            logtag="server.main",
        )
        self.socketctl.start_connecting()

        while True:
            try:
                self.data_controller.update()
            except KeyboardInterrupt:
                # Make sure everything made it into the data file
                self.data_controller.update()

                self.socketctl.close()

                log("server.main", "Server stopped")
                log("server.main", "-" * 20)

                # Quit everything (closes all the many threads)
                osexit(1)
