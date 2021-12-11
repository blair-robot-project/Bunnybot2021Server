import bluetooth
from threading import Thread

from dataconstants import MAC_DICT
from interface import printing
from controllers.connection import Connection
from controllers.systemctl import get_host_mac

PORT = 4
BACKLOG = 1
# Max message size
SIZE = 1024


class SocketController:
    clients = set()
    connecting = False

    def __init__(self, on_receive):
        self.host_mac = get_host_mac()
        if self.host_mac:
            # Setup server socket
            self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.server_sock.bind((self.host_mac, PORT))
            self.server_sock.listen(BACKLOG)
            self.server_sock.settimeout(3)

            self.on_receive = on_receive

    def start_connecting(self):
        if self.host_mac:
            self.connecting = True
            Thread(target=self.connect).start()

    def connect(self):
        while self.connecting:
            # Wait for connection
            client_sock, client_info = self.server_sock.accept()

            if self.connecting:
                # Setup connection
                connection = Connection(
                    client_sock,
                    MAC_DICT.get(client_info[0], client_info[0]),
                    lambda msg: self.on_receive(msg, connection),
                    lambda: safe_remove(self.clients, connection),
                )
                self.clients.add(connection)

                # Listen for data
                connection.start_listening()
            else:
                client_sock.close()

    def blanket_send(self, msg):
        for connection in self.clients:
            connection.send(msg)

    # Closes all connections and the server
    def close(self):
        self.connecting = False
        for connection in self.clients:
            connection.close()
        self.clients.clear()
        self.server_sock.close()
        printing.printf(
            "Closed server", style=printing.STATUS, log=True, logtag="socketctl.close"
        )


def safe_remove(s, k):
    try:
        s.remove(k)
    except KeyError:
        pass
