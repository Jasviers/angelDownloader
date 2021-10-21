from tkinter import messagebox, filedialog
import tkinter as tk
from tkinter.constants import HORIZONTAL
import tkinter.ttk as ttk
from youtube_dl import YoutubeDL

from urllib.parse import urlparse
import os
import re

class Downloader:

    def __init__(self, window):
        self.window = window
        self.window.title("Youtube Downloader")
        self.window.geometry("1400x300")

        self.PROGRESS_BAR_LEN=400
        self.actual_song_downloading=""

        self.label1 = tk.Label(self.window, text="Enter a youtube url")
        self.label1.place(x=50, y=50)
        self.label2 = tk.Label(self.window, text="")
        self.label2.place(x=self.PROGRESS_BAR_LEN+100, y=200)

        style = ttk.Style()
        style.theme_use('alt')
        style.configure("green.Horizontal.TProgressbar",
                    foreground='green', background='green')
        self.pb = ttk.Progressbar(self.window, style="green.Horizontal.TProgressbar", orient=HORIZONTAL,
                                     length=self.PROGRESS_BAR_LEN, mode="determinate")
        self.pb.place(x=50, y=200)

        self.entry = tk.Entry(self.window, bd=1, width="60")
        self.entry.place(x=50, y=100)

        self.btn = tk.Button(self.window, text="Save", command=self.downloadButton)
        self.btn.place(x=1200, y=100)


        self.YDL_OPTIONS = {'format': 'bestaudio', 
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',}],
        'noplaylist': 'True'}
        self.playlist_re = re.compile(r"\b(list)\b")
        self.watch_re = re.compile(r"\b(watch)\b")
        
    def downloadButton(self):
        if url:= self.entry.get():
            dir = filedialog.askdirectory()
            if os.path.isdir(dir):
                if songlist := self._songList(url):
                    step = int(self.PROGRESS_BAR_LEN/len(songlist))
                    for song in songlist:
                        self.actual_song_downloading = song["title"]
                        self.YDL_OPTIONS["outtmpl"] = dir+"\\"+"".join(song["title"].split())+".mp3"
                        self.label2["text"] = song["title"] if len(song["title"]) <= 60 else song["title"][:60]
                        self.window.update_idletasks()
                        try:
                            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                                ydl.download([song["source"]])
                        except:
                            messagebox.showerror("Error", f"Error downloading: {self.actual_song_downloading}")
                        self.pb["value"] += step
                else:
                    messagebox.showerror("Error", "Url doesn't work")
            else:
                messagebox.showerror("Error", "Directory doesn't exist")
        else:
            messagebox.showerror("Error", "Entry is empty")

    def _songList(self, url) -> list:
        url_result = urlparse(url)
        vlist = []
        if all([url_result.scheme, url_result.netloc, url_result.path]):
            if url_result.query and self.playlist_re.search(url_result.query):
                self.label2["text"] = "Downloading playlist references..."
                self.window.update_idletasks()
                if self.watch_re.search(url):
                    list_query = [i for i in url_result.query.split("&") if self.playlist_re.search(i)]
                    query = "".join([url_result.netloc, "/playlist?", list_query[0]])
                with YoutubeDL(self.YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(url, download=False)
                entries_len = len(info['entries'])
                for elem in info['entries']:
                    vlist.append({'source': elem['formats'][0]['url'], 'title': elem['title']})
            else:
                self.label2["text"] = "Downloading song reference..."
                self.window.update_idletasks()
                with YoutubeDL(self.YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(url, download=False)
                vlist.append({'source': info['formats'][0]['url'], 'title': info['title']})
        return vlist


window = tk.Tk()
Downloader(window)
window.mainloop()