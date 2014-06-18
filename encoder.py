#!/usr/bin/env python3

from datetime import date
from tkinter import *
from tkinter import ttk, filedialog


class sermonsLabel(ttk.Label):
    def __init__(self, parent, text, row):
        self.parent = parent
        ttk.Label.__init__(self, parent, text=text)
        self.grid(column=0, row=row, sticky=(W), padx=4)

class EncoderUi(Frame):
    def __init__(self):
        self.root = Tk()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.minsize(500, 450)

        Frame.__init__(self, self.root, padx=6, pady=14)

        self.parent = self.root

        self.speaker = list()

        self.initUI()

        self.root.mainloop()

    def initUI(self):
        self.parent.title("Sermon Encoder")
        self.grid(column=0, row=0, sticky=(N,S,E,W))
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.generateFilechooser()

        separator1 = ttk.Separator(self, orient=HORIZONTAL)
        separator1.grid(column=0, row=1, columnspan=2, sticky=(E,W), pady=6)

        self.generateFileInfoFields()

        separator2 = ttk.Separator(self, orient=HORIZONTAL)
        separator2.grid(column=0, row=10, columnspan=2, sticky=(E,W), pady=6)

        self.generateEncodingOptions()

        self.columnconfigure(1, weight=1)

    def generateFilechooser(self):
        self.targetFilename = StringVar()

        self.fileChooserText = ttk.Label(self, text="Input audio file")
        self.fileChooserFrame = Frame(self)
        self.fileChooserEntry = ttk.Entry(self.fileChooserFrame, width=40, textvariable=self.targetFilename)
        self.fileChooserButton = ttk.Button(self.fileChooserFrame, text="...", width=3, command=self.chooseFile)

        self.fileChooserFrame.configure(padx=2)

        self.fileChooserText.grid(column=0, row=0, sticky=(W))
        self.fileChooserFrame.grid(column=1, row=0, sticky=(E,W))
        self.fileChooserEntry.grid(column=0, row=0, sticky=(E,W), padx=4)
        self.fileChooserButton.grid(column=1, row=0, sticky=(E,W))

        self.fileChooserFrame.columnconfigure(0, weight=1)

    def generateFileInfoFields(self):
        self.sermonTitle = StringVar()
        self.sermonSpeaker = StringVar()
        self.sermonPassage = StringVar()
        self.sermonSeries = StringVar()
        self.sermonSeriesRecentVar = None
        self.sermonSeriesRecent = StringVar()
        self.sermonService = StringVar()
        self.sermonDateYear = IntVar()
        self.sermonDateMonth = IntVar()
        self.sermonDateDay = IntVar()
        self.sermonDirectory = StringVar()

        series_list_container = Frame(self)
        series_list_container.columnconfigure(0, weight=1)
        series_list_container.rowconfigure(0, weight=1)
        series_list_scrollbar = Scrollbar(series_list_container)
        series_list = Listbox(series_list_container, width=40, height=5, yscrollcommand=series_list_scrollbar.set, listvariable=self.sermonSeriesRecent)
        series_list.grid(column=0, row=0, sticky=(N,S,E,W))
        series_list_scrollbar.grid(column=1, row=0, sticky=(N,S,E))
        series_list_scrollbar.config(command=series_list.yview)

        dateFrameContainer = Frame(self)
        dateFrameContainer.columnconfigure(0, minsize=40, weight=2)
        dateFrameContainer.columnconfigure(1, weight=1)
        dateFrameContainer.columnconfigure(2, minsize=50, weight=2)
        dateFrameContainer.columnconfigure(3, weight=1)
        dateFrameContainer.columnconfigure(4, minsize=35, weight=2)
        dateFrameContainer.columnconfigure(5, weight=1)
        dateYearLabel = Label(dateFrameContainer, text="Year:")
        dateYearSpinbox = Spinbox(dateFrameContainer, from_=date.today().year - 50, to=date.today().year + 50, textvariable=self.sermonDateYear)
        self.sermonDateYear.set(date.today().year)
        dateMonthLabel = Label(dateFrameContainer, text="Month:")
        dateMonthSpinbox = Spinbox(dateFrameContainer, from_=1, to=12, textvariable=self.sermonDateMonth)
        self.sermonDateMonth.set(date.today().month)
        dateDayLabel = Label(dateFrameContainer, text="Day:")
        dateDaySpinbox = Spinbox(dateFrameContainer, from_=1, to=31, textvariable=self.sermonDateDay)
        self.sermonDateDay.set(date.today().day)
        dateYearLabel.grid(column=0, row=0, padx=2, sticky=(E,W))
        dateYearSpinbox.grid(column=1, row=0, sticky=(E,W))
        dateMonthLabel.grid(column=2, row=0, padx=2, sticky=(E,W))
        dateMonthSpinbox.grid(column=3, row=0, sticky=(E,W))
        dateDayLabel.grid(column=4, row=0, padx=2, sticky=(E,W))
        dateDaySpinbox.grid(column=5, row=0, sticky=(E,W))

        title_entry = ttk.Entry(self, width=40, textvariable=self.sermonTitle)
        speaker_combo = ttk.Combobox(self, width=40, textvariable=self.sermonSpeaker)
        passage_entry = ttk.Entry(self, width=40, textvariable=self.sermonPassage)
        series_entry = ttk.Entry(self, width=40, textvariable=self.sermonSeries)
        service_combo = ttk.Combobox(self, width=40, textvariable=self.sermonService)

        directoryFrameContainer = Frame(self)
        directoryFrameContainer.columnconfigure(0, weight=1)
        directoryFrameContainer.rowconfigure(0, weight=1)
        directoryEntry = ttk.Entry(directoryFrameContainer, width=40, textvariable=self.sermonDirectory)
        directoryButton = ttk.Button(directoryFrameContainer, text="...", width=3, command=self.chooseDirectory)
        directoryEntry.grid(column=0, row=0, sticky=(E,W), pady=3)
        directoryButton.grid(column=1, row=0, sticky=(E,W), padx=3)

        sermonsLabel(self, "Sermon title", 2)
        sermonsLabel(self, "Speaker", 3)
        sermonsLabel(self, "Bible Passage\n(e.g. Mark 1:1-3:5)", 4)
        sermonsLabel(self, "Series", 5)
        sermonsLabel(self, "Recent series", 6)
        sermonsLabel(self, "Service", 7)
        sermonsLabel(self, "Date", 8)
        sermonsLabel(self, "Directory", 9)

        title_entry.grid(column=1, row=2, sticky=(E,W), pady=3)
        speaker_combo.grid(column=1, row=3, sticky=(E,W), pady=3)
        passage_entry.grid(column=1, row=4, sticky=(E,W), pady=3)
        series_entry.grid(column=1, row=5, sticky=(E,W), pady=3)
        series_list_container.grid(column=1, row=6, sticky=(N,S,E,W), pady=3)
        service_combo.grid(column=1, row=7, sticky=(E,W), pady=3)
        dateFrameContainer.grid(column=1, row=8, pady=3)
        directoryFrameContainer.grid(column=1, row=9, sticky=(E,W), pady=3)

    def generateEncodingOptions(self):
        self.encode1 = BooleanVar()
        self.encode2 = BooleanVar()
        self.encode3 = BooleanVar()
        self.outputSuffix = StringVar()

        encodingOptionsContainer = Frame(self)
        encodingOptionsContainer.columnconfigure(0, weight=1, minsize=120)
        encodingOptionsContainer.columnconfigure(1, weight=1, minsize=140)
        encodingOptionsContainer.columnconfigure(2, weight=1, minsize=80)

        encodingOptionsLabel = ttk.Label(self, text="Enable")
        encodeOutputLabel = ttk.Label(self, text="Suffix")
        encode1Checkbox = ttk.Checkbutton(encodingOptionsContainer, text="Dialup MP3", variable=self.encode1, onvalue=True)
        encode2Checkbox = ttk.Checkbutton(encodingOptionsContainer, text="High Quality MP3", variable=self.encode2, onvalue=True)
        encode3Checkbox = ttk.Checkbutton(encodingOptionsContainer, text="Opus", variable=self.encode3, onvalue=True)
        encodeOutputEntry = ttk.Entry(self, textvariable=self.outputSuffix)
        encodeButton = ttk.Button(self, text="Encode", command=Controller.encode)

        encodingOptionsLabel.grid(column=0, row=11, sticky=(W))
        encode1Checkbox.grid(column=0, row=0, sticky=(E,W), padx=8)
        encode2Checkbox.grid(column=1, row=0, sticky=(E,W), padx=8)
        encode3Checkbox.grid(column=2, row=0, sticky=(E,W), padx=8)
        encodingOptionsContainer.grid(column=1, row=11, pady=5)
        encodeOutputLabel.grid(column=0, row=12, sticky=(W))
        encodeOutputEntry.grid(column=1, row=12, sticky=(E,W))
        encodeButton.grid(column=1, row=13, sticky=(E,W), padx = 10, pady=15)


        self.encode1.set(True)
        self.encode2.set(True)
        self.encode3.set(True)

    def chooseFile(self):
        filename = filedialog.askopenfilename(filetypes=(("Lossless audio", "*.flac *.wav *.aiff;"),("Lossy audio", "*.opus *.ogg *.mp3")))
        self.targetFilename.set(filename)

    def chooseDirectory(self):
        directoryName = filedialog.askdirectory()
        self.sermonDirectory = directoryName


class Data:
    def __init__(self):
        pass

    def getSpeakers(self, searchTerm):
        #stub
        return ("Alice", "Bob", "Carol")

class Controller:
    def encode(self):
        pass

def main():
    app = EncoderUi()
    pass

if __name__ == '__main__':
    main()

