import select
import socket
import bluetooth
import subprocess
import SongsQueue
import OknoGlowne
import os.path as path


class bluetoothConEvent(object):

    # sock = None

    inputs = []
    outputs = []

    # mapowanie socket-dane
    message_queues = {}


    def __init__(self):
        # hostMACAddress = '60:6D:C7:EF:BE:7C'
        hostMACAddress = '34:F6:4B:22:C6:39'
        PORT = 3
        self.BUFF = 1024
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.settimeout(10)
        self.sock.setblocking(0)
        self.sock.bind((hostMACAddress, PORT))
        self.alive = True
        self.inputs.append(self.sock)

    def recv_until(self, client, delimiter):
        result = ""
        data = b''
        while not result.endswith(delimiter):
            data = data + client.recv(1)
            result = data.decode('utf-8')
        return result


    def listen(self):
        self.sock.listen(10)
        print("Waiting for connection...")

        while self.inputs:
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)

            # jesli zdarzenie nastapilo w liscie do czytania
            for r in readable:

                # jesli zdarzenie wywolalo gniazdo serwera
                if r is self.sock:

                    client, addr = self.sock.accept()
                    client.setblocking(0)
                    self.inputs.append(client)
                    self.message_queues[client] = ""

                # jesli zdarzenie wywolalo gniazdo klienta - tutaj obsluz komunikaty protokolu
                else:

                    data = self.recv_until(r, '\r\n')

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
                self.outputs.remove(w)
                self.inputs.remove(w)
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
        if data:
            print(data)

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
                    print("attach err")
                    client.send("ATTACH_ERR\r\n".encode('utf-8'))
                    client.close()
                else:
                    print("attach ok")
                    client.send("ATTACH_OK\r\n".encode('utf-8'))
            # get songs
            if data.startswith("NEW_SONG"):
                try:
                    SongsQueue.song_propositions.append(data[8:-2])
                    SongsQueue.queue.append(data[8:-2])
                    SongsQueue.songs_updated.set()
                    client.send("OK\r\n".encode('utf-8'))
                except:
                    client.send("NEW_SONG_ERR\r\n".encode('utf-8'))
            elif data.startswith("PLAY\r\n"):
                if (SongsQueue.start == 0):
                    SongsQueue.player.play()
                    SongsQueue.player.positionChanged.connect(
                        OknoGlowne.Ui_MainWindow.update_position)  # zaktualizuje sie tylko raz
                    SongsQueue.player.durationChanged.connect(OknoGlowne.Ui_MainWindow.update_duration)
                    SongsQueue.start = 1

                else:
                    SongsQueue.player.pause()
                    SongsQueue.start = 0


            elif data.startswith("NEXT\r\n"):
                try:
                    # OknoGlowne.ui.nextSong() #nie dziala
                    pass
                except:
                    print(sys.exc_info()[0])
            elif data.startswith("PREV\r\n"):
                # OknoGlowne.Ui_MainWindow.prevSong()
                pass
            elif data.startswith("DETACH"):
                client.close()
                # remove this client from clients list, do it by searhing its index
                # since you don't know which thread is going to remove the first saved client
                self.clients.remove(client)
                # print("Removing client... Full list: " + str(self.clients))
                # print("Length: " + str(len(self.clients)))
                print("Client disconnected")

                # if everyone gets disconnected, reset ID
                if len(self.clients) == 0:
                    SongsQueue.id = -1
                a = False
        else:
            print("PUSTA DATA - zamykanie klienta6")
            client.close()
