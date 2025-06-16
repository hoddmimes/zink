package zink;

public class DBException extends Exception
{
    public DBException(String pMessage) {
        super(pMessage);
    }

    public DBException(Exception pException) {
        super(pException);
    }

    public DBException(String pMessage, Exception pException) {
        super(pMessage, pException);
    }
}
