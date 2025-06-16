package zink;

import com.google.gson.JsonArray;

public interface DBBase
{
    public void connect();

    public void save(String pApplication, String pTag, String pData) throws DBException ;

    public JsonArray find(String pApplication, String pTag, String pBefore, String pAfter, int pLimit) throws DBException;

    public void close();
}
