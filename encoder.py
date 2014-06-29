#!/usr/bin/env python3

from datetime import date, datetime
import json
from macpath import split
import sqlite3
from tkinter import *
from tkinter import ttk, filedialog


class sermonsLabel(ttk.Label):
    def __init__(self, parent, text, row):
        self.parent = parent
        ttk.Label.__init__(self, parent, text=text)
        self.grid(column=0, row=row, sticky=(W), padx=4)


class EncoderUi(Frame):
    def __init__(self, model):
        self.root = Tk()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.minsize(500, 450)

        self.root.title("Sermon Encoder")

        self.parent = Frame(self.root)
        self.parent.grid(column=0, row=0, sticky=(N, S, E, W))
        self.parent.columnconfigure(0, weight=0)

        self.model = model
        self.controller = None

        self.actionSermonSelected = None

        Frame.__init__(self, self.parent, padx=6, pady=14)

        self.speaker = list()

        self.initUI()

    def initUI(self):
        self.grid(column=0, row=0, sticky=(N, S, E, W))
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.generateFilechooser()

        separator1 = ttk.Separator(self, orient=HORIZONTAL)
        separator1.grid(column=0, row=1, columnspan=2, sticky=(E, W), pady=6)

        self.generateFileInfoFields()

        separator2 = ttk.Separator(self, orient=HORIZONTAL)
        separator2.grid(column=0, row=10, columnspan=2, sticky=(E, W), pady=6)

        self.generateEncodingOptions()

        self.generateMenu()

        self.fillData()

        self.columnconfigure(1, weight=1)

    def generateFilechooser(self):
        self.targetFilename = StringVar()

        self.fileChooserText = ttk.Label(self, text="Input audio file")
        self.fileChooserFrame = Frame(self)
        self.fileChooserEntry = ttk.Entry(self.fileChooserFrame, width=40, textvariable=self.targetFilename)
        self.fileChooserButton = ttk.Button(self.fileChooserFrame, text="...", width=3, command=self.chooseFile)

        self.fileChooserFrame.configure(padx=2)

        self.fileChooserText.grid(column=0, row=0, sticky=(W))
        self.fileChooserFrame.grid(column=1, row=0, sticky=(E, W))
        self.fileChooserEntry.grid(column=0, row=0, sticky=(E, W), padx=4)
        self.fileChooserButton.grid(column=1, row=0, sticky=(E, W))

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
        series_list = Listbox(series_list_container, width=40, height=5, yscrollcommand=series_list_scrollbar.set,
                              listvariable=self.sermonSeriesRecent)
        series_list.grid(column=0, row=0, sticky=(N, S, E, W))
        series_list_scrollbar.grid(column=1, row=0, sticky=(N, S, E))
        series_list_scrollbar.config(command=series_list.yview)

        series_list.bind("<<ListboxSelect>>", self.selectedSeries)

        dateFrameContainer = Frame(self)
        dateFrameContainer.columnconfigure(0, minsize=40, weight=2)
        dateFrameContainer.columnconfigure(1, weight=1)
        dateFrameContainer.columnconfigure(2, minsize=50, weight=2)
        dateFrameContainer.columnconfigure(3, weight=1)
        dateFrameContainer.columnconfigure(4, minsize=35, weight=2)
        dateFrameContainer.columnconfigure(5, weight=1)
        dateYearLabel = Label(dateFrameContainer, text="Year:")
        dateYearSpinbox = Spinbox(dateFrameContainer, from_=date.today().year - 50, to=date.today().year + 50,
                                  textvariable=self.sermonDateYear)
        self.sermonDateYear.set(date.today().year)
        dateMonthLabel = Label(dateFrameContainer, text="Month:")
        dateMonthSpinbox = Spinbox(dateFrameContainer, from_=1, to=12, textvariable=self.sermonDateMonth)
        self.sermonDateMonth.set(date.today().month)
        dateDayLabel = Label(dateFrameContainer, text="Day:")
        dateDaySpinbox = Spinbox(dateFrameContainer, from_=1, to=31, textvariable=self.sermonDateDay)
        self.sermonDateDay.set(date.today().day)
        dateYearLabel.grid(column=0, row=0, padx=2, sticky=(E, W))
        dateYearSpinbox.grid(column=1, row=0, sticky=(E, W))
        dateMonthLabel.grid(column=2, row=0, padx=2, sticky=(E, W))
        dateMonthSpinbox.grid(column=3, row=0, sticky=(E, W))
        dateDayLabel.grid(column=4, row=0, padx=2, sticky=(E, W))
        dateDaySpinbox.grid(column=5, row=0, sticky=(E, W))

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
        directoryEntry.grid(column=0, row=0, sticky=(E, W), pady=3)
        directoryButton.grid(column=1, row=0, sticky=(E, W), padx=3)

        sermonsLabel(self, "Sermon title", 2)
        sermonsLabel(self, "Speaker", 3)
        sermonsLabel(self, "Bible Passage\n(e.g. Mark 1:1-3:5)", 4)
        sermonsLabel(self, "Series", 5)
        sermonsLabel(self, "Recent series", 6)
        sermonsLabel(self, "Service/Suffix", 7)
        sermonsLabel(self, "Date", 8)
        sermonsLabel(self, "Directory", 9)

        speaker_combo["values"] = ('Allan Blanch', 'Wayne Connor', 'David Ferres', 'Bryson Smith')
        service_combo["values"] = (
            '(Common) - No suffix', 'a - Early Church', 'b - Morning Church', 'c - Evening church',
            't - Tuesday Church')
        self.valuesService = ('', 'a', 'b', 'c', 't')
        service_combo.bind("<<ComboboxSelected>>",
                           lambda e: service_combo.set(self.valuesService[service_combo.current()]))

        title_entry.grid(column=1, row=2, sticky=(E, W), pady=3)
        speaker_combo.grid(column=1, row=3, sticky=(E, W), pady=3)
        passage_entry.grid(column=1, row=4, sticky=(E, W), pady=3)
        series_entry.grid(column=1, row=5, sticky=(E, W), pady=3)
        series_list_container.grid(column=1, row=6, sticky=(N, S, E, W), pady=3)
        service_combo.grid(column=1, row=7, sticky=(E, W), pady=3)
        dateFrameContainer.grid(column=1, row=8, pady=3)
        directoryFrameContainer.grid(column=1, row=9, sticky=(E, W), pady=3)

        self.titleEntry = title_entry
        self.speakerCombo = speaker_combo
        self.passageEntry = passage_entry
        self.seriesEntry = series_entry
        self.seriesList = series_list
        self.serviceCombo = service_combo
        self.date1Spinbox = dateYearSpinbox
        self.date2Spinbox = dateMonthSpinbox
        self.date3Spinbox = dateDaySpinbox
        self.directoryEntry = directoryEntry
        self.directoryButton = directoryButton

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
        #encodeOutputLabel = ttk.Label(self, text="Suffix")
        encode1Checkbox = ttk.Checkbutton(encodingOptionsContainer, text="Dialup MP3", variable=self.encode1,
                                          onvalue=True)
        encode2Checkbox = ttk.Checkbutton(encodingOptionsContainer, text="High Quality MP3", variable=self.encode2,
                                          onvalue=True)
        encode3Checkbox = ttk.Checkbutton(encodingOptionsContainer, text="Opus", variable=self.encode3, onvalue=True)
        #encodeOutputEntry = ttk.Entry(self, textvariable=self.outputSuffix)
        encodeButton = ttk.Button(self, text="Encode")

        encodingOptionsLabel.grid(column=0, row=11, sticky=(W))
        encode1Checkbox.grid(column=0, row=0, sticky=(E, W), padx=8)
        encode2Checkbox.grid(column=1, row=0, sticky=(E, W), padx=8)
        encode3Checkbox.grid(column=2, row=0, sticky=(E, W), padx=8)
        encodingOptionsContainer.grid(column=1, row=11, pady=5)
        #encodeOutputLabel.grid(column=0, row=12, sticky=(W))
        #encodeOutputEntry.grid(column=1, row=12, sticky=(E,W))
        encodeButton.grid(column=1, row=13, sticky=(E, W), padx=10, pady=15)

        self.encode1Checkbox = encode1Checkbox
        self.encode2Checkbox = encode2Checkbox
        self.encode3Checkbox = encode3Checkbox
        #self.suffixEntry = encodeOutputEntry
        self.encodeButton = encodeButton

        self.encode1.set(True)
        self.encode2.set(True)
        self.encode3.set(True)

    def generateMenu(self):
        self.root.option_add("*tearOff", FALSE)

        menuBar = Menu(self.root)
        self.root['menu'] = menuBar

        apple = Menu(menuBar, name="apple")

        if self.root.tk.call("tk", "windowingsystem") != "aqua":
            menuBar.add_cascade(menu=apple, label="Program")

            apple.add_command(label="Options", command=self.openOptionsWindow)
            apple.add_command(label="Exit", command=self.exitApp)
        else:
            self.root.createcommand("::tk::mac::ShowPreferences", self.openOptionsWindowOSX)

    def fillData(self):
        recentSeries = self.model.getRecentSeries()
        self.sermonSeriesRecentVar = recentSeries
        self.sermonSeriesRecent = StringVar(value=self.sermonSeriesRecentVar)
        self.seriesList.configure(listvariable=self.sermonSeriesRecent)

    def chooseFile(self):
        filename = filedialog.askopenfilename(
            filetypes=(("Lossless audio", "*.flac *.wav *.aiff;"), ("Lossy audio", "*.opus *.ogg *.mp3")))
        self.targetFilename.set(filename)

    def chooseDirectory(self):
        directoryName = filedialog.askdirectory()
        self.sermonDirectory.set(directoryName)

    def openOptionsWindow(self):
        pass

    def openOptionsWindowOSX(event=None):
        pass

    def exitApp(self):
        self.root.quit()

    def setEncodeAction(self, action):
        self.encodeButton.configure(command=action)

    def setSelectSeriesAction(self, action):
        self.actionSermonSelected = action

    def disableFields(self):
        self.fileChooserEntry.configure(state="disabled")
        self.fileChooserButton.configure(state="disabled")
        self.titleEntry.configure(state="disabled")
        self.speakerCombo.configure(state="disabled")
        self.passageEntry.configure(state="disabled")
        self.seriesEntry.configure(state="disabled")
        self.seriesList.configure(state="disabled")
        self.serviceCombo.configure(state="disabled")
        self.date1Spinbox.configure(state="disabled")
        self.date2Spinbox.configure(state="disabled")
        self.date3Spinbox.configure(state="disabled")
        self.directoryEntry.configure(state="disabled")
        self.directoryButton.configure(state="disabled")
        self.encode1Checkbox.configure(state="disabled")
        self.encode2Checkbox.configure(state="disabled")
        self.encode3Checkbox.configure(state="disabled")
        #self.suffixEntry.configure(state="disabled")
        self.encodeButton.configure(state="disabled")

    def enableFields(self):
        self.fileChooserEntry.configure(state="normal")
        self.fileChooserButton.configure(state="normal")
        self.titleEntry.configure(state="normal")
        self.speakerCombo.configure(state="normal")
        self.passageEntry.configure(state="normal")
        self.seriesEntry.configure(state="normal")
        self.seriesList.configure(state="normal")
        self.serviceCombo.configure(state="normal")
        self.date1Spinbox.configure(state="normal")
        self.date2Spinbox.configure(state="normal")
        self.date3Spinbox.configure(state="normal")
        self.directoryEntry.configure(state="normal")
        self.directoryButton.configure(state="normal")
        self.encode1Checkbox.configure(state="normal")
        self.encode2Checkbox.configure(state="normal")
        self.encode3Checkbox.configure(state="normal")
        #self.suffixEntry.configure(state="normal")
        self.encodeButton.configure(state="normal")

    def selectedSeries(self, arg):
        selectedId = int(self.seriesList.curselection()[0])
        selectedName = self.sermonSeriesRecentVar[selectedId]
        self.actionSermonSelected(selectedName)

    def setSeries(self, speaker, name, service, directory):
        self.sermonSpeaker.set(speaker)
        self.sermonSeries.set(name)
        self.sermonService.set(service)
        self.sermonDirectory.set(directory)


class Data:
    def __init__(self):
        self.setupDatabase()
        self.setupOptionsText()
        pass

    def setupDatabase(self):
        self.conn = sqlite3.connect("history.db", detect_types=sqlite3.PARSE_DECLTYPES)

        cur = self.conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS series(
            seriesName TEXT PRIMARY KEY ON CONFLICT REPLACE UNIQUE NOT NULL,
            used TIMESTAMP NOT NULL,
            speaker TEXT NOT NULL,
            service TEXT NOT NULL,
            directory TEXT NOT NULL
        )''')
        self.conn.commit()

    def setupOptionsText(self):
        self.optionsFilename = "encodeOpts.conf"
        optsString = ""
        try:
            with open(self.optionsFilename) as f:
                optsString = f.readlines()

        except FileNotFoundError:
            optsString = '{"lq": {"program": "lame", "options": ""},' \
                ' "hq": {"program": "lame", "options": ""},' \
                ' "opus": {"program": "opusenc", "options": ""},' \
                ' "albumTitle": "DPC Bible Talks"}'

        self.encodingOptions = json.loads(optsString)
        json.dump(self.encodingOptions, self.optionsFilename, indent=4, sort_keys=True)

    def getEncodingOptions(self, quality):
        return self.encodingOptions[quality]

    def setEncodingProgram(self, quality, program):
        self.encodingOptions[quality]["program"] = program

    def setEncodingOptions(self, quality, options):
        self.encodingOptions[quality]["options"] = options

    def getSpeakers(self, searchTerm):
        #stub
        return ("Alice", "Bob", "Carol")

    def getRecentSeries(self):
        cur = self.conn.cursor()
        cur.execute("SELECT seriesName FROM series")
        rows = cur.fetchall()
        return tuple([row[0] for row in rows])

    def insertSeries(self, name, speaker, service, directory):
        cur = self.conn.cursor()
        today = datetime.now()
        cur.execute("INSERT INTO series(seriesName, used, speaker, service, directory) VALUES(?,?,?,?,?)",
                    (name, today, speaker, service, directory))
        self.conn.commit()

    def selectSeries(self, seriesName):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM series WHERE seriesName=?", (seriesName,))
        return cur.fetchone()


class Controller:
    def __init__(self, view, model):
        self.view = view
        self.model = model

    def encode(self):
        self.view.disableFields()
        self.model.insertSeries(self.view.sermonSeries.get(), self.view.sermonSpeaker.get(),
                                self.view.sermonService.get(), self.view.sermonDirectory.get())
        self.view.enableFields()

    def seriesSelected(self, seriesName):
        seriesRecord = self.model.selectSeries(seriesName)
        self.view.setSeries(seriesRecord[2], seriesRecord[0], seriesRecord[3], seriesRecord[4])

    def updateProgressBar(self):
        pass

    def encodeMp3(self, inputFile, outputFile, args, tags):
        programName = "lame"
        programArgs = "%s %s %s --tt %s --ta %s --tl %s --tc %s" % (
            args,
            inputFile,
            outputFile,
            tags["sermonName"],
            tags["speaker"],
            tags["albumTitle"],
            tags["comment"]
        )

        splitArgs = programArgs.split(" ")
        cmd = [programName] + splitArgs




def main():
    data = Data()
    gui = EncoderUi(data)
    controller = Controller(gui, data)
    gui.setEncodeAction(controller.encode)
    gui.setSelectSeriesAction(controller.seriesSelected)

    gui.root.mainloop()

    pass


if __name__ == '__main__':
    main()

