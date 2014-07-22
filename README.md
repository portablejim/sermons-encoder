# Sermons Encoder

## Description

Program to convert sermons in lossless formats
(e.g. wav, flac) to lossy formats (i.e. mp3, opus)

The program outputs the following files with the format YYYYMMDD
 (year-month-day) in the specified directory:
YYYYMMDD.mp3
dial/YYMMDD.mp3
YYYYMMDD.opus

The quality of the files is controllable in the program options.


## Dependencies

 * Python 3 with modules: tkinter, sqlite3
 * `ffmpeg` or `libav`
 * `lame`
 * `opusenc`

