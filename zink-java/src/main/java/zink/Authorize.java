package zink;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

import java.util.HashMap;

public class Authorize {
    static public enum Action {SAVE, FIND};

    final private HashMap<String, String> mApiKeys;
    final private boolean mSaveRestricted;
    final private boolean mFindRestricted;

    public Authorize(JsonArray jAuthorize, boolean pSaveRestricted, boolean pFindRestricted) {
        mApiKeys = new HashMap<>();
        mSaveRestricted = pSaveRestricted;
        mFindRestricted = pFindRestricted;
        if (jAuthorize != null) {
            for (int i = 0; i < jAuthorize.size(); i++) {
                JsonObject jUserKey = jAuthorize.get(i).getAsJsonObject();
                mApiKeys.put(jUserKey.get("key").getAsString(), jUserKey.get("key").getAsString());
            }
        }
    }

    public int size() {
        return mApiKeys.size();
    }

    public boolean isFindRestricted() {
        return mFindRestricted;
    }
    public boolean isSaveRestricted() {
        return mSaveRestricted;
    }

    public boolean validate(String pKey, Action pAction ) {
        if (((pAction == Action.SAVE) && (mSaveRestricted)) || ((pAction == Action.FIND) && (mFindRestricted))) {
            return mApiKeys.containsKey(pKey);
        }
        return false;
    }
}

