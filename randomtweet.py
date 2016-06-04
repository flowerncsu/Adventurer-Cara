import string, random, re, datetime
import keys   # Private set of constants representing the twitter API auth information
import tweepy
import botstate   # Global state information; some values should be immediately replaced with saved data.



def putAnBeforeVowels(inputstr):
    """
    Checks to see if 'a' is used before a word starting with a vowel. If so, replaces with 'an'.
    """
    outputstr = ''
    lastCopiedIndex = -1
    if ' a ' not in inputstr:
        return inputstr
    else:
        for match in re.finditer(' a ', inputstr):
            # match.start() is the letter *before* the space before 'a'
            # match.end() is the letter after ' a '
            if inputstr[match.end()] in 'aeiou':
                # insert the necessary 'n'
                # TODO: look for a more elegant way to insert a letter into a string
                outputstr += inputstr[lastCopiedIndex + 1:match.end() - 1]
                outputstr += 'n'
                lastCopiedIndex = match.end() - 2
        # add the rest of inputstr to outputstr
        outputstr += inputstr[lastCopiedIndex + 1:]
        return outputstr

def getRandomFight(adjectiveList, monsterList, weaponList):
   values = {'adj': random.choice(adjectiveList),
             'monster': random.choice(monsterList),
             'weapon': random.choice(weaponList),
             'outcome': random.choice(['I won! XP gained.', 'It got the better of me! I escaped.', 'I won by the skin of my teeth, but XP is XP!'])}
   template = string.Template("I fought a $adj $monster with a $weapon! $outcome")
   return putAnBeforeVowels(template.substitute(values))

def tweetEvent(eventString):
    # make sure the tweet is short enough for twitter's 140 character limit
    if len(eventString) <= 140:
        # send it out and return True
        auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
        auth.set_access_token(keys.ACCESS_TOKEN, keys.ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        api.update_status(eventString)
        # update the state variable indicating the new time that a random tweet has gone out
        botstate.lastRandomTweet = datetime.datetime.now()
        botstate.saveState()
        if logFile is not None:
            print('Tweeted successfully at ', str(botstate.lastRandomTweet), file=logFile)
        return True
    else:
        return False # to indicate that the tweet was aborted

# open log for transactions
try:
    logFile = open('twitterbot.log', 'a')
except OSError:
    print("Error opening log file")
    logFile = None

# load state information from file
if not botstate.getState():
    if logFile is not None:
        print('Error loading from disk', file=logFile)

# Don't run if the last random tweet was within the last hour. Err on the side of *not* tweeting too much
if botstate.lastRandomTweet is not None and (datetime.datetime.now() - botstate.lastRandomTweet) > datetime.timedelta(hours=1):
    # log that tweeting is being attempted
    if logFile is not None:
        print('Ok to tweet! botstate.lastRandomTweet is ', str(botstate.lastRandomTweet), file=logFile)
    retries = 0
    # Run the tweet function within the loop declaration, then retry if it fails, up to a max of 6 times.
    while retries <= 5 and not tweetEvent(getRandomFight(botstate.monsterAdjList,botstate.monsterList,botstate.weaponList)):
        if logFile is not None:
            print('Tweet failed. Retrying...', file=logFile)
        retries += 1
else:
    # log that tweeting was not attempted
    if logFile is not None:
        print('Not ok to tweet! botstate.lastRandomTweet is ', str(botstate.lastRandomTweet), file=logFile)

# Tag the log with date and time and close it.
if logFile is not None:
    print('Script ending at', str(datetime.datetime.now()), '\n', file=logFile)
    logFile.close()