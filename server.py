# noinspection PyProtectedMember
from os import _exit as osexit

import sys

import dataconstants
from controllers import datactl
from controllers.messagectl import MessageController
from controllers.socketctl import SocketController
from interface import printing
from interface.header import print_header
from interface.input_handler import InputHandler
from interface.logger import log
from tba.tba_saver import TBASaver


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

    def main(self):
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


if __name__ == "__main__":
    server = Server()
    server.main()
