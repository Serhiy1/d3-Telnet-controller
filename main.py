if __name__ == "__main__":
    from tkinter import *
    from controller import TimelineControlGUI

    root = Tk()
    root.title('simple GUI')
    root.geometry("725x450")
    root.resizable(width=False, height=False)
    validation_ui = TimelineControlGUI(root)
    root.mainloop()