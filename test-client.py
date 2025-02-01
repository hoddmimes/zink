import http.client
import json
import ssl

def main():
    conn = http.client.HTTPSConnection('127.0.0.1', port=5000, context = ssl._create_unverified_context())

    headers = {'Content-type': 'application/json'}

    rqst = {'application': 'test-client',
           'tag' : 'bar',
           'data' : 'frotz data'}

    json_data = json.dumps(rqst)

    conn.request('POST', '/post',  json_data, headers )

    response = conn.getresponse()
    print(response.read().decode())

if __name__ == '__main__':
    main()