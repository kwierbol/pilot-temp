from threading import Event
import platform

#user proposals - buffer
song_propositions = []
songs_updated = Event()

#actual queue keeping track of the current song
queue = []

#id, initialized to -1 if no clients are connected
id = -1

dir_path = None

#pplayer actions
start = 0 #0 pause 1 start 2 stop

#next/prev song in playlist ???
nextSong = False
prevSong = False


