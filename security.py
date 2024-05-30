import bcrypt
from flask import session
def hashPassword(password):
    #add salt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(),salt) # you must pass the password encoded
    return hashed_password.decode()


def check_isUploader():
    if 'is_uploader' in session:
        if session['is_uploader'] == True:
            return True
        else: 
            return False
    else:
        return False
    

def check_isUser():
    if 'is_user' in session:
        if session['is_user'] == True:
            return True
        else:
            return False
    else:
        return False
    

SECRET_KEY = "T&v$2PQsLx!9j8Rk@5gFw#ZmDp1YhCn*4uXy7eBdAa6VbGz3JqU"
    






























































































































