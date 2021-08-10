class DbConnectError(Exception):
    def __init__(self, msg='Database connection failed'):
        self.msg = msg
    
    def __str__(self):
        return self.msg