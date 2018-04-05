import telnetlib
import time
import os
import socket
import json

tracks = ['track 1', 'track 2', 'track 3', 'track 4']
transport_list = []
d3 = telnetlib.Telnet()
status = ''
request_number = None

class Transport:
    def __init__(self, name):
        self.transport_name = name
        self.tracks = []

    def add_tracks(self, track):
        self.tracks.append(track)

    def print_tracks(self):
        for i in range(len(self.tracks)):
            print self.tracks[i]


def load_previous():
    global transport_list
    path = os.path.expanduser('~\config.txt')
    path = os.path.abspath(path)
    file = open(path, 'r')
    data = file.readline()
    data = data.split()
    host = data[1]
    data = file.readline()
    data = data.split()
    port = data[1]
    data = file.readline()
    data = data.split()
    list_size = data[3]
    list_size = int(list_size)
    file.readline()
    for i in range(0, list_size):
        T = file.readline()
        T = T[:-1]
        transport_list.append(Transport(T))
        T = transport_list[i]
        data = file.readline()
        data = data.split()
        track_list_size = data[-1]
        track_list_size = int(track_list_size)
        for i in range(0, track_list_size):
            track = file.readline()
            track = track[:-1]
            track = track.split(',')
            T.add_tracks((track[0], track[1]))

    print_classes()


def init_client():
    global host
    global port
    host = '127.0.0.1'
    port = 54321
    cls()
    try:
        d3.open(host, port, 3)
        print('connection successful')
    except:
        print("cannot connect to server")


def make_new_config():
    cls()
    global host
    global port
    while True:
        host = raw_input('whats the IP address of the d3 machine hosting the session \n')
        try:
            socket.inet_aton(host)
            break
        except socket.error:
            print('not a valid IP')
            time.sleep(1)
            cls()

    while True:
        port = raw_input('whats the port number that d3 is listening to \n')
        try:
            port = int(port)
            if 0 < port < 65535:
                break
            else:
                print('Not a valid port number')
                time.sleep(1)
                cls()
        except:
            print('Not a valid port number')
            time.sleep(1)
            cls()


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def main_menu():
    while True:
        print('type the number representing your choice and press enter to select')
        print('1. load previous configuration')
        print('2. make a new configuration')
        user_input = raw_input()

        if user_input == '1':
            load_previous()
            break
        if user_input == '2':
            make_new_config()
            break
        else:
            print('\n' * 5)
            print('invalid input')
            time.sleep(1)
            cls()


def get_tracks():
    global tracks
    global status
    global request_number
    d3.write('{"query":{"q":"trackList"}}\n')
    data = d3.read_until('\n', 1)
    data = json.loads(data)
    tracks = data['results']
    status = data['status']
    request_number = data['request']

    results = [(track['track'], track['length']) for track in tracks]
    tracks = results


def get_transports():
    global transport_list
    while True:
        data = raw_input('please enter the names of all your transports, Enter nothing once you are done \n')
        if data == '':
            break
        else:
            transport_list.append(Transport(data))
            cls()


def form_classes():
    global transport_list
    global tracks

    for transport in transport_list:
        print(transport.transport_name)
        for track in tracks:
            print(track)

        list = raw_input('type in the numbers corresponding to the transport separating with a space \n')
        list = list.split()

        for i in range(len(list)):
            x = int(list[i])
            x -= 1
            transport.add_tracks(tracks[x])


def print_classes():
    cls()
    for transport in transport_list:
        print(transport.transport_name)
        transport.print_tracks()
        print


def save_config():
    path = os.path.expanduser('~\config.txt')
    path = os.path.abspath(path)
    global host
    global port
    global transport_list
    file = open(path, 'w')
    file.write('HOST: ' + host + ' \n')
    file.write('PORT: ' + str(port) + ' \n')
    file.write('NUMBER OF TRANSPORTS: ' + str(len(transport_list)) + ' \n')
    file.write('\n')
    for transport in transport_list:
        file.write(transport.transport_name + ' \n')
        file.write('NUMBER OF TRACKS: ' + str(len(transport.tracks)) + ' \n')
        for i in range(len(transport.tracks)):
            info = transport.tracks[i]
            file.write(info[0] + ',' + str(info[1]) + ' \n')
    file.write('EOF')

    file.close


def main():
    main_menu()
    while True:
        init_client()
        get_transports()
        get_tracks()
        form_classes()
        print_classes()

        print('are you happy with this configuration?')
        value = raw_input('Y/N \n')
        if value.lower() == 'y':
            save_config()
            break

main()
''' TODO - Need to decode the string that is returned from d3
         - Need to set up track class: name , length
         - Need to link the track class and the Transport class
         - refactor the main() function so it properly run the other functions properly
         - Need to set up a system that sends commands to d3
         - Need to set up a system that verifies that commands have been sent and accepted by d3
         - General Refactoring
'''