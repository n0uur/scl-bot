"""User Model
Use to references and store state for Line Users.
"""

class User:

    users = []

    def __init__(self):
        
        User.users.append(self)

    @classmethod
    def findUser(cls):
        pass
