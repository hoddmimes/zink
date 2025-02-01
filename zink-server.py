
import argparse
from pathlib import Path
import http.server
import ssl
import json



class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(post_data.decode('utf-8'))

configuration_file = None
configuration = None

def connect_database():
    global configuration
    if configuration["database"]["type"] == "mongodb":
        connect_mongodb( configuration["database"]["confiiguration"])



def start_web_server():
    global configuration
    server_address = ( configuration["interface"],int( configuration["https-port"]))
    httpd = http.server.HTTPServer(server_address, MyHandler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=configuration["ssl"]["cert"], keyfile=configuration["ssl"]["key"])

    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    httpd.serve_forever()

def load_configuration( config_file ):
    global configuration
    if config_file.exists():
        with open(config_file, 'r') as file:
            configuration = json.load(file)
            print(f"Loaded configuration from {config_file}")
    else:
        print(f"Error: Configuration file {config_file} not found")
        exit(0)


def main():
    global configuration_file
    parser = argparse.ArgumentParser(
        prog="zink-server",
        description="HTTPS server capturing, event from HTTP clients",
        epilog="Thanks for using %(prog)s!",
    )

    parser.add_argument("-cfg", "--configuration" ,  default="./zink-server.json")
    args = parser.parse_args()
    configuration_file = Path(args.configuration)

    load_configuration(configuration_file)

    connect_database()

    start_web_server()



if __name__ == '__main__':
    main()