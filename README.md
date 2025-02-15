# Zink - An Event Sink

### About Zink

If you need to log events to a remote host, Zink might be a tool worth exploring.

Zink is a simple Python HTTP server application that listens for HTTP requests to either save or find events. The idea is that client applications or scripts can send **_Save_** or **_Find_** requests to the server.

The server uses an embedded _SQLite3_ or _MongoDB_ database to persist events.

### Data

The Zink server can both _Save_ and _Find_ _events_. The data attributes associated with an event are:

- `application`: String
- `tag`: String (optional)
- `time`: String (format: 'yyyy-MM-dd HH:mm:ss.SSS')
- `data`: String

When the server persists an event, it automatically sets the `time` for the event.

### Zink Clients

To interact with a Zink server, a client application will use HTTP/HTTPS connections. Requests are sent as HTTP/HTTPS POST requests for **Save** and **Find**.

Data can also be retrieved (i.e., **FIND**) from the Zink server via a standard browser using GET requests.

**POST requests** are JSON messages with the following structure:



**SAVE events** 
The URL path to the POST **save** entry is "/save" e.g. _https://<host>/save_
The post data in a _save_ have the following Json format
```json
{
  'application' : string
  'tag' : string
  'data' : string }
```
**_NOTE:_** \
    _'data.tag' is optional in save requests_

**FIND events**
The URL path to the POST **find** entry is "/save" e.g. _https://<host>/find_
The post data in a _find_ have the following Json format
```json
{
  'application': string
  'tag': string,
  'after': string,
  'before': string,
  'limit': int
}
```
**_NOTE:_** \
_'application' is mandatory_\
_'data.tag','data.after','data.before' and limit are optional_\
_'data.after' and 'data.before' are time strings have the following format 'yyyy-MM-dd HH:mm:ss.SSS'. They do not need to be complete. The time strings are padded._\
_'limit' specifies max number of events that should be retreived, latest first.


#### GET Requests
It's possible do find Zink events directly from an ordinary browser via accessing a Zink server URL like
```
https://localhost:8282/FIND?apikey=6ad345f621&application=frotz&tag=foo&before=2025-01-11&after=2025-01-01 20:22
```
**_NOTE:_** \
_'application' is a mandatory query parameter_ \
_'apikey' maybe mandatory or not depending on the server configuration_ \
_remaing parameters are optional_ \


## Server Configuration

The Zink server does take one parameter a JSON configuration file location
The configuration file has the following format

**_For Sqlite3 usage_**

```json
{
    "verbose" : true,
    "logfile" : null,
    "authorization" : {
        "file": "../zink-api-keys.json",
        "save_restricted": true,
        "find_restricted": true
    },
   "http_port": "8888",
   "interface" : "0.0.0.0",
   "ssl": {
      "key": "../key.pem",
      "cert": "../cert.pem"
   },
  "database" : {
      "type" : "sqlite3",
      "configuration" :  {
        "db_file" : "../zink.db"}
  }
}
```


**_For Mongodb usage_**
```json
{
  "verbose" : true,
  "logfile" : null,
  "authorization" : {
    "file": "../zink-api-keys.json",
    "save-restricted": true,
    "find-restricted": false
  },
  "http_port": "8888",
  "interface" : "0.0.0.0",
  "ssl": {
    "key": "../key.pem",
    "cert": "../cert.pem"
  },
  "database" : {
    "type" : "mongodb",
    "configuration" :  {
      "host" : "localhost",
      "port" :  27017,
      "db" :  "zink"}
  }
}
```


**_NOTE:_**\
The Zink server uses a simple API key-based authorization mechanism. If 'authorization' is present in the configuration file, the server will validate incoming requests to ensure they are authorized.
Validation for Save and Find requests can be enabled or disabled using the _save_restricted_ and _find_restricted_ attributes, respectively.
If 'authorization' is not present in the configuration file, no request validation will be performed.\
If 'logfile' is not present or null loging will be done to STDOUT\
If you would like the server to run SSL you have to generate a SSL certificate. This can be done with the following command
```
$ openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout key.pem -out cert.pem
```

 ## Zink Service as System Service

You might want to run the Zink service as a system service. In that case you have to create a system service file.
A simple example for linux would look like

**_Name the file zink.service_**
```
[Unit]
Description=Zink event server

[Service]
User=bertilsson
WorkingDirectory=/usr/local/zink
ExecStart=/usr/bin/python3 /usr/local/zink/zink-server.py -cfg=zink-server-sqlite3.json

[Install]
WantedBy=multi-user.target
```

On Fedora and Ubunto the file should be placed in the directory 
/lib/systemd/system

You have to enable the service with the following command
```
$ sudo systemctl enable zink.service
```

The service could then be started with the following command 
```
$ sudo systemctl start zink.service
```

The Zink service will do some progress logging to the system log.
You can see the actual status of the Zink service with the following command
```
$ sudo systemctl status zink.service
```

The system logging events can be viewed with the following commands
```
$ sudo journalctl -u zink
$ sudo journalctl -u zink --since="30 minutes"
```

_The rest is in the code_






