"""
User Model
Use to references and store state for Line Users.
"""

class User:

    STATE_NORMAL = 0
    STATE_SETTING = 1
    STATE_REMOTE = 2

    users = []

    def __init__(self, user_id):

        self.user_id = user_id
        self.state = self.STATE_NORMAL

        self.ssh_session = None # current router remote session
        self.current_router = None # current router id
        self.current_config = None # current config on router for SNMP module
        self.is_waiting_for_config = False # waiting for input from user to config router

        self.reply_token = None

        self.users.append(self)

    @classmethod
    def getUser(cls, user_id):
        for user in cls.users:
            if user.user_id == user_id:
                return user # return user object
        return User(user_id) # create new user object
