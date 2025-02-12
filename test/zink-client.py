import http.client
import json
import ssl
import datetime
import random

connection = None


def createConnection():
    global connection
    connection = http.client.HTTPSConnection('127.0.0.1', port=8282, context = ssl._create_unverified_context())

def javaTime():
    now = datetime.datetime.now();
    dt = now.strftime("%Y-%m-%d %H:%M:%S.%f")[0:-3]
    return dt

def saveEvents( count, current_hour ):
    _app = f'test-{current_hour}'

    for i in range(count):
        _json_msg = {'application' : _app}
        _x = random.randint(1,10)
        if (_x % 2) == 0:
            _json_msg['tag'] = "tag-" + str(_x)
        _json_msg['data'] = f'test data message {(i+1)} at {javaTime()}'
        send_post( {'command' : 'SAVE', 'apikey': 'test', 'data' : _json_msg} )


def findEvents( nowstr, current_hour ):
    _app = f'test-{current_hour}'
    # Find the last added messages
    _json_data = {'application' : _app}
    _json_data['after'] = nowstr
    send_post( { 'command' : 'FIND', 'apikey': 'test', 'data' : _json_data });


def main():
    _dt = datetime.datetime.now()
    _nowstr = javaTime()

    createConnection()
    saveEvents( 27, _dt.hour )

    findEvents( _nowstr, _dt.hour )



def send_post( json_data ):
    _headers = {'Content-type': 'application/json'}
    _json_rqst_data = json.dumps(json_data)

    print("[request] " + _json_rqst_data)
    connection.request('POST', '/post',  _json_rqst_data, _headers )

    response = connection.getresponse()

    _msg = response.read().decode();
    if response.code == 200 and len(_msg) > 0:
        try:
            _msg_array = json.loads(_msg)
            for m in _msg_array:
                print(m)
        except json.decoder.JSONDecodeError:
            print("[response] status: " + str(response.code) + " msg: " + _msg )
    else:
        print("[response] status: " + str(response.code) + " msg: " + _msg )

if __name__ == '__main__':
    main()