import telnetlib
import json


class D3TelnetSession:
    def __init__(self, host, port):

        # setup connection

        self.host = host
        self.port = port
        self.timeout = 3
        self.transport_control = telnetlib.Telnet()
        self.start_connection()

        # setup internal variables

        self.track_list = []
        self.player_list = []
        self._get_player_list()
        self._get_track_list()

        self.request_number = 0
        self.return_status = ""
        self.command = ""
        self.track = ""
        self.location = ""
        self.player = ""
        self.transition = ""

        self.track_command_dict = None
        self.command_dict = None
        self._update_command_dict()

    def _update_command_dict(self):

        self.track_command_dict = {"command": self.command,
                                   "track": self.track,
                                   "location": self.location,
                                   "player": self.player,
                                   "transition": self.transition}

        self.command_dict = {"request": self.request_number,
                             "track_command": self.track_command_dict}

    def start_connection(self):

        self.transport_control.open(self.host, self.port, self.timeout)

    def close_connection(self):

        self.transport_control.close()

    def _get_player_list(self):

        get_player_command = '{"query":{"q":"playerList"}}\n'
        self.transport_control.write(get_player_command.encode("ascii"))

        self.player_list = self.transport_control.read_until('\n'.encode("ascii"), 1)
        self.player_list = self._parse_data(self.player_list, "player")

        self.request_number += 1

    def _get_track_list(self):

        get_track_command = '{"query":{"q":"trackList"}}\n'
        self.transport_control.write(get_track_command.encode("ascii"))

        self.track_list = self.transport_control.read_until('\n'.encode("ascii"), 1)
        self.track_list = self._parse_data(self.track_list, "track")

        self.request_number += 1

    def _parse_data(self, data, json_type):

        print(data)
        data = json.loads(data)  # breaks up the Json string into an dict
        self.request_number = data['request']
        self.return_status = data['status']
        results = None

        if json_type == "track":

            track_list = data['results']
            results = [(track['track']) for track in track_list]

        elif json_type == "player":

            player_list = data['results']
            results = [(player['player']) for player in player_list]

        return results

    def send_command(self, command=None, track=None, player=None, location=None, transition=None):

        if command not in ["play", "playSection", "stop"]:
            raise Exception("Bad command, input is not in list of valid commands")
        else:
            self.command = command

        if track not in self.track_list:
            raise Exception("Bad command, track given does not exist or is not in any setList")
        else:
            self.track = track

        if player not in self.player_list:
            raise Exception(
                "Bad command, player given does not exist or is not currently active in the multi transport")
        else:
            self.player = player

        if location is None:
            self.location = "00:00:00:00"
        else:
            # TODO: Use Regex to verify location
            self.location = location

        if transition is None:
            self.transition = "0"
        else:
            # TODO: figure out how to verify
            self.transition = transition

        self._update_command_dict()

        string = json.dumps(self.command_dict)
        self.transport_control.write(string.encode('ascii'))

        status = self.transport_control.read_until('\n'.encode('ascii'), 1)
        status = status.decode('ascii')
        self.return_status = json.loads(status)
        self.request_number += 1

    def get_track_list(self):
        return self.track_list

    def get_player_list(self):
        return self.player_list