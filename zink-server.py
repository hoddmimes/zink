
import argparse
from pathlib import Path
import http.server
import ssl



class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(post_data.decode('utf-8'))

def declare_server():

    server_address = ('127.0.0.1', 5000)
    httpd = http.server.HTTPServer(server_address, MyHandler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(
        prog="zink-server",
        description="HTTPS server capturing, event from HTTP clients",
        epilog="Thanks for using %(prog)s!",
    )

    parser.add_argument("-p", "--port" )
    parser.add_argument("-r", "--root" )
    parser.add_argument("-db", "--database" )
    args = parser.parse_args()
    print(args)

    declare_server()


if __name__ == '__main__':
    main()