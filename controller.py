import telnetlib
import json

d3 = telnetlib.Telnet()

status = ''
request_number = 0
data = ""
host = ""
port = 0
transport_list = []
track_list = []
dictionary = {}


def send_data():

    global dictionary
    global request_number

    quit_loop = False
    key_list = list(dictionary.keys())
    newline = '\n'
    newline = newline.encode('ascii')

    print("\n the syntax for sending a command to d3 will be based a letter and numbering system")
    print('to make this script work you will only need to type in three things: [play mode], [transport], [track]')
    print('there is no need to type out the full names for everything, just the associated numbers')
    print('as a example, if I want transport 1 to play track 3, I will type out "P,1,3" \n ')

    while not quit_loop:

        print_matrix()

        user_input = input('User input: ')
        user_input = user_input.split(',')

        command = user_input[0]
        transport = int(user_input[1]) - 1
        track = int(user_input[2]) - 1

        if command == 'p':
            command = 'play'

        elif command == 'ps':
            command = 'playSection'

        elif command == 's':
            command = 'stop'

        transport = key_list[transport]
        track = dictionary[transport][track]

        string = '{"request":%s,"track_command":{"command":"%s","track":"%s","location":"00:00:00:00","player":"%s","transition":"0"}}\n' % (request_number, command,  track,  transport)
        print(string)
        string = string.encode('ascii')
        d3.write(string)
        data = d3.read_until(newline, 1)

        print(data)
        request_number += 1


def print_matrix():

    global dictionary

    key_list = list(dictionary.keys())

    for key in range(len(key_list)):
        padding = len(key_list[key])
        padding = 25 - padding
        padding = padding * " "
        print(str(key + 1) + ". " + key_list[key] + padding + ' || ', end='')

    temp_list = []
    for key in key_list:
        temp_list.append(dictionary[key])

    print('')
    print(('-' * 28 + ' || ') * len(key_list))

    for i in range(len(temp_list)):
        for u in range(len(temp_list)):
            if temp_list[u][i] == 'null ':
                print(' ' * 28 + ' || ', end='')
            else:
                padding = len(temp_list[u][i])
                padding = 25 - padding
                padding = padding * " "
                print(str(i + 1) + ". " + temp_list[u][i] + padding + ' || ', end='')
        print('')


def make_new_config():
    global host
    global port

    good_config = False

    while not good_config:
        host = input('whats the IP address of the machine you are trying to connect to? \n')
        port = input("what port is d3 running on? \n")

        good_config = connect_to_server()

    send_request_command()
    receive_data()
    parse_data()
    get_transports()
    user_selection()
    save_data()


def connect_to_server():

    global host
    global port

    try:
        d3.open(host, port, 3)
        print('connection successful \n')
        return True
    except:
        print("cannot connect to server \n")
        return False


def send_request_command():

    query = ('{"query":{"q":"trackList"}}\n').encode('ascii')
    d3.write(query)


def receive_data():

    global data

    newline = '\n'
    newline = newline.encode('ascii')  # all data needs to be converted to ASCII bytes before being sent or received
    data = d3.read_until(newline, 1)


def parse_data():

    global request_number
    global track_list
    global status
    global data

    data = json.loads(data)   # breaks up the Json string into an dict
    request_number = data['request']
    status = data['status']  #
    track_list = data['results']  #
    results = [(track['track'], track['length']) for track in track_list]
    track_list = results

    print(status)
    print(request_number)
    print(results)


def get_transports():

    global transport_list

    transports = input('write down all the transports with a comma separating each one \n')
    transport_list = transports.split(',')


def user_selection():

    global transport_list
    global track_list

    for i in range(len(transport_list)):
        print(transport_list[i], '\n')
        for n in range(len(track_list)):
            var = track_list[n]
            print(str(n + 1) + ' ' + var[0])

        selection = input('input the associated track number for your each transport using comma separation \n')
        selection = selection.split(',')

        transfer_list = []
        for o in range(len(selection)):
            transfer_list.extend(track_list[int(selection[o]) - 1])

        form_dictionary(transport_list[i], transfer_list)


def form_dictionary(key, selection):

    global dictionary

    for i in range(0, len(selection), 2):
        track = selection[i]
        dictionary.setdefault(key, []).append(track)


def save_data():

    global track_list
    global host
    global port
    global dictionary

    max_length = 0

    file = open('data.txt', 'w')

    file.write(host + '\n')
    file.write(str(port) + '\n' + '\n')

    for key in dictionary.keys():
        list = dictionary[key]
        if len(dictionary[key]) > max_length:
            max_length = len(dictionary[key])

    for key in dictionary.keys():
        file.write(key + '\n')
        temp = dictionary[key]

        for i in range(len(temp)):
            file.write(temp[i] + '\n')

        if len(temp) < max_length:
            number = max_length - len(temp)
            for u in range(number):
                file.write('null \n')
        file.write('---'+'\n')

    file.write('EOF')
    file.close()
    print("data saved")


def load_data():

    global host
    global port
    global dictionary

    escaped = False
    eof = False
    i = 0

    file = open('data.txt', 'r')
    host = file.readline()
    host = host[:-1]
    port = file.readline()
    port = port[:-1]
    port = int(port)
    file.readline()

    temp_list = file.readlines()
    list_of_tracks = []

    while not eof:
        escaped = False
        if temp_list[i] == 'EOF':
            eof = True
        else:
            key = temp_list[i]
            key = key[:-1]
            i += 1
            while not escaped:
                if temp_list[i] == '---\n':
                    escaped = True
                    i += 1
                else:
                    blah = temp_list[i]
                    blah = blah[:-1]
                    list_of_tracks.append(blah)
                    i += 1
        for v in range(len(list_of_tracks)):
            dictionary.setdefault(key, []).append(list_of_tracks[v])
        list_of_tracks = []


def main():

    selection = ""
    selection = input('would you like to load a previous config? y/n \n')
    selection = selection.lower()
    temp = False

    if selection == 'y':
        try:
            load_data()
            temp = connect_to_server()
            if temp == False:
                make_new_config()

        except IOError:
            print('could not load data, making new config \n')
            make_new_config()
    else:
        make_new_config()

    send_data()

main()
