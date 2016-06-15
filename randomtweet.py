import string, random, re, datetime
import keys   # Private set of constants representing the twitter API auth information
import tweepy
import botstate   # Global state information; some values should be immediately replaced with saved data.
import profanity

# Used in replyToMention()
REPLY_SUCCESS = 0
REPLY_FAIL = 1
REPLY_LATER = 2

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

def tweetEvent(eventString, tweetType='lastRandomTweet'):
    """
    eventString is the text to tweet
    tweetType should be the key in botstate.stateDict which needs to be updated.
    """
    global api
    # make sure the tweet is short enough for twitter's 140 character limit
    if len(eventString) <= 140:
        # send it out and return True
        api.update_status(eventString)
        # update the state variable indicating the new time that a random tweet has gone out
        botstate.stateDict[tweetType] = datetime.datetime.now()
        botstate.saveState()
        if logFile is not None:
            print('Tweeted successfully at', str(botstate.stateDict[tweetType]), file=logFile)
        return True
    else:
        return False # to indicate that the tweet was aborted

def removeSpaces(text):
    """
    Removes any leading or trailing spaces and returns the trimmed string.
    """
    while text[0] == ' ':
        text = text[1:]
    while text[-1] == ' ':
        text = text[:-1]
    return text

def checkForAttack(text):
    """
    If the text passed in states that something "attacks" or "attacked", returns a string containing the thing that attacked.
    Else, returns None.
    """
    if 'attacks' in text or 'attacked' in text:
        match = re.search('attack', text)
        # Start with everything before the word "attack"
        result = text[:match.start()]
        # Take out the @AdventurerCara (if it wasn't after the word "attack" and thus already removed)
        result = re.sub('@AdventurerCara', '', result)
        # At this point we should just have the thing that attacked, possibly with leading or trailing spaces
        result = removeSpaces(result)
        # Create a string to fight it with a random weapon
        values = {'monster': result,
                  'weapon': random.choice(botstate.weaponList),
                  'outcome': random.choice(['I won! XP gained.', 'It got the better of me! I escaped.', 'I won by the skin of my teeth, but XP is XP!'])}
        template = string.Template("I fought $monster with a $weapon! $outcome")
        return putAnBeforeVowels(template.substitute(values))

    else:
        return None

def replyToMention(mention):
    """
    Takes in a tweepy.Status object and replies if it knows what to do with it.
    If attempt to reply is successful, tweets, updates botstate.stateDict['lastReply'] and
       returns REPLY_SUCCESS
    If botstate.stateDict['lastReply'] was within the past 30 minutes, adds the mention to
       botstate.stateDict['storedMentions'] and returns REPLY_LATER
    If no reply was able to be created, returns REPLY_FAIL
    """
    if botstate.stateDict['lastReply'] > (datetime.datetime.now() - datetime.timedelta(minutes=30)):
        if mention not in botstate.stateDict['storedMentions']:
            # avoid duplicating a mention in storage
            botstate.stateDict['storedMentions'].append(mention)
        if logFile is not None:
            print('Mention saved for later reply:', mention.text, file=logFile)
        return REPLY_LATER
    else:
        attack = checkForAttack(mention.text)
        if attack is not None:
            # Add the username of the person who suggested the fight
            attack += ' @' + mention.user.screen_name
            # Tweet the event and update lastReply
            tweetEvent(attack, 'lastReply')


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

# Set up twitter auth
auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
auth.set_access_token(keys.ACCESS_TOKEN, keys.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# See if there are any mentions that didn't get a reply earlier
for mention in botstate.stateDict['storedMentions']:
    replyToMention(mention)

# Check for new mentions to reply to.
mentions = api.mentions_timeline()
# Use a variable to separately track the last mention number in the current set in case they are out of order,
# to avoid inadvertently skipping one.
lastMentionInCurrentSet = 0
for mention in mentions:
    if mention.id > botstate.stateDict['lastMentionFound']:
        replyToMention(mention)
        if lastMentionInCurrentSet < mention.id:
            lastMentionInCurrentSet = mention.id
if lastMentionInCurrentSet > botstate.stateDict['lastMentionFound']:
    botstate.stateDict['lastMentionFound'] = lastMentionInCurrentSet

# Make a random tweet as long as the last random tweet was at least 3 hours ago and last reply at least 15 minutes ago,
# to err on the side of not overtweeting.
if botstate.stateDict['lastRandomTweet'] is not None and \
                (datetime.datetime.now() - botstate.stateDict['lastRandomTweet']) > datetime.timedelta(hours=3) and \
                (datetime.datetime.now() - botstate.stateDict['lastReply']) > datetime.timedelta(minutes=15):
    # log that tweeting is being attempted
    if logFile is not None:
        print("Ok to tweet! stateDict['lastRandomTweet'] is ", str(botstate.stateDict['lastRandomTweet']), file=logFile)
    retries = 0
    # Run the tweet function within the loop declaration, then retry if it fails, up to a max of 6 times.
    while retries <= 5 and not tweetEvent(getRandomFight(botstate.monsterAdjList,botstate.monsterList,botstate.weaponList)):
        if logFile is not None:
            print('Tweet failed. Retrying...', file=logFile)
        retries += 1
else:
    # log that tweeting was not attempted
    if logFile is not None:
        print("Not ok to tweet! stateDict['lastRandomTweet'] is ", str(botstate.stateDict['lastRandomTweet']), file=logFile)

# Tag the log with date and time and close it.
if logFile is not None:
    print('Script ending at', str(datetime.datetime.now()), '\n', file=logFile)
    logFile.close()