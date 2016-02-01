"""
"""

import sys
import time
import traceback
import subprocess
import datetime
import ConfigParser
from os.path import expanduser
from slackbot import SlackBot
from humanize import naturaltime, naturalday


def hi(bot, msg, match):
    bot.respond(msg, 'Hello')

def seen(bot, msg, match):
    user_id = match.group(1)
    user_info = bot.users.get(user_id)
    if user_info:
        response = 'I last saw ' + '<@' + user_id + '>'
        response += naturaltime(time.time() - user_info['time'])
    else:
        response = "I haven't seen " + '<@' + user_id + '> lately'
    bot.respond(msg, response)

def getFortune(bot, msg, match):
    ftext = subprocess.check_output(['fortune'])

    response = 'Your fortune:\n' + ftext
    bot.respond(msg, response)

def getStats(bot, msg, match):
    stats = bot.stats
    response = "I was born "
    response += naturalday(datetime.datetime.fromtimestamp(stats['bornOn']))
    response += ' and named CrashBot version '+stats['version']
    response += ".\n"
    response += "I woke up "
    response += naturaltime(time.time() - stats['startTime'])
    response += ".\n"
    response += "I've answered " + str(stats['count']+1) + " commands.\n"
    response += "I've seen " + str(bot.users.count()) + " users."
    bot.respond(msg, response)

def help(bot, msg, match):
    response = 'I am the Crash Bot. '
    response += 'I try to be helpful by answering commands.\n'
    response += 'You can send me a direct message or reference me @crashbot in any message\n'
    response += "I'll respond to the commands:\n\n"
    response += "help by showing you this message\n"
    response += "fortune by showing you a fortune\n"
    response += "seen @user by telling you the last time I saw that user\n"
    response += "stats by telling you a few stats about myself\n"
    response += "\nI hope I can be of assistance"
    bot.respond(msg, response)

def main(bot):
    if not bot.connect():
        return
    bot.register('hi', hi)
    bot.register('help', help)
    bot.register('stats', getStats)
    bot.register('fortune', getFortune)
    bot.register('seen <@([^>]+)>', seen)
    bot.run()

def parseSettings():
    filename = expanduser("~/.crashbot")
    config = ConfigParser.ConfigParser()
    config.read(filename)
    settings = dict(config.items('CrashBot'))
    return settings

if __name__ == '__main__':
    settings = parseSettings()
    if 'token' not in settings:
        print "No token in the settings file"
        sys.exit(1)
    bot = SlackBot(settings['token'])
    while True:
        try:
            main(bot)
        except KeyboardInterrupt:
            break
        except:
            traceback.print_exc()
            bot.saveState()
            time.sleep(5)
