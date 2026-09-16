import tkinter as tk
import tkinter.font as tkf
from PIL import Image

#TODO BETTER UI!!!!!

image = Image.open("Shock by @duwiexe.png")

Root = tk.Tk()
Root.resizable(False,False)
Root.eval('tk::PlaceWindow . center')
Root.title("Duwi popup")
Root.geometry("300x150")
Root.minsize(300, 100)
Root.columnconfigure(0, weight=1)
Root.rowconfigure(0,weight=1)

font = tkf.Font(family="Helvetica", size=20, weight="bold")

liveNotif = tk.Label(Root,font=font,text="No Duwi... :(")
liveNotif.grid(column=0,row=0,sticky='nsew')

auth_Button = tk.Button(Root,text='Connect to Twitch')
auth_Button.grid(column=0,row=0,sticky='s',pady=5)