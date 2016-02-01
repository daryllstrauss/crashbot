
import json
import re
import time
import atexit
import pickle
from slackclient import SlackClient
from users import SlackUsers


class SlackBot(object):
    version = "1.0"

    def __init__(self, token):
        self.token = token
        self.sc = SlackClient(token)
        self.rules = []
        self.stats = dict()
        self.users = SlackUsers()
        atexit.register(self.saveState)
        self.loadState()

    def loadState(self):
        try:
            with open("bot.data", "r") as f:
                pickler = pickle.Unpickler(f)
                self.stats = pickler.load()
        except:
            pass
        if 'version' not in self.stats:
            self.stats['version'] = self.version
        self.stats['startTime'] = time.time()
        if 'bornOn' not in self.stats:
            self.stats['bornOn'] = self.stats['startTime']
        self.stats['count'] = 0
        self.users.loadState()

    def saveState(self):
        with open("bot.data", "w") as f:
            pickler = pickle.Pickler(f)
            pickler.dump(self.stats)
        self.users.saveState()

    def connect(self):
        if self.sc.rtm_connect():
            self.me = self.call('auth.test')
            self.me['pat'] = re.compile('<@'+self.me['user_id']+'>')
            return True
        return False

    def call(self, *args, **kwargs):
        return json.loads(self.sc.api_call(*args, **kwargs))

    def run(self):
        while True:
            messages = self.sc.rtm_read()
            if messages:
                print messages
                self.handle_messages(messages)
            time.sleep(1)

    def handle_messages(self, messages):
        for msg in messages:
            if msg['type'] == 'message':
                self.handle_message(msg)
            if msg['type'] == 'presence_change':
                self.handle_presence(msg)
            if msg['type'] == 'user_typing':
                self.handle_typing(msg)

    def handle_message(self, msg):
        if 'text' not in msg:
            return
        for rule in self.rules:
            if 'user' in msg and msg['user'] == self.me['user_id']:
                continue
            if ('me' in rule and
                    msg['channel'][0] != 'D' and
                    not self.me['pat'].search(msg['text'])):
                continue
            m = rule['pat'].search(msg['text'])
            if m:
                rule['func'](self, msg, m)
                self.stats['count'] += 1

    def handle_presence(self, msg):
        if msg['presence'] == 'active':
            self.users.update(msg['user'], 'active')

        elif msg['presence'] == 'away':
            self.users.update(msg['user'], 'away')

    def handle_typing(self, msg):
        self.users.update(msg['user'], 'active', msg['channel'])

    def addRule(self, pat, func, me):
        self.rules.append({'pat': pat, 'func': func, 'me': me})

    def respond(self, msg, text):
        if msg['channel'][0] != 'D':
            greet = '<@'+msg['user']+'> '
        else:
            greet = ''
        self.call(
            'chat.postMessage', channel=msg['channel'], as_user=True,
            text=greet+text)

    def register(self, pat, func, patFlags=re.IGNORECASE):
        self.addRule(re.compile(pat, patFlags), func, True)


# def respond_to(bot, matchstr, flags=0):
#     def wrapper(func):
#         bot.addRule(re.compile(matchstr, flags), func, True)
#         return func
#     return wrapper
