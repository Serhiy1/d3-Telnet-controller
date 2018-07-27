import telnetlib
import json
import os
import re

d3 = telnetlib.Telnet()

status = ''
request_number = 0
data = ""
host = ""
port = 0
transport_list = []
track_list = []
dictionary = {}
max_length = 0
main_quit = False


grouped_block_1 = [re.compile(r'((ps)|p|s)'),re.compile(r'(\d)'),re.compile(r'(\d)'),
                   re.compile(r'([0-9][0-9]:[0-5][0-9]:[0-5][0-9]:[0-5][0-9])'),re.compile(r'(\d)')]
grouped_block_2 = [re.compile(r'((ps)|p|s)'),re.compile(r'(\d)'),re.compile(r'(\d)'),re.compile(r'(\d)')]
grouped_block_3 = [re.compile(r'((ps)|p|s)'),re.compile(r'(\d)'),re.compile(r'(\d)')]
# [play state],[transport],[track],[time],[transition]
# [play state],[transport],[track],[transition]
# [play state],[transport],[track]


def send_data():

    global dictionary
    global request_number
    global status

    quit_loop = False
    key_list = list(dictionary.keys())
    newline = '\n'
    newline = newline.encode('ascii')

    print("\n the syntax for sending a command to d3 will be based a letter and numbering system")
    print('to make this script work you will only need to type in a minimum of three things: ')
    print('[play mode], [transport], [track]')
    print('additionally you also have 2 extra variables, time and transition.'
          ' They are automatically set to 0 if left empty')
    print('there is no need to type out the full names for everything, just the associated numbers')
    print('as a example, if I want transport 1 to play track 3, I will type out "P,1,3" \n ')

    while not quit_loop:

        print_matrix()

        user_input = input('User input: ')
        user_input_list = user_input.split(',')

        if validate_input(user_input) is False:
            break
        else:
            command = user_input_list[0]
            transport = int(user_input_list[1]) -1
            track = int(user_input_list[2]) - 1
            if len(user_input_list) == 3:
                location = "00:00:00:00"
                transition = "0"

            elif len(user_input_list) == 4:
                location = user_input_list[4-1]
                location = str(location)
                transition = "0"

            elif len(user_input_list) == 5:
                location = user_input_list[4 - 1]
                transition = user_input_list[5-1]

            if command == 'p':
                command = 'play'

            elif command == 'ps':
                command = 'playSection'

            elif command == 's':
                command = 'stop'

            transport = key_list[transport]
            track = dictionary[transport][track]
            string = '{"request":%s,"track_command":{"command":"%s","track":"%s","location":"%s","player":"%s","transition":"%s"}}\n' % (
                request_number, command,  track, location, transport, transition)
            log = 'request:%s, %s track: %s at location: %s on transport: %s  using transition %s' % (
                request_number, command,  track, location, transport, transition)

            string = string.encode('ascii')
            d3.write(string)
            status = d3.read_until(newline, 1)
            status = status.decode('ascii')
            status = json.loads(status)

            print(log)
            input(status['status'])

            cls()
            request_number += 1


def validate_input(user_input):

    split_list = user_input.split(',')

    if len(split_list) < 3:
        print("malformed command - not enough arguments given")
        return false

    elif len(split_list) > 5:
        print("malformed command - too many arguments given")
        return false

    elif len(split_list) == 3:
        state = actual_filter(split_list, grouped_block_3, 3)
        return state

    elif len(split_list) == 4:
        state = actual_filter(split_list, grouped_block_2, 4)
        return state

    elif len(split_list) == 5:
        state = actual_filter(split_list, grouped_block_1, 5)
        return state


def actual_filter(user_input, block, number):

    error_list = ["Play state", "Transport", "Track", "Time code", "Fade time"]

    for i in range(len(user_input)):
        if re.match(block[i], user_input[i]) is None:
            error = error_list[i]
            print("malformed command at " + error)
            return False

    return True


def print_matrix():

    global dictionary
    global max_length

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

    for i in range(max_length):
        for u in range(len(temp_list)):
            # snoop = temp_list[u][i]
            if temp_list[u][i] == 'null':
                print(' ' * 28 + ' || ', end='')
            else:
                padding = len(temp_list[u][i])
                padding = 25 - padding
                padding = padding * " "
                print(str(i + 1) + ". " + temp_list[u][i] + padding + ' || ', end='')
        print('')

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


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
    load_data()


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
    for track in results:
        print(track[0], end=', ')
    print()


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
    global max_length

    file = open('data.txt', 'w')

    file.write(host + '\n')
    file.write(str(port) + '\n')

    for key in dictionary.keys():
        list = dictionary[key]
        if len(dictionary[key]) > max_length:
            max_length = len(dictionary[key])
    file.write(str(max_length) + '\n')

    for key in dictionary.keys():
        file.write(key + ',')
        temp = dictionary[key]

        for i in range(len(temp)):
            if i == len(temp)-1:
                file.write(temp[i])
            else:
                file.write(temp[i] + ',')

        if len(temp) < max_length:
            file.write(',')
            number = max_length - len(temp)
            for u in range(number):
                if u == number-1:
                    file.write('null')
                else:
                    file.write('null,')
        file.write('\n')

    file.write('EOF')
    file.close()
    print("data saved")


def load_data():

    global host
    global port
    global dictionary
    global max_length

    host = ''
    port = []
    dictionary = {}
    max_length = 0
    list_of_tracks = []

    escaped = False
    eof = False
    i = 0

    file = open('data.txt', 'r')
    host = file.readline()
    host = host[:-1]
    port = file.readline()
    port = port[:-1]
    port = int(port)
    max_length = file.readline()
    max_length = max_length[:-1]
    max_length = int(max_length)

    while not eof:

        read_data = file.readline()

        if read_data == 'EOF':
            eof = True
        else:
            read_data = read_data.split(',')
            key = read_data[0]
            list_of_tracks = read_data[1:]
            list_of_tracks[-1] = list_of_tracks[-1][:-1]

        for v in range(len(list_of_tracks)):
            dictionary.setdefault(key, []).append(list_of_tracks[v])


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


while not main_quit:
    try:
        main()
    except Exception as error:
        print(type(error))
        print(error.args)
        print(error)
