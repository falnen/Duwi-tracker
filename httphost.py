from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
"""
Twitch provides user access tokens upon user authorization, but does so via a URL fragment.
It places this fragment at the end of a redirect URL provided with the link to the auth page.
Which requires us to host a webpage to acquire this fragment.
"""
class webPage(BaseHTTPRequestHandler):
    fragment = None
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open ("acquireFragment.html", encoding= "utf-8") as file:
            view = file.read()
        self.wfile.write(view.encode("utf-8"))

    def do_POST(self):
        response = self.rfile.read(60).decode("utf-8")
        if "error" in response:
            pass
        else:
            webPage.fragment = response

def getFragment() -> str: 
    with HTTPServer(('localhost',3000),webPage) as server:
        server.handle_request()
        server.handle_request()
        server.server_close()
        if webPage.fragment:
            accesstoken = webPage.fragment.split('=').pop(1).split("&").pop(0)
            return accesstoken
        else:
            return False

def validateToken(token:str) -> bool:
    '''
    Tokens must be validated every hour as per twitch regulation.
    '''
    result = requests.get("https://id.twitch.tv/oauth2/validate",headers={"Authorization":f'Bearer {token}'})
    if result.reason == 'OK':
        #result.content.decode('utf-8')
        return True
    elif result.reason == 'Unauthorized':
        return False