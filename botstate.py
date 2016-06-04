import pickle, datetime

# These three variables refer to the global state of the bot. All 3 should be datetime objects.
# Values are initialized to None, but should be replaced with state information unpacked from saved data before use.
lastRandomTweet = None # refers to purely randomly-generated tweets
lastReply = None # refers to a tweet which is specifically a reply to another twitter user
lastCheckForMentions = None # when the bot last checked for mentions

saveFileName = 'twitterbot.dat'

def getState():
    """
    References save file and loads state variables.
    Returns True if successful, False if error.
    """
    global lastRandomTweet
    global lastReply
    global lastCheckForMentions
    try:
        saveFile = open(saveFileName, 'rb') # 'rb' means read in binary mode (not str)
        stateDict = pickle.load(saveFile)
        lastRandomTweet = stateDict['lastRandomTweet']
        lastReply = stateDict['lastReply']
        lastCheckForMentions = stateDict['lastCheckForMentions']
        saveFile.close()
        return True
    except (OSError, pickle.PickleError):
        return False


def saveState():
    """
    Saves state variables to a file. Creates file if not yet existing.
    """
    global lastRandomTweet
    global lastReply
    global lastCheckForMentions
    stateDict = {'lastRandomTweet': lastRandomTweet,
                 'lastReply': lastReply,
                 'lastCheckForMentions': lastCheckForMentions}
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
    global lastRandomTweet
    global lastReply
    global lastCheckForMentions
    lastCheckForMentions = toSet
    lastRandomTweet = toSet
    lastReply = toSet
    print(lastRandomTweet)
    saveState()

# Food for the randomness generator. Imagination welcome below!
monsterList = ['orc', 'goblin', 'troll', 'wizard', 'dwarf']
monsterAdjList = ['giant', 'magic', 'evil', 'sneaky', 'rabid', 'vicious']
weaponList = ['crossbow', 'sword', 'dagger', 'wet noodle', 'staff', 'harmonica']