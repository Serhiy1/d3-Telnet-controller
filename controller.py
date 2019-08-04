from tkinter import *
from functools import partial
from d3_session_class import D3TelnetSession


class TimelineControlGUI:

    def __init__(self, parent):
        self.root = parent
        self.connection = None

        self.frame_1 = Frame(master=self.root, width=200, height=200)
        self.frame_2 = Frame(master=self.root, width=350, height=200)
        self.button_frame = Frame(master=self.root)

        self.host_ip_text = StringVar()
        self.host_ip_tk_var = StringVar()
        self.host_port_text = StringVar()
        self.host_port_tk_var = StringVar()

        self.dynamic_player_GUI_labels = []
        self.dynamic_track_GUI_selectors = []
        self.dynamic_play_mode_GUI_selectors = []
        self.dynamic_send_command_GUI_buttons = []

        self.dynamic_play_mode_strings = []
        self.dynamic_track_strings = []

        self.host_port_text_box = Entry(self.frame_1, textvariable=self.host_port_tk_var)
        self.host_ip_text_box = Entry(self.frame_1, textvariable=self.host_ip_tk_var)

        self.player_list = []
        self.track_list = []
        self.play_mode_list = ["play", "playSection", "stop"]

        self.draw_initial_input()

    def draw_initial_input(self):

        self.frame_1.grid(row= 1, column=1)
        self.button_frame.grid(row=2, column=1)

        self.host_ip_text.set("Host ip")
        self.host_ip_tk_var.set("127.0.0.1")

        host_ip_label = Label(self.frame_1, textvariable=self.host_ip_text)
        host_ip_label.grid(row=1, column=1)

        self.host_ip_text_box.grid(row=1, column=2)

        self.host_port_text.set("Host port")
        self.host_port_tk_var.set("54321")

        host_port_label = Label(self.frame_1, textvariable=self.host_port_text)
        host_port_label.grid(row=2, column=1)
        self.host_port_text_box.grid(row=2, column=2)

        switch_button = Button(self.button_frame, text="switch", command=self.switch_frame)
        switch_button.grid(row=1, column=1)

    def switch_frame(self):
        self.frame_1.grid_forget()
        self.button_frame.grid_forget()
        self.frame_2.grid(row=1, column=1)
        self.draw_new_ui()

    def make_and_send_command(self, row_number):
        selected_play_mode = self.dynamic_play_mode_strings[row_number].get()
        selected_track = self.dynamic_track_strings[row_number].get()
        selected_player = self.player_list[row_number]

        self.connection.send_command(command=selected_play_mode, track=selected_track, player=selected_player)

    def draw_new_ui(self):

        self.connection = D3TelnetSession(self.host_ip_text_box.get(), self.host_port_text_box.get())
        self.connection.start_connection()
        self.player_list = self.connection.player_list
        self.track_list = self.connection.track_list
        print(self.track_list)
        print(self.player_list)

        for index, player in enumerate(self.player_list):
            track_string = StringVar()
            track_string.set(self.track_list[0])

            play_mode_string_var = StringVar()
            play_mode_string_var.set(self.play_mode_list[0])

            player_string_var = StringVar()
            player_string_var.set("Transport: %s" % player)

            self.dynamic_play_mode_strings.append(play_mode_string_var)
            self.dynamic_track_strings.append(track_string)

            self.dynamic_player_GUI_labels.append(Label(self.frame_2, textvariable=player_string_var))
            self.dynamic_track_GUI_selectors.append(OptionMenu(self.frame_2, track_string, *self.track_list))
            self.dynamic_play_mode_GUI_selectors.append(OptionMenu(self.frame_2, play_mode_string_var, *self.play_mode_list))
            self.dynamic_send_command_GUI_buttons.append(Button(self.frame_2, text="Execute", command=partial(self.make_and_send_command, index)))

        for index, label in enumerate(self.dynamic_player_GUI_labels):
            label.grid(row=index, column=1)

        for index, menu in enumerate(self.dynamic_track_GUI_selectors):
            menu.grid(row=index, column=2)

        for index, menu in enumerate(self.dynamic_play_mode_GUI_selectors):
            menu.grid(row=index, column=3)

        for index, button in enumerate(self.dynamic_send_command_GUI_buttons):
            button.grid(row=index, column=4)
