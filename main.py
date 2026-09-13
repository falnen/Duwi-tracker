import UI
import httphost
import Sockethost
import webbrowser
import Persistence
from threading import Thread
import pystray

APP_CLIENT_ID = "5wzg88m34ulgtxj4fdfazf9d2mpxq1"
#Also in Sockethost

class main():
    def __init__(self):
        self.token = None
        self.listener_thread = None

    def twitchAuthorize(self):
        UI.auth_Button.configure(command=None, text="Waiting for Auth...")
        webbrowser.open(f"https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={APP_CLIENT_ID}&redirect_uri=http://localhost:3000&scope=")
        self.token = httphost.getFragment()
        self.connect()

    def startListener(self):
        Persistence.saveTokenToFile(self.token)
        self.listener_thread = Thread(group=None,target=listener.start,kwargs={"accesstoken":self.token},daemon=True)
        self.listener_thread.start()
        UI.auth_Button.configure(command=None,text='Connected!')

    def connect(self):
        if self.token:
            valid = httphost.validateToken(self.token)
            if valid:
                self.startListener()
            else:
                UI.auth_Button.configure(command=self.twitchAuthorize,text='Reconnect to twitch')
        else:
            UI.auth_Button.configure(command=self.twitchAuthorize,text='Failed to connect... try again?')

if __name__ == "__main__":

    listener = Sockethost.liveListener()
    savedtoken = Persistence.loadTokenFromFile()
    app = main()
    if savedtoken:
        app.token = savedtoken
        app.connect()
    else:
        UI.auth_Button.configure(command=app.twitchAuthorize,text='Connect to twitch')

    def onClose():
        Persistence.saveTokenToFile(listener.accesstoken)
        if app.listener_thread is not None and app.listener_thread.is_alive():
            listener.stop()
            app.listener_thread.join()
        trayicon.stop()
        UI.Root.destroy()

    def trayClick():
        UI.Root.deiconify()

    def iconify():
        UI.Root.withdraw()

    trayicon = pystray.Icon('app',UI.image,menu=pystray.Menu(pystray.MenuItem('open',trayClick,default=True),pystray.MenuItem('Exit',onClose)))
    traythread = Thread(group=None,target=trayicon.run,daemon=True)
    traythread.start()

    UI.Root.protocol("WM_DELETE_WINDOW", iconify)


    UI.Root.mainloop()