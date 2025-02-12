
import argparse
import logging
import atexit
import sys
import urllib.parse
from pathlib import Path
import http.server
import ssl
import json
import syslog
from urllib.parse import urlparse
from urllib import parse
from aux import Aux
from aux import StringBuilder
from aux import Zlogger
from api_authorization import ApiAuthorization
from db_base import db_base
from mongo_db import mongo_db
from sqlite3_db import sqlite3_db


db : db_base = None
zlogger = None
configuration_file = None
configuration = None
authorization = None

class MyHandler(http.server.SimpleHTTPRequestHandler):


    def logmsg(self, stscode=None, msg=None ):
        global configuration

        if configuration['verbose']:
            if not stscode:
                zlog(f'[REQUEST] request: {msg}' )
            else:
                if msg:
                    zlog(f'[RESPONSE] sts: {str(stscode)}  message: {msg}' )
                else:
                    zlog(f'[RESPONSE] sts: {str(stscode)} (no message)' )

    def send_error(self, stscode, message):
        super().send_error(stscode,message)
        self.logmsg(stscode, message)

    def do_GET(self):
        global configuration
        global authorization

        if 'favicon.ico' in self.path:
            return self.send_response(404,"favicon.ico not found")

        self.logmsg(msg="requestor host: " + self.client_address[0] + " request: " + self.path)

        if not '?' in self.path:
            return self.send_error(400,"no query parameters present in request")

        _urlrqst =  urlparse( self.path );
        if not '/FIND' == _urlrqst.path.upper():
            return self.send_error(400,"invalid command")

        _params = dict(parse.parse_qsl(parse.urlsplit(self.path).query))

        if not 'application' in _params:
            return self.send_error(400,'invalid query parameter "application" is missing')

        if authorization and authorization.isFindRestricted() and not 'apikey' in _params:
            return self.send_error(400, 'invalid query parameter "apikey" is missing')

        if authorization and authorization.isFindRestricted() and not authorization.checkApiKey( _params['apikey'], 'FIND'):
            return self.send_error(401,'unauthorized apikey')

        self.defData( _params )

        _result = db.find( _params['application'], _params['tag'], _params['before'], _params['after'],_params['limit'])
        _html_string = self.buildFindPage(_result)

        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write( _html_string.encode('utf-8') )
        self.logmsg( 200, _html_string.encode('utf-8'))

    def buildHtmlRow( self,row ):
        if row['tag'] :
            _tag = row['tag']
        else:
            _tag = ""

        sb = StringBuilder()
        sb.append('</tr>')
        sb.append(f'<td style="text-align: center;border-collapse: collapse;border: 1px solid darkgray">{row["time"]}</td>')
        sb.append(f'<td style="text-align: center;border-collapse: collapse;border: 1px solid darkgray">{row["application"]}</td>')
        sb.append(f'<td style="text-align: center;border-collapse: collapse;border: 1px solid darkgray">{_tag}</td>')
        sb.append(f'<td style="text-align: center;border-collapse: collapse;border: 1px solid darkgray">{row["data"]}</td>')
        sb.append('<tr>')
        return sb.toString()


    def buildFindPage(self, result ):
        sb = StringBuilder()
        sb.append("<html>")
        sb.append('<body>')
        sb.append('<div  style="border:2px solid black; width:80%; margin-top: 50px;background-color:#f2f2f2">')
        sb.append('<br><br>')
        sb.append('<table style="margin: 0 auto; font-family:arial;">')
        sb.append('<tr>')
        sb.append('<th style="text-align: center;border-collapse: collapse;border: 1px solid darkgray">Time</th>')
        sb.append('<th style="text-align: center;border-collapse: collapse;border: 1px solid darkgray">Application</th>')
        sb.append('<th style="text-align: center;border-collapse: collapse;border: 1px solid darkgray">Tag</th>')
        sb.append('<th style="text-align: center;border-collapse: collapse;border: 1px solid darkgray">Message</th>')
        sb.append('</tr>')

        for _row in result:
            sb.append(self.buildHtmlRow( _row ))

        sb.append('</table>')
        sb.append('<br><br>')
        sb.append('</div>')
        sb.append('</body>')
        sb.append('</html>')

        return sb.toString()


    def do_POST(self):
        global configuration

        content_length = int(self.headers['Content-Length'])
        json_data_str = self.rfile.read(content_length)
        try:
            json_data = json.loads( json_data_str.decode('utf-8'))
        except json.decoder.JSONDecodeError:
            return self.send_error( 400, "Invalid json request " + str(json_data_str))

        self.logmsg(msg="requestor host: " + self.client_address[0] + " rqst: " + json_data_str.decode('utf-8'))

        _apikey = (None if not 'apikey' in json_data else json_data['apikey'])

        if not "command" in json_data:
            return self.send_error( 400, "Invalid request (command): " + json_data_str )

        if not "data" in json_data:
            return self.send_error( 400, "Invalid request (data): " + json_data_str)

        if json_data['command'].upper() == 'SAVE':
            return self.save_data( _apikey, json_data['data'] )


        if json_data['command'].upper() == 'FIND':
            return self.find_data( _apikey, json_data['data'] )

        self.send_error( 400, "Invalid command: " + str( json_data ))
        return self.logmsg(400, "Invalid command: " + str( json_data ))


    def defData(self, json_data):
        if not 'tag' in json_data:
            json_data['tag'] = None
        if not 'data' in json_data:
            json_data['data'] = None
        if not 'after' in json_data:
            json_data['after'] = None
        if not 'before' in json_data:
            json_data['before'] = None
        if not 'limit' in json_data:
            json_data['limit'] = 0
        return json_data


    def find_data( self, apikey, rqst_data):
        if not "application" in rqst_data:
            return self.send_error( 400, "Invalid request (data): " + str( rqst_data ))

        if authorization and authorization.isFindRestricted() and not apikey:
            return self.send_error( 400,'invalid query parameter "apikey" is missing')


        if authorization and authorization.isFindRestricted() and not authorization.checkApiKey( apikey,'FIND'):
            return self.send_error( 401,'unauthorized api-key')

        rqst_data = self.defData( rqst_data )
        _entries = db.find( rqst_data['application'], rqst_data['tag'], rqst_data['before'], rqst_data['after'],rqst_data['limit'])

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        _result = {'data': _entries }

        self.wfile.write(json.dumps(_entries).encode('utf-8'))
        self.logmsg( 200, json.dumps(_entries))


    def save_data( self, apikey, param_data ):

        if not "application" in param_data:
            return self.send_error( 400, "Invalid request (application): " + str( param_data ))

        if not "data" in param_data:
            return self.send_error( 400, "Invalid request (data): " + str( param_data ))

        if authorization and authorization.isSaveRestricted() and not apikey:
            return self.send_error(400,'invalid query parameter "apikey" is missing')

        if authorization and authorization.isFindRestricted() and not authorization.checkApiKey( apikey,'SAVE'):
            return self.send_error(401,'unauthorized api-key')


        global db
        param_data = self.defData( param_data )
        db.save( param_data['application'], param_data['tag'], param_data['data'])
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.logmsg(stscode=203)





def connect_database():
    global configuration
    global db

    if configuration["database"]["type"] == 'mongodb':
        db = mongo_db(configuration["database"]["configuration"]["host"],
                      configuration["database"]["configuration"]["port"],
                      configuration["database"]["configuration"]["db"])
        db.connect()
    if configuration["database"]["type"] == 'sqlite3':
        db = sqlite3_db(configuration["database"]["configuration"]["db_file"])
        db.connect()
    Aux.tosyslog(f"Connected to DB {configuration['database']['configuration']}")



def start_web_server():
    global configuration
    server_address = ( configuration["interface"],int( configuration["http_port"]))
    httpd = http.server.HTTPServer(server_address, MyHandler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    _key_file = configuration["ssl"]["key"]
    _cert_file = configuration["ssl"]["cert"]
    context.load_cert_chain(certfile=configuration["ssl"]["cert"], keyfile=configuration["ssl"]["key"])

    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    Aux.tosyslog(f"Starting Web Service on interface {configuration['interface']} port {configuration['http_port']}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        zlogger.log("Keyboard interruption, exiting Zink server")
        sys.exit("\n bye, bye")


def load_configuration( config_file ):
    global configuration
    if config_file.exists():
        with open(config_file, 'r') as file:
            configuration = json.load(file)
            Aux.tosyslog(f"Configuration file {config_file} loaded")
    else:
        print(f"Error: Configuration file {config_file} not found")
        Aux.tosyslog(f"Error: Configuration file {config_file} not found")
        exit(0)

def zlog( msg ):
    zlogger.log( msg)


def openLogfile():
    global configuration
    global zlogger

    if 'logfile' in configuration:
        zlogger = Zlogger( configuration["logfile"])
        Aux.tosyslog(f"Created and opened logfile {configuration['logfile']}")
    else:
        zlogger = Zlogger( None )
        Aux.tosyslog("Created and opened logfile STDOUT")


def load_authorization():
    global configuration
    global authorization

    if not 'authorization' in configuration:
        zlog("No authorization defined")

    if not 'file' in configuration['authorization']:
            zlog("No authorization file attribute defined")

    _auth_file = Path(configuration['authorization']['file'])
    if not _auth_file.exists():
        zlog(f"Authorization file {configuration['authorization']['file']} does not exists")
        return

    with open(_auth_file, 'r') as file:
        _api_keys = json.load(file)
        print(f"Loaded ({len(_api_keys['api-keys'])}) api-keys fom api-key-file {configuration['authorization']['file']}")
        _find_restricted = True
        if 'find_restricted' in configuration['authorization']:
            _find_restricted = configuration['authorization']['find_restricted']
        _save_restricted = True
        if 'save_restricted' in configuration['authorization']:
            _save_restricted = configuration['authorization']['save_restricted']

        authorization = ApiAuthorization( _api_keys, _find_restricted, _save_restricted, zlogger )
        Aux.tosyslog(f"Loaded authorization file {configuration['authorization']['file']}")


def zinkExit():
    Aux.tosyslog( Aux.javaTime() + " Zink server is terminating, Good Bye!")


def main():
    global configuration_file

    syslog.openlog("zink")
    parser = argparse.ArgumentParser(
        prog="zink-server",
        description="HTTPS server capturing, event from HTTP clients",
        epilog="Thanks for using %(prog)s!",
    )




    parser.add_argument("-cfg", "--configuration" ,  default="./zink-server-sqlite3.json")
    args = parser.parse_args()
    configuration_file = Path(args.configuration)

    load_configuration(configuration_file)
    openLogfile()
    print(f"Loaded configuration from {configuration_file}")

    atexit.register(zinkExit)

    load_authorization()

    connect_database()

    start_web_server()

if __name__ == '__main__':
    main()