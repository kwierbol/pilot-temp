
import bluetooth #trzeba miec pybluez
import threading
import subprocess
import os.path as path
from Utils import *
from PyQt5.QtCore import QObject
import time
from OknoGlowne import Ui_MainWindow
from Song import Song
import SongsQueue


class bluetoothCon(object):

    clients = []

    def __init__(self):
        #hostMACAddress = '60:6D:C7:EF:BE:7C'
        hostMACAddress = self.read_btaddress()
        PORT = 3
        self.BUFF = 1024
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.socket.settimeout(10)
        self.socket.bind((hostMACAddress, PORT))
        self.alive = True

    def listen(self):
        self.socket.listen(10)
        print("Waiting for connection...")
        
        while self.alive:
            try:
                client, clientInfo = self.socket.accept()
                client.settimeout(1000)
                print("Connected: " + str(clientInfo))
                self.clients.append(client)
                # print("Appending client... Full list: " + str(self.clients))
                # print("Length: " + str(len(self.clients)))
                thr1 = threading.Thread(target=self.bluetoothListenToClient, args=(client, clientInfo))
                thr1.start()
                #thr1.join()
            except bluetooth.BluetoothError:
                pass


    def read_btaddress(self):
        cmd = "hciconfig"
        device_id = "hci0"
        status, output = subprocess.getstatusoutput(cmd)
        bt_mac = output.split("{}:".format(device_id))[1].split("BD Address: ")[1].split(" ")[0].strip()
        #print("SERVER BLUETOOTH ADAPTER MAC ADDRESS: " + bt_mac) #debug
        return bt_mac


    def bluetoothListenToClient(self, client, clientInfo):

        a = True
        while a:
            try:
                client.settimeout(120)
                data = client.recv(self.BUFF)

                data = data.decode('utf-8')

                #debug
                print("Data from client: " + data)
                print("SongsQueue.id: " + str(SongsQueue.id))

                if data:
                    #starting new queue
                    if data.startswith("NEW_QUEUE") and SongsQueue.id == -1:
                        SongsQueue.id = data[9:-2]
                        print("DEBUG: nowe id ", SongsQueue.id)
                        client.send("NEW_QUEUE_OK\r\n".encode('utf-8'))
                    #starting new queue but it exists
                    elif data.startswith("NEW_QUEUE") and SongsQueue.id != -1:
                        client.send("NEW_QUEUE_ERROR\r\n".encode('utf-8'))
                    #attach to existing queue
                    elif data.startswith("ATTACH") and SongsQueue.id != -1:
                        pin = data[6:-2]
                        print(pin)
                        if pin != SongsQueue.id:
                            client.send("ATTACH_ERR\r\n".encode('utf-8'))
                            client.close()
                        else:
                            client.send("ATTACH_OK\r\n".encode('utf-8'))
                    #get songs
                    if data.startswith("NEW_SONG"):
                        user_input = data[8:-2]
                        user_path = file_path(SongsQueue.dir_path, user_input)

                        #sanitize user input for path traversal
                        if path.isfile(user_path) and SongsQueue.dir_path in path.abspath(user_path):
                            try:
                                SongsQueue.song_propositions.append(data[8:-2])
                                SongsQueue.queue.append(data[8:-2])
                                SongsQueue.songs_updated.set()
                                client.send("OK\r\n".encode('utf-8'))
                            except:
                                client.send("NEW_SONG_ERR\r\n".encode('utf-8'))
                    elif data.startswith("PLAY"):
                        if(SongsQueue.start == 0):
                            SongsQueue.start = 1
                        else:
                            SongsQueue.start = 0
                    elif data.startswith("NEXT"):
                        #TODO play next
                        # SongsQueue.nextSong = True
                        pass
                    elif data.startswith("PREV"):
                        #TODO play prev
                        # SongsQueue.prevSong = True
                        pass
                    elif data.startswith("DETACH"):
                        client.close()
                        #remove this client from clients list, do it by searhing its index
                        #since you don't know which thread is going to remove the first saved client
                        self.clients.remove(client)
                        # print("Removing client... Full list: " + str(self.clients))
                        # print("Length: " + str(len(self.clients)))
                        print("Client disconnected")

                        #if everyone gets disconnected, reset ID
                        if len(self.clients) == 0:
                            SongsQueue.id = -1
                        a = False
            except:
                print("Closing client")
                if self.clients:
                    try:
                        self.clients.remove(client)
                        # print("Removing client... Full list: " + str(self.clients))
                        # print("Length: " + str(len(self.clients)))
                    except:
                        print("Error while removing client from clients list. Might not exist")
                    #if everyone gets disconnected, reset ID
                if len(self.clients) == 0:
                    SongsQueue.id = -1
                client.close()
                a = False

        return ""

    def updateAllClients(self):

        if SongsQueue.queue:
            current_song = Song(SongsQueue.queue[0])
            msg = "CURRENT_" + current_song.getTitle() + "_" + current_song.getArtist() + "\r\n"
            print("Sending message: " + msg)
            for client in self.clients:
                client.send(msg.encode('utf-8'))

    def bluetoothClose(self):
        self.socket.close()
        self.alive = False


