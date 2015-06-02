# Helper exceptions
    
class CredentialsNotFoundError(Exception):
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)

class RTCInvalidCredentials(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value) 

class RTCSubmitError(Exception):
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)