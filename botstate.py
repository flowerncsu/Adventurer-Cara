import pickle, datetime

# This dictionary refers to the global state of the bot.
# Values are initialized to None, but should be replaced with state information unpacked from saved data before use.

stateDict = {'lastRandomTweet': None, # refers to purely randomly-generated tweets
             'lastReply': None, # refers to a tweet which is specifically a reply to another twitter user
             'lastMentionFound': None, # status ID of last mention processed
             'storedMentions': None # list of mentions that may warrant a response but which have not been evaluated yet
}


saveFileName = 'twitterbot.dat'

def getState():
    """
    References save file and loads state variables.
    Returns True if successful, False if error.
    """
    global stateDict
    try:
        saveFile = open(saveFileName, 'rb') # 'rb' means read in binary mode (not str)
        stateDict = pickle.load(saveFile)
        saveFile.close()
        return True
    except (OSError, pickle.PickleError):
        return False


def saveState():
    """
    Saves state variables to a file. Creates file if not yet existing.
    """
    global stateDict
    try:
        saveFile = open(saveFileName, 'wb') # overwrites existing file because of 'w', 'b' allows binary data
        pickle.dump(stateDict, saveFile)
        saveFile.close()
        return True
    except (OSError, pickle.PickleError):
        return False

def initState(toSet=(datetime.datetime.now() - datetime.timedelta(days=1))):
    """
    Run this function to initialize the saveFile. By default, times are set
    to 1 day ago, but can be passed as a parameter (one parameter sets all dates the same.)
    """
    global stateDict
    stateDict['lastMentionFound'] = 1
    stateDict['lastRandomTweet'] = toSet
    stateDict['lastReply'] = toSet
    saveState()

# Food for the randomness generator. Imagination welcome below!
monsterList = ['orc', 'goblin', 'troll', 'wizard', 'dwarf']
monsterAdjList = ['giant', 'magic', 'evil', 'sneaky', 'rabid', 'vicious']
weaponList = ['crossbow', 'sword', 'dagger', 'wet noodle', 'staff', 'harmonica']