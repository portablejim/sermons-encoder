#!/usr/bin/env python3

from datetime import date, datetime
import json
import os
from os.path import dirname, realpath
import platform
import shlex
import shutil
import sqlite3
import subprocess
import threading
from time import sleep
from tkinter import *
from tkinter import ttk, filedialog, messagebox

PROGRAMNAME = "sermonsEncoder"


class STATUS:
    READY = 0
    ENCODING_1 = 10
    ENCODING_2 = 11


class sermonsLabel(ttk.Label):
    def __init__(self, parent, text, row):
        self.parent = parent
        ttk.Label.__init__(self, parent, text=text)
        self.grid(column=0, row=row, sticky=W, padx=4)


class EncoderUi(ttk.Frame):
    def __init__(self, model):
        self.root = Tk()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.minsize(500, 490)

        binPath = dirname(realpath(__file__))
        iconPath = os.path.join(binPath, "../icon/icon.gif")
        if os.path.exists(iconPath):
            img = PhotoImage(file=iconPath)
            self.root.tk.call('wm', 'iconphoto', self.root._w, img)

        self.root.title("Sermon Encoder")

        self.parent = ttk.Frame(self.root)
        self.parent.grid(column=0, row=0, sticky=(N, S, E, W))
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

        self.model = model
        self.controller = None

        self.actionSermonSelected = None

        ttk.Frame.__init__(self, self.parent, padding=(6,6,14,14))

        self.speaker = list()

        self.status = STATUS.READY
        self.statusUpdate = False
        self.root.after(100, self.monitor)

        self.initUI()

    def initUI(self):
        self.grid(column=0, row=0, sticky=(N, S, E, W))
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(6, weight=1)

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
        self.fileChooserFrame = ttk.Frame(self)
        self.fileChooserEntry = ttk.Entry(self.fileChooserFrame, width=40, textvariable=self.targetFilename)
        self.fileChooserButton = ttk.Button(self.fileChooserFrame, text="...", width=3, command=self.chooseFile)

        self.fileChooserFrame.configure(padding=(2,2,0,0))

        self.fileChooserText.grid(column=0, row=0, sticky=W)
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

        series_list_container = ttk.Frame(self)
        series_list_container.columnconfigure(0, weight=1)
        series_list_container.rowconfigure(0, weight=1)
        series_list_scrollbar = Scrollbar(series_list_container)
        series_list = Listbox(series_list_container, width=40, height=5, yscrollcommand=series_list_scrollbar.set,
                              listvariable=self.sermonSeriesRecent)
        series_list.grid(column=0, row=0, sticky=(N, S, E, W))
        series_list_scrollbar.grid(column=1, row=0, sticky=(N, S, E))
        series_list_scrollbar.config(command=series_list.yview)

        series_list.bind("<<ListboxSelect>>", self.selectedSeries)

        dateFrameContainer = ttk.Frame(self)
        dateFrameContainer.columnconfigure(0, minsize=40, weight=2)
        dateFrameContainer.columnconfigure(1, weight=1)
        dateFrameContainer.columnconfigure(2, minsize=50, weight=2)
        dateFrameContainer.columnconfigure(3, weight=1)
        dateFrameContainer.columnconfigure(4, minsize=35, weight=2)
        dateFrameContainer.columnconfigure(5, weight=1)
        dateYearLabel = ttk.Label(dateFrameContainer, text="Year:")
        dateYearSpinbox = Spinbox(dateFrameContainer, from_=date.today().year - 50, to=date.today().year + 50,
                                  textvariable=self.sermonDateYear)
        self.sermonDateYear.set(date.today().year)
        dateMonthLabel = ttk.Label(dateFrameContainer, text="Month:")
        dateMonthSpinbox = Spinbox(dateFrameContainer, from_=1, to=12, textvariable=self.sermonDateMonth)
        self.sermonDateMonth.set(date.today().month)
        dateDayLabel = ttk.Label(dateFrameContainer, text="Day:")
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

        directoryFrameContainer = ttk.Frame(self)
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

        encodingOptionsContainer = ttk.Frame(self)
        encodingOptionsContainer.columnconfigure(0, weight=1, minsize=120)
        encodingOptionsContainer.columnconfigure(1, weight=1, minsize=140)
        encodingOptionsContainer.columnconfigure(2, weight=1, minsize=80)

        encodingOptionsLabel = ttk.Label(self, text="Enable")
        encode1Checkbox = ttk.Checkbutton(encodingOptionsContainer, text="Dialup MP3", variable=self.encode1,
                                          onvalue=True)
        encode2Checkbox = ttk.Checkbutton(encodingOptionsContainer, text="High Quality MP3", variable=self.encode2,
                                          onvalue=True)
        encode3Checkbox = ttk.Checkbutton(encodingOptionsContainer, text="Opus", variable=self.encode3, onvalue=True)
        encodeButton = ttk.Button(self, text="Encode")
        progressText = ttk.Label(self, anchor="center", padding="0 0 0 5")
        progressBar = ttk.Progressbar(self, mode="indeterminate")

        encodingOptionsLabel.grid(column=0, row=11, sticky=W)
        encode1Checkbox.grid(column=0, row=0, sticky=(E, W), padx=8)
        encode2Checkbox.grid(column=1, row=0, sticky=(E, W), padx=8)
        encode3Checkbox.grid(column=2, row=0, sticky=(E, W), padx=8)
        encodingOptionsContainer.grid(column=1, row=11, pady=5)
        encodeButton.grid(column=1, row=13, sticky=(E, W), padx=10, pady=15)
        progressText.grid(column=1, row=15, sticky=(E, W))
        progressBar.grid(column=1, row=16, sticky=(E, W))

        self.encode1Checkbox = encode1Checkbox
        self.encode2Checkbox = encode2Checkbox
        self.encode3Checkbox = encode3Checkbox
        #self.suffixEntry = encodeOutputEntry
        self.encodeButton = encodeButton
        self.encodeProgressText = progressText
        self.encodeProgressBar = progressBar

        self.hideProgress()

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

    def generateOptions(self):
        window = Toplevel(self)
        window.columnconfigure(0, weight=1)
        window.transient(self.root)
        window.title("Sermon Encoder Options")
        frame = ttk.Frame(window)
        frame.columnconfigure(2, weight=1)

        sermonsLabel(frame, "Low quality MP3 options", 0)
        sermonsLabel(frame, "High quality MP3 options", 1)
        sermonsLabel(frame, "Opus options", 2)

        self.lqOptionsProgram = StringVar()
        self.lqOptionsOptions = StringVar()
        self.hqOptionsProgram = StringVar()
        self.hqOptionsOptions = StringVar()
        self.opusOptionsProgram = StringVar()
        self.opusOptionsOptions = StringVar()

        self.comboboxLqOptionsProgram = ttk.Combobox(frame, textvariable=self.lqOptionsProgram, width=8)
        self.comboboxHqOptionsProgram = ttk.Combobox(frame, textvariable=self.hqOptionsProgram, width=8)
        self.comboboxOpusOptionsProgram = ttk.Combobox(frame, textvariable=self.opusOptionsProgram, width=8)
        self.entryLqOptionsOptions = ttk.Entry(frame, textvariable=self.lqOptionsOptions)
        self.entryHqOptionsOptions = ttk.Entry(frame, textvariable=self.hqOptionsOptions)
        self.entryOpusOptionsOptions = ttk.Entry(frame, textvariable=self.opusOptionsOptions)
        self.buttonSaveOptions = ttk.Button(frame, text="Save", command=self.saveOptions)

        # TODO: When I code ffmpeg and opusenc
        # programValues = ("ffmpeg", "lame", "oggenc", "opusenc")
        programValues = ("lame", "opusenc")
        self.comboboxLqOptionsProgram["values"] = programValues
        self.comboboxHqOptionsProgram["values"] = programValues
        self.comboboxOpusOptionsProgram["values"] = programValues
        self.comboboxLqOptionsProgram.configure(state="readonly")
        self.comboboxHqOptionsProgram.configure(state="readonly")
        self.comboboxOpusOptionsProgram.configure(state="readonly")
        self.lqOptionsProgram.set(self.model.getEncodingOptions("lq")["program"])
        self.hqOptionsProgram.set(self.model.getEncodingOptions("hq")["program"])
        self.opusOptionsProgram.set(self.model.getEncodingOptions("opus")["program"])
        self.lqOptionsOptions.set(self.model.getEncodingOptions("lq")["options"])
        self.hqOptionsOptions.set(self.model.getEncodingOptions("hq")["options"])
        self.opusOptionsOptions.set(self.model.getEncodingOptions("opus")["options"])

        frame.grid(column=0, row=0, padx=8, pady=8, sticky=(N, E, S, W))
        self.comboboxLqOptionsProgram.grid(column=1, row=0)
        self.comboboxHqOptionsProgram.grid(column=1, row=1)
        self.comboboxOpusOptionsProgram.grid(column=1, row=2)
        self.entryLqOptionsOptions.grid(column=2, row=0, sticky=(E, W))
        self.entryHqOptionsOptions.grid(column=2, row=1, sticky=(E, W))
        self.entryOpusOptionsOptions.grid(column=2, row=2, sticky=(E, W))
        self.buttonSaveOptions.grid(column=2, row=3, sticky=E, pady=3)

        self.optionsWindow = window

    def fillData(self):
        recentSeries = self.model.getRecentSeries()
        self.sermonSeriesRecentVar = recentSeries
        self.sermonSeriesRecent = StringVar(value=self.sermonSeriesRecentVar)
        self.seriesList.configure(listvariable=self.sermonSeriesRecent)

    def chooseFile(self):
        lastdir = self.model.getLatestInputDirectory()
        if lastdir == "" or not os.path.isdir(lastdir):
            lastdir = os.path.expanduser("~")

        filename = filedialog.askopenfilename(
            filetypes=(("Lossless audio", "*.flac *.wav *.aiff;"), ("Lossy audio", "*.opus *.ogg *.mp3")),
            initialdir=lastdir,
            parent=self)
        self.targetFilename.set(filename)

    def chooseDirectory(self):
        directoryName = filedialog.askdirectory(parent=self, initialdir=self.sermonDirectory.get())
        if directoryName != "":
            self.sermonDirectory.set(directoryName)

    def openOptionsWindow(self):
        self.generateOptions()
        pass

    def openOptionsWindowOSX(self):
        self.generateOptions()
        pass

    def saveOptions(self):
        self.optionSaveAction()
        self.buttonSaveOptions.configure(state="disabled")
        sleep(0.5)
        self.optionsWindow.destroy()
        pass

    def exitApp(self):
        self.root.quit()

    def setEncodeAction(self, action):
        self.encodeButton.configure(command=action)

    def setSelectSeriesAction(self, action):
        self.actionSermonSelected = action

    def setOptionSaveAction(self, action):
        self.optionSaveAction = action

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

    def hideProgress(self):
        self.encodeProgressText.grid_remove()
        self.encodeProgressBar.grid_remove()

    def showProgress(self):
        self.encodeProgressText.grid()
        self.encodeProgressBar.grid()

    # noinspection PyUnusedLocal
    def selectedSeries(self, unused):
        if len(self.seriesList.curselection()) > 0:
            selectedId = int(self.seriesList.curselection()[0])
            selectedName = self.sermonSeriesRecentVar[selectedId]
            self.actionSermonSelected(selectedName)

    def setSeries(self, speaker, name, service, directory):
        self.sermonSpeaker.set(speaker)
        self.sermonSeries.set(name)
        self.sermonService.set(service)
        self.sermonDirectory.set(directory)

    def setDirectory(self, path):
        self.sermonDirectory.set(path)

    def monitor(self):
        if self.statusUpdate:
            if self.status == STATUS.READY:
                self.enableFields()
                self.encodeProgressBar.stop()
                self.hideProgress()
            elif self.status == STATUS.ENCODING_1:
                self.disableFields()
                self.encodeProgressText.configure(text="Decoding input file")
                self.encodeProgressBar.start(1)
                self.showProgress()
            elif self.status == STATUS.ENCODING_2:
                self.encodeProgressText.configure(text="Encoding output files")
                self.encodeProgressBar.stop()
                self.encodeProgressBar.start(50)
            self.statusUpdate = False
        self.root.after(100, self.monitor)


class Data:
    def __init__(self):
        self.setupPaths()
        self.setupDatabase()
        self.setupOptionsText()
        self.setupProgramPaths()

        self.encodingResult = {"hq": -1, "lq": -1, "opus": -1}

    def setupPaths(self):
        system = platform.system()
        binPath = dirname(realpath(__file__))
        self.settingsPath = os.path.join(binPath, "..")
        if system == "Linux":
            self.settingsPath = os.path.join(os.path.expanduser("~"), ".config", PROGRAMNAME)
        elif system == "Darwin":
            self.settingsPath = os.path.join(os.path.expanduser("~"), "Library", "Application Support", PROGRAMNAME)
        elif system == "Windows":
            self.settingsPath = os.path.join(os.environ["APPDATA"], PROGRAMNAME)

        print("Using settings path: ", self.settingsPath, file=sys.stderr)
        if not os.path.exists(self.settingsPath):
            os.makedirs(self.settingsPath)


    def setupDatabase(self):
        dbPath = os.path.join(self.settingsPath, "history.db")
        self.conn = sqlite3.connect(dbPath, detect_types=sqlite3.PARSE_DECLTYPES)

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
        self.optionsPath = os.path.join(self.settingsPath, self.optionsFilename)
        try:
            with open(self.optionsPath) as f:
                optsString = " ".join(f.readlines())

        except FileNotFoundError:
            optsString = '{"lq": {"program": "lame", "options": ""},' \
                         ' "hq": {"program": "lame", "options": ""},' \
                         ' "opus": {"program": "opusenc", "options": ""},' \
                         ' "albumTitle": "DPC Bible Talks"}'

        self.encodingOptions = json.loads(optsString)
        self.saveOptions()

    def setupProgramPaths(self):
        self.pathsPath = os.path.join(self.settingsPath, "paths.json")
        pathsString = '{\n' \
                     '"autodetectPaths": true,\n' \
                     '"programPaths": {\n' \
                     '    "ffmpeg": "ffmpeg",\n' \
                     '    "lame": "lame",\n' \
                     '    "opusenc": "opusenc",\n' \
                     '    "oggenc": "oggenc"\n' \
                     '},\n' \
                     ' "lastPath": ""' \
                     '}'
        if not os.path.exists(self.pathsPath):
            try:
                with open(self.pathsPath, 'w') as f:
                    f.writelines(pathsString)
            except:
                pass


        try:
            with open(self.pathsPath) as f:
                pathsString = " ".join(f.readlines())
        except FileNotFoundError:
            pass

        self.programPaths = json.loads(pathsString)
        self.saveProgramPaths()


    def saveOptions(self):
        with open(self.optionsPath, mode="w") as f:
            json.dump(self.encodingOptions, f, indent=4, sort_keys=True)

    def saveProgramPaths(self):
        with open(self.pathsPath, mode="w") as f:
            json.dump(self.programPaths, f, indent=4, sort_keys=True)

    def getEncodingOptions(self, quality):
        return self.encodingOptions[quality]

    def setEncodingProgram(self, quality, program):
        self.encodingOptions[quality]["program"] = program
        self.saveOptions()

    def setEncodingOptions(self, quality, options):
        self.encodingOptions[quality]["options"] = options
        self.saveOptions()

    def getLatestInputDirectory(self):
        return self.programPaths["latestPath"]

    def setLatestInputDirectory(self, directory):
        self.programPaths["latestPath"] = directory
        self.saveProgramPaths()

    def getRecentSeries(self):
        cur = self.conn.cursor()
        cur.execute("SELECT seriesName FROM series ORDER BY used DESC LIMIT 10")
        rows = cur.fetchall()
        return tuple([row[0] for row in rows])

    def getLatestDirectory(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT directory FROM series ORDER BY used DESC LIMIT 1")
            rows = cur.fetchall()
            return rows[0][0]
        except:
            return ""

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

    def getProgram(self, name):
        if self.programPaths["autodetectPaths"]:
            if name == "ffmpeg":
                hasFfmpeg = shutil.which('ffmpeg') is not None
                if hasFfmpeg:
                    return "ffmpeg"
                else:
                    hasLibav = shutil.which('avconv') is not None
                    if hasLibav:
                        return "avconv"

            if shutil.which(name) is not None:
                return name

        # If autodetect fails or is turned off, attempt to get program path.
        if name in self.programPaths["programPaths"]:
            return self.programPaths["programPaths"][name]

        # Else just return what we are sent
        return name



class Controller:
    def __init__(self, view, model):
        self.view = view
        self.model = model

    def prefillForm(self):
        dirName = self.model.getLatestDirectory().strip()
        if dirName == "" or not os.path.exists(dirName):
            dirName = os.path.expanduser("~")

        self.view.setDirectory(dirName)

    def encode(self):
        #self.view.after(self.monitor())

        targetPath = os.path.join(self.view.sermonDirectory.get(), "dial")
        if not os.path.exists(targetPath):
            os.mkdir(targetPath)

        inputFile = self.view.targetFilename.get().strip()
        title = self.view.sermonTitle.get().strip()
        speaker = self.view.sermonSpeaker.get().strip()
        series = self.view.sermonSeries.get().strip()
        directory = self.view.sermonDirectory.get().strip()

        if inputFile == "" or not os.path.exists(inputFile) or os.path.isdir(inputFile):
            messagebox.showerror("Invalid input audio file",
                                 "The input audio file path is missing or invalid."
                                 + "Please input a valid file path.")
            return

        if title == "" or speaker == "" or series == "" or directory == "":
            messagebox.showerror("Incomplete Info",
                                 "Please fill out the title, speaker, series and directory before encoding.")
            return

        if not os.path.exists(directory) or not os.path.isdir(directory):
            messagebox.showerror("Invalid output directory",
                                 "Please specify a valid directory to output the audio files to."
                                 + "You will need write access to the directory for encoding to succeed.")
            return

        self.model.insertSeries(self.view.sermonSeries.get(), self.view.sermonSpeaker.get(),
                                self.view.sermonService.get(), self.view.sermonDirectory.get())

        inputDirectory = os.path.dirname(inputFile)
        self.model.setLatestInputDirectory(inputDirectory)

        if os.path.exists(self.view.targetFilename.get()):
            threading.Thread(target=self.encodeAllFiles).start()

    def seriesSelected(self, seriesName):
        seriesRecord = self.model.selectSeries(seriesName)
        self.view.setSeries(seriesRecord[2], seriesRecord[0], seriesRecord[3], seriesRecord[4])

    def encodeAllFiles(self):
        self.view.status = STATUS.ENCODING_1
        self.view.statusUpdate = True

        rawWav = self.fileToRam(self.view.targetFilename.get())

        self.view.status = STATUS.ENCODING_2
        self.view.statusUpdate = True

        targetDate = "%04d%02d%02d" % (
            self.view.sermonDateYear.get(), self.view.sermonDateMonth.get(), self.view.sermonDateDay.get())
        suffix = ""
        if self.view.sermonService.get().strip() != "":
            suffix = "-" + self.view.sermonService.get()
        filename = "%s%s" % (targetDate, suffix)
        comment = "%s %s %s" % (self.view.sermonPassage.get(), targetDate, self.view.sermonSeries.get())
        metadata = {"sermonName": self.view.sermonTitle.get(), "speaker": self.view.sermonSpeaker.get(),
                    "albumTitle": self.view.sermonSeries.get(), "comment": comment}

        commandLookup = {"lame": self.encodeLame, "opusenc": self.encodeOpus}

        thread1 = threading.Thread()
        thread2 = threading.Thread()
        thread3 = threading.Thread()
        if self.view.encode1.get():
            thread1 = threading.Thread(target=commandLookup[self.model.getEncodingOptions("lq")["program"]],
                                       args=("-",
                                             os.path.join(self.view.sermonDirectory.get(), "dial", "%s.mp3" % filename),
                                             self.model.getEncodingOptions("lq")["options"],
                                             metadata,
                                             rawWav,
                                             "lq"))
        if self.view.encode2.get():
            thread2 = threading.Thread(target=commandLookup[self.model.getEncodingOptions("lq")["program"]],
                                       args=("-",
                                             os.path.join(self.view.sermonDirectory.get(), "%s.mp3" % filename),
                                             self.model.getEncodingOptions("hq")["options"],
                                             metadata,
                                             rawWav,
                                             "hq"))
        if self.view.encode3.get():
            thread3 = threading.Thread(target=commandLookup[self.model.getEncodingOptions("opus")["program"]],
                                       args=("-",
                                             os.path.join(self.view.sermonDirectory.get(), "%s.opus" % filename),
                                             self.model.getEncodingOptions("opus")["options"],
                                             metadata,
                                             rawWav,
                                             "opus"))

        if self.view.encode1.get():
            thread1.start()
        if self.view.encode2.get():
            thread2.start()
        if self.view.encode3.get():
            thread3.start()

        if self.view.encode1.get():
            thread1.join()
        if self.view.encode2.get():
            thread2.join()
        if self.view.encode3.get():
            thread3.join()

        resultLq = self.model.encodingResult["lq"]
        resultHq = self.model.encodingResult["hq"]
        resultOpus = self.model.encodingResult["opus"]
        if resultLq != 0 or resultHq != 0 or resultOpus != 0:
            messagebox.showerror("Error encoding files",
                                 "One or more files failed to encode properly.")

        self.view.status = STATUS.READY
        self.view.statusUpdate = True

        print("All done")

    def doEncode(self, launchArgs, fileInput, updateValue):
        splitArgs = launchArgs
        encodeData = threading.local()
        print(" ".join(splitArgs))
        encodeData.thread = subprocess.Popen(splitArgs, stdin=subprocess.PIPE)
        encodeData.thread.stdin.write(fileInput)
        encodeData.thread.stdin.close()

        encodeData.thread.wait()
        self.model.encodingResult[updateValue] = encodeData.thread.returncode

    def reenableWhenFinished(self, t1, t2, t3):
        t1.join()
        t2.join()
        t3.join()

        self.view.enableFields()

    def fileToRam(self, inputFile):
        program = self.model.getProgram("ffmpeg")

        cmd = [program, "-y", "-i", inputFile, "-f", "wav", "-"]

        rawWav = bytearray()

        print("CMD: " + " ".join(cmd))
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while True:
            data = p.stdout.read(2048)
            if len(data) == 0:
                break

            rawWav += data

        return rawWav

    def encodeLame(self, inputFile, outputFile, args, tags, fileInput, updateValue):
        splitArgs = shlex.split(args)
        cmd = [
            self.model.getProgram("lame"),
            inputFile,
            outputFile,
            "--tt",
            tags["sermonName"],
            "--ta",
            tags["speaker"],
            "--tl",
            tags["albumTitle"],
            "--tc",
            tags["comment"]
        ]
        cmd = cmd[:3] + splitArgs + cmd[3:]

        self.doEncode(cmd, fileInput, updateValue)
        print("Lame Done")

    def encodeOpus(self, inputFile, outputFile, args, tags, fileInput, updateValue):
        splitArgs = shlex.split(args)
        cmd = [
            self.model.getProgram("opusenc"),
            "--quiet",
            inputFile,
            outputFile,
            "--artist",
            tags["speaker"],
            "--title",
            tags["sermonName"],
            "--album",
            tags["albumTitle"]
        ]
        cmd = cmd[:1] + splitArgs + cmd[1:]

        self.doEncode(cmd, fileInput, updateValue)
        print("Opus done")

    def saveOptions(self):
        self.model.setEncodingProgram("lq", self.view.lqOptionsProgram.get())
        self.model.setEncodingProgram("hq", self.view.hqOptionsProgram.get())
        self.model.setEncodingProgram("opus", self.view.opusOptionsProgram.get())

        self.model.setEncodingOptions("lq", self.view.lqOptionsOptions.get())
        self.model.setEncodingOptions("hq", self.view.hqOptionsOptions.get())
        self.model.setEncodingOptions("opus", self.view.opusOptionsOptions.get())


def main():
    data = Data()
    gui = EncoderUi(data)
    controller = Controller(gui, data)
    gui.setEncodeAction(controller.encode)
    gui.setSelectSeriesAction(controller.seriesSelected)
    gui.setOptionSaveAction(controller.saveOptions)
    controller.prefillForm()

    gui.root.mainloop()

    pass


if __name__ == '__main__':
    main()
