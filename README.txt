Adventurer Cara Twitter Bot

PURPOSE:
Adventurer Cara randomly creates a tale of an encounter she had during an RPG-style adventure and tweets accordingly.
She also listens for mentions and replies to certain comments.

This code was originally created for the purpose of tinkering with python libraries and API interaction.

USE:
Script requires a keys.py file with Twitter OAuth information, as follows:
CONSUMER_KEY = ...
CONSUMER_SECRET = ...
ACCESS_TOKEN = ...
ACCESS_TOKEN_SECRET = ...

Tweeting is accomplished by running the randomtweet script. Controls are in place to prevent tweets from being too frequent,
regardless of how frequently the script is run. If automatic tweeting is desired, use a scheduler to run the script
at appropriate time intervals.