 #!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import webbrowser
import BaseHTTPServer
import urlparse

from rauth import OAuth1Service, utils

HOSTNAME = "localhost"
LISTEN_PORT = 8000

keepServing = True

header = ""
footer = ""
responseTemplate = ""
inputTemplate = ""
errorTemplate = ""

with open("templates/header.html", "r") as templateFile:
    header = templateFile.read().decode("utf8")
with open("templates/footer.html", "r") as templateFile:
    footer = templateFile.read().decode("utf8")
with open("templates/response_template.html", "r") as templateFile:
    responseTemplate = templateFile.read().decode("utf8")
with open("templates/input_template.html", "r") as templateFile:
    inputTemplate = templateFile.read().decode("utf8")
with open("templates/error_template.html", "r") as templateFile:
    errorTemplate = templateFile.read().decode("utf8")

service = None
request_token = None
request_token_secret = None

class OAuthReturnHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):
        global service
        global request_token
        global request_token_secret

        if self.path == "/submit":
            length = int(self.headers['Content-Length'])
            post_data = urlparse.parse_qs(self.rfile.read(length).decode('utf-8'))
            if "key" not in post_data or "secret" not in post_data:
                self.send_response(301)
                self.send_header("Location", "/error")
                self.end_headers()
                return

            service = OAuth1Service(
                name="Twitter",
                consumer_key=post_data["key"][0],
                consumer_secret=post_data["secret"][0],
                request_token_url='https://api.twitter.com/oauth/request_token',
                access_token_url='https://api.twitter.com/oauth/access_token',
                authorize_url='https://api.twitter.com/oauth/authorize',
                base_url='https://api.twitter.com/1.1/'
            )
            params = {
                "oauth_callback" : "http://%s:%i/token" % (HOSTNAME, LISTEN_PORT)
            }
            token_response = service.get_raw_request_token(params=params)
            token_data = utils.parse_utf8_qsl(token_response.content)
            try:
                request_token = token_data["oauth_token"]
                request_token_secret = token_data["oauth_token_secret"]
                next_url = service.get_authorize_url(request_token)
            except KeyError:
                next_url = "/error"

            self.send_response(301)
            self.send_header("Location", next_url)
            self.end_headers()


    def do_GET(self):
        global keepServing

        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            output = "%s%s%s" % (header, inputTemplate, footer)
            self.wfile.write(output)
        elif self.path == "/error":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            output = "%s%s%s" % (header, errorTemplate, footer)
            self.wfile.write(output)
        elif self.path.startswith("/token"):
            if (service == None):
                self.send_response(301)
                self.send_header("Location", "/")
                self.end_headers()
                return

            get_data = urlparse.parse_qs(self.path[len("/token?"):])
            oauth_token = get_data["oauth_token"][0]
            oauth_verifier = get_data["oauth_verifier"][0]
            creds = {
                'request_token': request_token,
                'request_token_secret': request_token_secret
            }
            params = {'oauth_verifier': oauth_verifier}
            sess = service.get_auth_session(params=params, **creds)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            output = u""
            output += header
            output += responseTemplate
            output += footer
            output = output.replace(u"%%ACCESS_TOKEN%%", sess.access_token.encode("utf8"))
            output = output.replace(u"%%ACCESS_TOKEN_SECRET%%", sess.access_token_secret.encode("utf8"))
            self.wfile.write(output.encode("utf8"))
            keepServing = False




server_class = BaseHTTPServer.HTTPServer
httpd = server_class((HOSTNAME, LISTEN_PORT), OAuthReturnHandler)

browser_opened = False
try:
    while keepServing:
        if not browser_opened:
            webbrowser.open("http://%s:%s" % (HOSTNAME, LISTEN_PORT))
            browser_opened = True
        httpd.handle_request()
except Exception, e:
    raise e
    keepServing = False
finally:
    httpd.server_close()
