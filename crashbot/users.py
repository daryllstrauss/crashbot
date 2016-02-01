
import time
import atexit
import pickle

class SlackUsers(object):
    def __init__(self):
        self.users = dict()
        atexit.register(self.saveState)

    def saveState(self):
        with open("users.data", "w") as f:
            pickler = pickle.Pickler(f)
            pickler.dump(self.users)

    def loadState(self):
        try:
            with open("users.data", "r") as f:
                pickler = pickle.Unpickler(f)
                self.users = pickler.load()
        except:
            pass

    def update(self, user, state, channel=None):
        self.users[user] = {
            'state': state,
            'time': time.time(),
            'channel': channel
        }

    def get(self, user):
        return self.users.get(user, None)

    def count(self):
        return len(self.users)
