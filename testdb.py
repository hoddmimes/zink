import pymongo
from pymongo.errors import ConnectionFailure
import sys
from datetime import datetime
import time
import syslog
import logging


def dbExists( db, name ):
    dbs = db.list_database_names()
    if [item for item in dbs if item == name] == []:
        return False
    else:
        return True

def createDatabase( dbClient, dbName ):
    db = dbClient[ dbName ];
    dbCollection = db['entities'];
    dbCollection.create_index('application', unique = False)
    dbCollection.create_index('time', unique = False)
    dbCollection.create_index('time', unique = False)





def main():

    dbClient = pymongo.MongoClient("mongodb://" + "192.168.42.11" + ":" + str(27017))
    if not dbExists( dbClient, 'zink'):
      createDatabase( dbClient, 'zink')

    try:
        dbClient.admin.command('ismaster')
    except Exception as e:
        print("Failed to connect to DB, reason: " + str(e))
        exit(0)

    global db
    global collection
    db = dbClient[ "zink" ]
    collection = db["entries"]

    save("tezt", None, "detta är bar data")


def save( application, tag, data ):
    now = datetime.now();
    timstr = now.strftime("%Y-%m-%d %H:%M:%S.%f")[0:-3]
    doc = {'application' : application, 'data' : data, 'time' : timstr }
    if tag:
        doc['tag'] = tag;
    z = collection.insert_one(doc)
    print(z)



if __name__ == '__main__':
    main()