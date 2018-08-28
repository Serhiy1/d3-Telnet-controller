import telnetlib
import json
import os
import re

d3 = telnetlib.Telnet()
main_quit = False

dictionary = {}
grouped_block_1 = [re.compile(r'((ps)|p|s)'), re.compile(r'(\d)'), re.compile(r'(\d)'),
                   re.compile(r'([0-9][0-9]:[0-5][0-9]:[0-5][0-9]:[0-5][0-9])'), re.compile(r'(\d)')]
grouped_block_2 = [re.compile(r'((ps)|p|s)'), re.compile(r'(\d)'), re.compile(r'(\d)'), re.compile(r'(\d)')]
grouped_block_3 = [re.compile(r'((ps)|p|s)'), re.compile(r'(\d)'), re.compile(r'(\d)')]

# [play state],[transport],[track],[time],[transition]
# [play state],[transport],[track],[transition]
# [play state],[transport],[track]


def send_data():

    global dictionary
    request_number = 0
    status = ""

    quit_loop = False
    key_list = list(dictionary.keys())
    key_list.remove("host")
    key_list.remove("port")
    key_list.remove("max length")

    newline = '\n'
    newline = newline.encode('ascii')

    print("""Input syntax
[play state],[transport],[track] - ps,1,1
[play state],[transport],[track],[transition] - ps,1,1,1
[play state],[transport],[track],[time],[transition] - ps,1,1,00:00:00:00,1 \n

Available play states - ps - play section, p - play, s - stop \n """)
          
    while not quit_loop:

        print_matrix()

        user_input = input('User input: ')
        user_input_list = user_input.split(',')

        if format_validation(user_input) is False:
            print("invalid input")
            input("enter to continue\n")
            cls()
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
            log = 'request %s: %s track: %s at location: %s on transport: %s  using transition %s' % (
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


def format_validation(user_input):

    split_list = user_input.split(',')

    if len(split_list) < 3:
        print("malformed command - not enough arguments given")
        return False

    elif len(split_list) > 5:
        print("malformed command - too many arguments given")
        return False

    elif len(split_list) == 3:
        state = actual_filter(split_list, grouped_block_3, 3)
        if state:
            state = input_validation(split_list)
        return state

    elif len(split_list) == 4:
        state = actual_filter(split_list, grouped_block_2, 4)
        if state:
            state = input_validation(split_list)
        return state

    elif len(split_list) == 5:
        state = actual_filter(split_list, grouped_block_1, 5)
        if state:
            state = input_validation(split_list)
        return state


def actual_filter(user_input, block, number):

    error_list = ["Play state", "Transport", "Track", "Time code", "Fade time"]

    for i in range(len(user_input)):
        if re.match(block[i], user_input[i]) is None:
            error = error_list[i]
            print("malformed command at " + error)
            return False

    return True


def input_validation(user_input):

    global dictionary
    transport_list = list(dictionary.keys())
    transport_list.remove("host")
    transport_list.remove("port")
    transport_list.remove("max length")

    # The "-1" is used to change the 1 index to 0 index

    if (int(user_input[1])) > len(transport_list):
        print("transport not in list")
        return False
    if (int(user_input[2])) > len(dictionary[transport_list[int(user_input[1]) - 1]]): # using the dictionary to get the tracklist using the user input
        print("track not in list")
        return False

    return True


def print_matrix():

    global dictionary

    max_length = dictionary["max length"]
    transport_list = list(dictionary.keys())
    transport_list.remove("host")
    transport_list.remove("port")
    transport_list.remove("max length")

    for key in range(len(transport_list)):
        padding = len(transport_list[key])
        padding = 25 - padding
        padding = padding * " "
        print(str(key + 1) + ". " + transport_list[key] + padding + ' || ', end='')

    temp_list = []
    for key in transport_list:
        temp_list.append(dictionary[key])

    print('')
    print(('-' * 28 + ' || ') * len(transport_list))

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

    print("\n")

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def make_new_config():
    global dictionary
    good_config = False

    while not good_config:
        host = input('whats the IP address of the machine you are trying to connect to? \n')
        port = input("what port is d3 running on? \n")

        good_config = connect_to_server(host, port)

    dictionary['host'] = host
    dictionary['port'] = str(port)

    track_list = get_track_list_from_server()  # done
    transport_list = get_transports()  # done
    create_transport_track_dict(track_list, transport_list)  # done
    save_data()
    load_data()


def connect_to_server(host,port):

    try:
        d3.open(host, port, 3)
        print('connection successful \n')
        return True
    except:
        print("cannot connect to server \n")
        return False


def get_track_list_from_server():

    newline = '\n'

    query = ('{"query":{"q":"trackList"}}\n').encode('ascii')
    d3.write(query)
    newline = newline.encode('ascii')  # all data needs to be converted to ASCII bytes before being sent or received
    data = d3.read_until(newline, 1)

    data = parse_data(data)

    return data


def parse_data(data):

    global request_number
    global status

    data = json.loads(data)   # breaks up the Json string into an dict
    request_number = data['request']
    status = data['status']  #
    track_list = data['results']  #
    results = [(track['track']) for track in track_list]

    return results


def get_transports():

    transports = input('write down all the transports with a comma separating each one \n')
    transport_list = transports.split(',')
    return transport_list


def create_transport_track_dict(track_list, transport_list):

    global dictionary
    max_length = 0

    for i in range(len(transport_list)):
        print(transport_list[i], '\n')
        for n in range(len(track_list)):
            print(str(n + 1) + ' ' + track_list[n])

        selection = input('input the associated track number for your each transport using comma separation \n')
        selection = selection.split(',')

        if len(selection) > max_length:  # Need to gather the maximum length of the list
            max_length = len(selection)

        transfer_list = []
        for o in range(len(selection)):
            index = int(selection[o]) - 1  # selection is indexed by 1 and list is 0 indexed
            transfer_list.append(track_list[index])

        form_dictionary(transport_list[i], transfer_list)

    dictionary["max length"] = max_length


def form_dictionary(key, selection):

    global dictionary

    for track in selection:
        dictionary.setdefault(key, []).append(track)


def save_data():

    global dictionary

    serialised_text = json.dumps(dictionary)

    file = open('data.txt', 'w')
    file.write(serialised_text)
    file.close()

    print("data saved")


def load_data():

    global dictionary

    file = open('data.txt', 'r')
    data = file.readline()
    dictionary = json.loads(data)
    transport_list = list(dictionary.keys())  # Get the list of transports, removing the host, port and max length

    max_length = dictionary["max length"]

    transport_list.remove("host")
    transport_list.remove("port")
    transport_list.remove("max length")

    # Everything below is done to maintain compatibility with PIA code that draws the table

    for transport in transport_list:
        if max_length > len(dictionary[transport]):
            padding = max_length - len(dictionary[transport])
            for i in range(padding):
                dictionary.setdefault(transport, []).append("null")


def main():

    global dictionary

    selection = input('would you like to load a previous config? y/n \n')
    selection = selection.lower()

    if selection == 'y':
        try:
            load_data()
            temp = connect_to_server(dictionary["host"], dictionary["port"])
            if temp == False:
                make_new_config()

        except IOError:
            print('could not load data, making new config \n')
            make_new_config()
    else:
        make_new_config()

    send_data()


while not main_quit:
    main()

'''try:
main()
except Exception as error:
print(type(error))
print(error.args)
print(error)

'''


# TODO : Investigate the random variable pass through at the actual filter function




