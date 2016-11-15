
#!/usr/bin/env python2
from SimpleHTTPServer import SimpleHTTPRequestHandler
import SocketServer
import shutil
import webbrowser
from urlparse import urlparse
import io
import json

from one import OneNote

PORT = 5353

from requests_oauthlib import OAuth2Session
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


# for Office365 notebooks
enterprise_api = {
    # This information is obtained upon registration of a new Outlook Application
    'client_id':'APP_ID_HERE',
    'client_secret':'APP_SECRET_HERE',
    'auth_url':'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    'token_url':'https://login.microsoftonline.com/common/oauth2/v2.0/token',
    'refresh_url':'https://login.live.com/oauth20_token.srf',
    'scope': ["Notes.Read.All", "Notes.Read"],
    'redirect_uri':'http://localhost:5353/zim',
    }  

# for OneDrive personal notebooks
live_api = {
    # This information is obtained upon registration of a new Outlook Application
    'client_id':'APP_ID_HERE',
    'client_secret':'APP_SECRET_HERE',
    'auth_url':'https://login.live.com/oauth20_authorize.srf',
    'token_url':'https://login.live.com/oauth20_token.srf',
    'refresh_url':'https://login.live.com/oauth20_token.srf',
    'scope':["wl.signin", "wl.basic", "wl.offline_access", "office.onenote"],
    'redirect_uri':'http://localhost:5353/zim',
    }  

onenote = None

class  AuthServerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        print("Serving: ", url.path)

        self.send_response(200, message='Logging in to your Live account!<br/>Close this window now...')

        # Get the authorization verifier code from the callback url
        # /zim?...
        if url.path.find("zim") >= 0:
            query = url.query
            params = dict(qc.split("=") for qc in query.split("&"))
            # use the callback url to extract the tokens
            self.server.on_callback(self.path)


        if url.path.find("import") >= 0:
            if onenote is not None:
                onenote.import_all()

  
            
 
class AuthServer(SocketServer.TCPServer):
    def __init__(self, api_config):
        SocketServer.TCPServer.__init__(self, ("", PORT), AuthServerHandler)
        self.config = api_config
        self.api = None
        self.token = None 

    def login(self):
        self.refresh_token()
        if self.token is not None:
            self.on_login()
            return

        self.api = OAuth2Session(self.config['client_id'],scope=self.config['scope'],redirect_uri=self.config['redirect_uri'])

        # Redirect  the user owner to the OAuth provider (i.e. Outlook) using an URL with a few key OAuth parameters.
        authorization_url, state = self.api.authorization_url(self.config['auth_url'])
        print('Please go here and authorize,', authorization_url)
        webbrowser.open(authorization_url,new=1, autoraise=True)
        self.start()

    def start(self):
        print("serving on port", PORT)
        try:
            self.serve_forever()
        except:
            self.shutdown()
            self.server_close()
    
    def get_token(self, callback_url):
        # Fetch the access token
        self.token = self.api.fetch_token(self.config['token_url'],client_secret=self.config['client_secret'],authorization_response=callback_url)
        print("successfully logged in to MS live!")

    def refresh_token(self):
        """Refreshing an OAuth 2 token using a refresh token.
        """
        tokenstr = self.load_token()

        if tokenstr:
            token = json.loads(tokenstr)
            extra = {
                'client_id': self.config['client_id'],
                'client_secret': self.config['client_secret'],
            }

            self.api = OAuth2Session(self.config['client_id'], token=token)
            self.token = self.api.refresh_token(self.config['refresh_url'], **extra)

    def save_token(self, token):
        with io.open('token.dat', 'w', encoding='utf-8') as f:
            f.write(unicode(json.dumps(token)))

    def load_token(self):
        try:
            with io.open('token.dat', 'r', encoding='utf-8') as f:
                tokenstr = f.read()
                return tokenstr
        except (OSError, IOError) as e:
            print('ERROR: ', e)
            return None

    def on_callback(self, callback_url):
        self.get_token(callback_url)
        self.save_token(self.token)
    
    def on_login(self):
        onenote = OneNote(self.api)
        onenote.import_all()


live_api['client_id'] = os.getenv('LIVE_CLIENT_ID', live_api['client_id'])
live_api['client_secret'] =os.getenv('LIVE_CLIENT_SECRET', live_api['client_secret'])

enterprise_api['client_id'] = os.getenv('ENTERPRISE_CLIENT_ID', enterprise_api['client_id'])
enterprise_api['client_secret'] =os.getenv('ENTERPRISE_CLIENT_SECRET', enterprise_api['client_secret'])


server = AuthServer(live_api)

server.login()
