import telnetlib, json, os, re, time
from timecode import Timecode

d3 = telnetlib.Telnet()
dictionary = {}

grouped_block_1 = [re.compile(r'((ps)|p|s)'), re.compile(r'(\d)'), re.compile(r'(\d)'),
                   re.compile(r'([0-9][0-9]:[0-5][0-9]:[0-5][0-9]:[0-5][0-9])'), re.compile(r'(\d)')]
grouped_block_2 = [re.compile(r'((ps)|p|s)'), re.compile(r'(\d)'), re.compile(r'(\d)'), re.compile(r'(\d)')]
grouped_block_3 = [re.compile(r'((ps)|p|s)'), re.compile(r'(\d)'), re.compile(r'(\d)')]

# List of regex list to verify input commands from the users
# [play state],[transport],[track],[time],[transition]
# [play state],[transport],[track],[transition]
# [play state],[transport],[track]


def create_new_command_file():

    cls()
    print("command list file does not exist")

    file = open("command list.txt", "w")
    file.write("The command list is formatted using a command - time code pair"
               "as an example: p,1,1/ 00:00:17:08 would be a valid command"
               "subsequent commands are placed onto a newline "
               "delete this paragraph after populating the file with the necessary commands")
    file.close()
    print("created command list.txt in the working directory of the the python script"
          "please read the instructions inside the file"
          "this script will now close")
    input()
    quit()


def run_timecode_command_list():

    frame_rate = "30"  # default frame rate

    command_increment = 0
    frame_count = 0
    marker = time.time()

    clock = Timecode(frame_rate)
    command_list = load_command_list()

    if command_list[0] == "null":
        create_new_command_file()
    else:

        while True:

            delta = time.time() - marker  # time delta returned in microseconds

            if delta >= 1/int(frame_rate):  # Converts microseconds into frames, due to variance cannot be a exact comparison
                # code below should take less than a frame to process to keep the clock accurate

                frame_count += 1  # Total frame count
                tc_list = clock.frames_to_tc(frame_count)
                tc = clock.tc_to_string(tc_list[0], tc_list[1], tc_list[2], tc_list[3])
                marker = time.time()
                print(tc, end="\r")

                if command_list[command_increment] == "end":
                    print("finished command list")
                    input("closing program")
                    quit()
                else:
                    comp_1 = clock.tc_to_frames(tc)
                    comp_2 = clock.tc_to_frames(command_list[command_increment][1])

                    if comp_1 >= comp_2:
                        print("                  ", end="\r")
                        print(command_list[command_increment][1], " - ", command_list[command_increment][0])
                        send_data(command_list[command_increment][0])
                        command_increment += 1

    print("Finished playing through the command list")


def load_command_list():

    end = False
    command_list = []

    try:
        command_file = open("command list.txt", "r")
    except IOError:
        command_list.append("null")
        return command_list

    while not end:

        temp_string = command_file.readline()

        if temp_string == "end\n":
            command_list.append("end")  # marking end of file
            return command_list

        else:
            temp_string = temp_string[:-1]
            temp_list = temp_string.split("/")
            temp_tuple = tuple(temp_list)
            command_list.append(temp_tuple)


def playback_or_live():

    valid_input = False

    while not valid_input:
        choice = input("Do you want to run a series of commands from a save file(y) or run custom commands(n)?\n")
        if choice.lower() == "y":
            run_timecode_command_list()
        if choice.lower() == "n":
            live_commands()
        else:
            print("Invalid input")
            cls()


def live_commands():

    quit_loop = False

    while not quit_loop:
        print("""Input syntax shown below 
        [play state],[transport],[track] - ps,1,1
        [play state],[transport],[track],[transition] - ps,1,1,1
        [play state],[transport],[track],[time],[transition] - ps,1,1,00:00:00:00,1    
        If you want to put multiple commands simultaneously use the '/' key to split them
            
        Available play states - ps - play section, p - play, s - stop \n """)

        print_matrix()

        command = input('User input: ')
        if "/" in command:
            command_list = command.split('/')
            for command in command_list:
                send_data(command)
        else:
            send_data(command)

        input("press enter to continue")
        cls()


def send_data(user_command):

    global dictionary
    request_number = 0
    transport_list = dictionary["transport list"]

    newline = '\n'
    newline = newline.encode('ascii')
    commands = user_command.split(',')

    if format_validation(user_command) is False:
        print("invalid input")
        input("enter to continue\n")
        cls()
    else:
        command = commands[0]
        transport = int(commands[1]) -1
        track = int(commands[2]) - 1

        if len(commands) == 3:
            location = "00:00:00:00"
            transition = "0"

        elif len(commands) == 4:
            location = commands[4-1]
            location = str(location)
            transition = "0"

        elif len(commands) == 5:
            location = commands[4 - 1]
            transition = commands[5-1]

        if command == 'p':
            command = 'play'

        elif command == 'ps':
            command = 'playSection'

        elif command == 's':
            command = 'stop'

        transport = transport_list[transport]
        track = dictionary[transport][track]
        string = '{"request":%s,"track_command":{"command":"%s",' \
                 '"track":"%s","location":"%s","player":"%s","transition":"%s"}}\n' % (
                    request_number, command,  track, location, transport, transition)

        log = 'request %s: %s track: %s at location: %s on transport: %s  using transition %s' % (
            request_number, command,  track, location, transport, transition)

        string = string.encode('ascii')
        d3.write(string)
        status = d3.read_until(newline, 1)
        status = status.decode('ascii')
        status = json.loads(status)

        print(log)
        print(status['status'])

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
        state = actual_filter(split_list, grouped_block_3)
        if state:
            state = input_validation(split_list)
        return state

    elif len(split_list) == 4:
        state = actual_filter(split_list, grouped_block_2)
        if state:
            state = input_validation(split_list)
        return state

    elif len(split_list) == 5:
        state = actual_filter(split_list, grouped_block_1)
        if state:
            state = input_validation(split_list)
        return state


def actual_filter(user_input, block):

    error_list = ["Play state", "Transport", "Track", "Time code", "Fade time"]

    for i in range(len(user_input)):
        if re.match(block[i], user_input[i]) is None:
            error = error_list[i]
            print("malformed command at " + error)
            return False

    return True


def input_validation(user_input):

    global dictionary
    transport_list = list(dictionary["transport list"])

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
    transport_list = dictionary["transport list"]

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

    track_list = get_track_list_from_server()
    transport_list = get_transports()

    dictionary["transport list"] = transport_list

    create_transport_track_dict(track_list, transport_list)
    save_data()
    load_data()


def connect_to_server(host, port):

    try:
        d3.open(host, port, 3)
        print('connection successful \n')
        return True
    except Exception as error:
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
    try:
        file = open('data.txt', 'r')
    except IOError:
        print('file does not exist, making new config \n')
        make_new_config()

    data = file.readline()
    file.close()
    dictionary = json.loads(data)

    if not connect_to_server(dictionary["host"], dictionary["port"]):
        print("failed to connect to server"
              "Creating a new configuration")
        make_new_config()
    else:
        transport_list = list(dictionary["transport list"])
        max_length = dictionary["max length"]

    # Everything below is done to maintain compatibility with PIA code that draws the table

    for transport in transport_list:
        if max_length > len(dictionary[transport]):
            padding = max_length - len(dictionary[transport])
            for i in range(padding):
                dictionary.setdefault(transport, []).append("null")


def main():

    valid = False

    while not valid:

        selection = input('would you like to load a previous config? y/n or q for quit \n')
        selection = selection.lower()

        if selection.lower() == 'y':
            load_data()
            valid = True

        elif selection.lower() == "n":
            make_new_config()
            valid = True

        elif selection.lower() == "q":
            quit()

        else:
            input("invalid input, enter to continue")
            cls()

    playback_or_live()


try:
    main()
except Exception as error:
    print(type(error))
    print(error.args)
    print(error)
