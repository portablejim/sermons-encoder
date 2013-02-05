#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk

class sermonsLabel(ttk.Label):
    def __init__(self, parent, text, row):
        self.parent = parent
        ttk.Label.__init__(self, parent, text=text)
        self.grid(column=0, row=row, sticky=(W))

class EncoderUi(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.speaker = list()

        self.initUI()

    def initUI(self):
        self.parent.title("Sermon Encoder")
        self.grid(column=0, row=0, sticky=(N,S,E,W))
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(5, weight=2)

        self.parent.minsize(300, 150)

        self.grid(column=0, row=0)

        self.sermon_title = StringVar()
        self.sermon_speaker = StringVar()
        self.sermon_passage = StringVar()
        self.sermon_series = StringVar()
        self.sermon_service = StringVar()
        self.sermon_date = StringVar()
        self.sermon_directory = StringVar()

        series_list_container = Frame(self)
        series_list_container.grid(column=0, row=0, sticky=(N,S,E,W))
        series_list_scrollbar = Scrollbar(series_list_container)
        series_list = Listbox(series_list_container, width=40, height=5, yscrollcommand=series_list_scrollbar.set)
        series_list.grid(column=0, row=0, sticky=(N,S,E,W))
        series_list_scrollbar.grid(column=1, row=0, sticky=(N,S))
        series_list_scrollbar.config(command=series_list.yview)

        title_entry = ttk.Entry(self, width=40, textvariable=self.sermon_title)
        speaker_combo = ttk.Combobox(self, width=40, textvariable=self.sermon_speaker)
        passage_entry = ttk.Entry(self, width=40, textvariable=self.sermon_passage)
        series_entry = ttk.Entry(self, width=40, textvariable=self.sermon_series)
        service_combo = ttk.Combobox(self, width=40, textvariable=self.sermon_service)
        date_entry = ttk.Entry(self, width=40, textvariable=self.sermon_date)
        directory_entry = ttk.Entry(self, width=40, textvariable=self.sermon_directory)

        #title_label = ttk.Label(self, text="Sermon title:")
        title_label = sermonsLabel(self, "Sermon title:", 1)
        speaker_label = sermonsLabel(self, "Speaker:", 2)
        passage_label = sermonsLabel(self, "Bible Passage (e.g. Mark 1:1-3:5):", 3)
        series_label = sermonsLabel(self, "Series:", 4)
        series_list_label = sermonsLabel(self, "Recent series:", 5)
        service_label = sermonsLabel(self, "Service:", 6)
        date_label = sermonsLabel(self, "Date:", 7)
        directory_label = sermonsLabel(self, "Directory:", 8)

        title_entry.grid(column=1, row=1, sticky=(E,W))
        speaker_combo.grid(column=1, row=2, sticky=(E,W))
        passage_entry.grid(column=1, row=3, sticky=(E,W))
        series_entry.grid(column=1, row=4, sticky=(E,W))
        series_list_container.grid(column=1, row=5, sticky=(N,S,E,W))
        service_combo.grid(column=1, row=6, sticky=(E,W))
        date_entry.grid(column=1, row=7, sticky=(E,W))
        directory_entry.grid(column=1, row=8, sticky=(E,W))

        self.columnconfigure(1, weight=1)
        

class Data:
    def __init__(self):
        pass

class Controller:
    pass

def main():
    root = Tk()
    app = EncoderUi(root)
    root.mainloop()
    pass

if __name__ == '__main__':
    main()

