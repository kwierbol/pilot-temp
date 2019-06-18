import select
import socket
import bluetooth
import subprocess
import SongsQueue
import Utils
import os.path as path


class bluetoothConEvent(object):

    inputs = [socket]
    outputs = []

    # mapowanie socket-dane
    message_queues = {}


    def __init__(self):
        # hostMACAddress = '60:6D:C7:EF:BE:7C'
        hostMACAddress = self.read_btaddress()
        PORT = 3
        self.BUFF = 1024
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.socket.settimeout(10)
        self.socket.setblocking(0)
        self.socket.bind((hostMACAddress, PORT))
        self.alive = True


    def listen(self):
        self.socket.listen(10)
        print("Waiting for connection...")

        while self.inputs:
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)

            # jesli zdarzenie nastapilo w liscie do czytania
            for r in readable:

                # jesli zdarzenie wywolalo gniazdo serwera
                if r is s:

                    client, addr = self.socket.accept()
                    client.setblocking(0)
                    self.inputs.append(client)
                    self.message_queues[client] = ""

                # jesli zdarzenie wywolalo gniazdo klienta - tutaj obsluz komunikaty protokolu
                else:

                    data = r.recv(1024)

                    if data:
                        self.message_queues[r] = data
                        if r not in self.outputs:
                            self.outputs.append(r)

                    # jesli nic nie przyszlo to ktos sie rozlaczyl
                    else:

                        if r in self.outputs:
                            self.outputs.remove(r)

                        self.inputs.remove(r)
                        r.close()
                        del self.message_queues[r]

            # jesli zdarzenie nastapilo w liscie do pisania
            for w in writable:
                data = self.message_queues.get(w)

                #data handler
                self.protocol_handler(data, w)

                del self.message_queues[w]
                # self.outputs.remove(w)
                # self.inputs.remove(w)
                # w.close()

            # jesli zdarzenie nastapilo w liscie odpowiedzialnej za monitorowanie bledow
            for e in exceptional:
                self.inputs.remove(e)
                if e in self.outputs:
                    self.outputs.remove(e)
                e.close()
                del self.message_queues[e]


    def protocol_handler(self, data, client):

        # starting new queue
        if data.startswith("NEW_QUEUE") and SongsQueue.id == -1:
            SongsQueue.id = data[9:-2]
            print("DEBUG: nowe id ", SongsQueue.id)
            client.send("NEW_QUEUE_OK\r\n".encode('utf-8'))
        # starting new queue but it exists
        elif data.startswith("NEW_QUEUE") and SongsQueue.id != -1:
            client.send("NEW_QUEUE_ERROR\r\n".encode('utf-8'))
        # attach to existing queue
        elif data.startswith("ATTACH") and SongsQueue.id != -1:
            pin = data[6:-2]
            print(pin)
            if pin != SongsQueue.id:
                client.send("ATTACH_ERR\r\n".encode('utf-8'))
                client.close()
            else:
                client.send("ATTACH_OK\r\n".encode('utf-8'))
        # get songs
        if data.startswith("NEW_SONG"):
            user_input = data[8:-2]
            user_path = Utils.file_path(SongsQueue.dir_path, user_input)

            # sanitize user input for path traversal
            if path.isfile(user_path) and SongsQueue.dir_path in path.abspath(user_path):
                try:
                    SongsQueue.song_propositions.append(data[8:-2])
                    SongsQueue.queue.append(data[8:-2])
                    SongsQueue.songs_updated.set()
                    client.send("OK\r\n".encode('utf-8'))
                except:
                    client.send("NEW_SONG_ERR\r\n".encode('utf-8'))
        elif data.startswith("PLAY"):
            if (SongsQueue.start == 0):
                SongsQueue.start = 1
            else:
                SongsQueue.start = 0
        elif data.startswith("NEXT"):
            # TODO play next
            # SongsQueue.nextSong = True
            pass
        elif data.startswith("PREV"):
            # TODO play prev
            # SongsQueue.prevSong = True
            pass
        elif data.startswith("DETACH"):
            self.inputs.remove(client)
            self.outputs.remove(client)
            del self.message_queues[client]
            client.close()
            print("Client disconnected")

    def read_btaddress(self):
        cmd = "hciconfig"
        device_id = "hci0"
        status, output = subprocess.getstatusoutput(cmd)
        bt_mac = output.split("{}:".format(device_id))[1].split("BD Address: ")[1].split(" ")[0].strip()
        # print("SERVER BLUETOOTH ADAPTER MAC ADDRESS: " + bt_mac) #debug
        return bt_mac
