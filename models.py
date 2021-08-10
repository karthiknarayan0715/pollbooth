class User:
    def __init__(self, username,  email, name, role):
        self.username = username
        self.email = email
        self.name = name
        self.role = role
        
class Teams:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Poll:
    def __init__(self, id, title, question, options, is_ended):
        self.id = id
        self.title = title
        self.question = question
        self.options = options
        self.is_ended = is_ended