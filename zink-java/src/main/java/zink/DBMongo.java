package zink;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.mongodb.BasicDBObject;

import com.mongodb.client.*;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.IndexOptions;
import com.mongodb.client.model.Sorts;
import com.mongodb.client.result.InsertOneResult;
import org.bson.Document;
import org.bson.conversions.Bson;

import java.text.SimpleDateFormat;

public class DBMongo implements DBBase
{
    private static final SimpleDateFormat SDF = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");

    private static final String APPLICATION = "application";
    private static final String TAG = "tag";
    private static final String DATA = "data";
    private static final String TIME = "time";
    private static final String COLLECTION_NAME =" entries";


    final String mDbHost;
    final int mDbPort;
    final String mDbName;

    private MongoClient mClient;
    private MongoDatabase mDb;
    private MongoCollection<Document> mEntriesCollection;

    DBMongo(  String pDbName, String pDbHost, int pDbPort )
    {
        mDbHost = pDbHost;
        mDbPort = pDbPort;
        mDbName = pDbName;
    }
    @Override
    public void connect() throws DBException
    {
        try {
            boolean tDbExits = checkIfDbExits();

            // Open and connect to the database
            String tURI = "mongodb://" + mDbHost + ":" + mDbPort + "/";
            mClient = MongoClients.create( tURI );
            mDb = mClient.getDatabase( mDbName );

            mEntriesCollection = mDb.getCollection(COLLECTION_NAME);
            if (!tDbExits) {
                createKeys();
            }
        }
        catch(Exception e ) {
            throw new DBException( e );
        }
    }

    private void createKeys() {
        mEntriesCollection.createIndex( new BasicDBObject(APPLICATION,1 ), new IndexOptions().unique( false ));
        mEntriesCollection.createIndex( new BasicDBObject(TAG,2 ), new IndexOptions().unique( false ));
        mEntriesCollection.createIndex( new BasicDBObject(TIME,3 ), new IndexOptions().unique( false ));
    }

    private boolean checkIfDbExits( ) throws DBException {
        try {
            String tURI = "mongodb://" + mDbHost + ":" + mDbPort + "/";
            mClient = MongoClients.create( tURI );
            MongoIterable<String> tDBItr =  mClient.listDatabaseNames();
            for( String tDbName : tDBItr) {
                if (tDbName.compareTo( mDbName ) == 0) {
                    mClient.close();
                    return true;
                }
            }
            mClient.close();
            return false;
        }
        catch(Exception e ) {
            throw new DBException( e );
        }
    }

    @Override
    public void delete() throws DBException
    {
        try {
            if (mDb != null) {
                mDb.drop();
                mClient.close();
                connect();
            } else {
                throw new DBException("database can not be deleted, the DB is not yet opened");
            }
        }
        catch( Exception e){
            throw new DBException(e);
        }
    }

    @Override
    public void save(String pApplication, String pTag, String pData) throws DBException
    {
        try {
            Document tDoc = new Document();
            tDoc.put( APPLICATION, pApplication);
            if (pTag != null) {
                tDoc.put( TAG, pTag);
            }
            tDoc.put( DATA, pData);
            tDoc.put( TIME, SDF.format(System.currentTimeMillis()));
            InsertOneResult tSts = mEntriesCollection.insertOne( tDoc );
        }
        catch( Exception e) {
          throw new DBException(e);
        }
    }

    @Override
    public JsonArray find(String pApplication, String pTag, String pBefore, String pAfter, int pLimit) throws DBException {
        Bson tFilter = Filters.eq( APPLICATION, pApplication );
        if (pTag != null) {
            tFilter = Filters.and( tFilter, Filters.eq( TAG, pTag));
        }
        if (pBefore != null) {
            tFilter = Filters.and( tFilter, Filters.lt( TIME, pBefore));
        }
        if (pAfter != null) {
            tFilter = Filters.and( tFilter, Filters.gt( TIME, pAfter));
        }
        JsonArray jResults = new JsonArray();
        FindIterable<Document> tDocuments = mEntriesCollection.find( tFilter).limit(pLimit).sort(Sorts.descending(TIME ));

        for( Document tDoc : tDocuments) {
            JsonObject jEntry = new JsonObject();
            jEntry.addProperty( APPLICATION, tDoc.getString( APPLICATION));
            jEntry.addProperty( TIME, tDoc.getString( TIME ));
            jEntry.addProperty( DATA, tDoc.getString(DATA));
            if (tDoc.containsKey( TAG )) {
                jEntry.addProperty(TAG, tDoc.getString(TAG));
            }
            jResults.add(jEntry);
        }
        return jResults;
    }

    @Override
    public void close() {
        mClient.close();
        mDb = null;
        mClient = null;
    }
}
