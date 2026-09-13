import UI
from httphost import validateToken
from websockets.sync.client import connect,ClientConnection
from json import loads
from threading import Timer,Lock
import requests
APP_TIMEOUT = 600

APP_CLIENT_ID = "5wzg88m34ulgtxj4fdfazf9d2mpxq1"
#also in main

WS_URL = f'wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds={APP_TIMEOUT}'
EVENT_SUB_URL = "https://api.twitch.tv/helix/eventsub/subscriptions"
DUWI_ID = '92395876'

class liveListener():
    def __init__(self):
        self.accesstoken = None
        self._current_websocket = None
        self._old_websocket: ClientConnection = None
        self._watchdog = None
        self._watchdog_lock = Lock()

    def _startWatchdog(self):
        with self._watchdog_lock:
            if self._watchdog is not None:
                self._watchdog.cancel()

            self._watchdog = Timer(APP_TIMEOUT, self._timeout,)
            self._watchdog.daemon = True
            self._watchdog.start()

    def _timeout(self):
        if self._current_websocket is not None:
            self._current_websocket.close()
        #TODO Implement an error message
        self.start()

    def start(self,URL:str = WS_URL,accesstoken:str = None):
        if accesstoken:
            self.accesstoken = accesstoken
        try:
            with connect(URL) as ws:
                self._current_websocket = ws
                validationcycle = 0 #Token must be validated every hour.
                while True:
                    validationcycle += 1
                    if validationcycle >= 10:
                        validationcycle = 0
                        if not validateToken(self.accesstoken):
                            self._current_websocket.close()
                            #TODO tkinter things
                            break
                    message = loads(ws.recv())
                    self._handleMessage(message)
        except Exception as e:
            #TODO Implement an error message system
            print(e)

    def stop(self):
        self._watchdog.cancel()
        self._watchdog.join()
        self._current_websocket.close()

    def _handleMessage(self,message:dict):
        self._startWatchdog()
        metadata = message["metadata"]
        payload = message["payload"]
        match metadata["message_type"]:
            case "session_welcome":
                self.sessionid = payload["session"]["id"]
                self._requestSubscription(self.sessionid,self.accesstoken)
                if self._old_websocket is not None:
                    self._old_websocket.close()
                    self._old_websocket = None  
            case "notification":
                self._receiveNotification(metadata,payload)
            case "session_keepalive":
                #Sent every APP_TIMEOUT seconds if no notification is received
                print('Keep alive')
            case "revocation":
                self._receiveRevocation(metadata,payload)
    
    def _requestSubscription(self,sessionid:str,accesstoken:str):
        headers = {
            "Authorization": f"Bearer {accesstoken}",
            "Client-Id": APP_CLIENT_ID,
            "Content-Type": "application/json"
            }
        body = {
            "type": "stream.online",
            "version": "1",
            "condition": {
                "broadcaster_user_id": DUWI_ID
            },
            "transport": {
                "method": "websocket",
                "session_id": sessionid
            }
        }
        sub = requests.post(EVENT_SUB_URL,headers=headers,json=body)
        print(sub.status_code)
        #TODO Display info in app

    def _receiveNotification(self,metadata:dict,payload:dict):
        UI.Root.after(0,UI.Root.deiconify())
        UI.Root.after(0,UI.liveNotif.configure(text='Duwi is LIVE!!!'))
        notification = payload["event"]
        #TODO Display aditional info in app

    def _receiveReconnect(self,payload:dict):
        new_ws_url = payload["reconnect_url"]
        print("Reconnecting")
        self._old_websocket = self._current_websocket
        self.start(new_ws_url)

    def _receiveRevocation(self,metadata:dict,payload:dict):
        self._current_websocket.close()
        #TODO error message display and try again button
        print(payload["status"])
