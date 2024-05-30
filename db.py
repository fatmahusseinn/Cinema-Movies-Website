import sqlite3
import bcrypt
def connectDb(name='database.db'):
    return sqlite3.connect(name,check_same_thread=False)

connection = connectDb("store.db")
#---------------------------------
#users
def createUsersTable():
    cursor = connection.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    full_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
    )
    """
    cursor.execute(query)
    connection.commit()


# add user to db after register
def addUser(name,username,password):
    cursor = connection.cursor()
    query = """
    INSERT INTO users(full_name,username,password) VALUES (?,?,?)
    """
    cursor.execute(query,(name,username,password,))
    connection.commit()

def checkUsernameExists(username):
    cursor = connection.cursor()
    query = """
    SELECT id FROM users WHERE username = ?
    """
    cursor.execute(query,(username,))

    if cursor.fetchone():
        return True
    else:
        return False
    
def getUserId(username):
    cursor = connection.cursor()
    query = """
    SELECT id FROM users WHERE username = ?
    """
    cursor.execute(query,(username,))

    return cursor.fetchone()[0]
    
#when login , check if the username and password exactly matches
def loginUserDb(username,password):
    cursor = connection.cursor()
    query = """
    SELECT password FROM users WHERE username = ?
    """
    cursor.execute(query,(username,))
    stored_hashpassword = cursor.fetchone()
    if stored_hashpassword:
        if bcrypt.checkpw(password.encode(),stored_hashpassword[0].encode()): #tuple' object has no attribute 'encode' , password and hashed password must be both encoded
            return True
    return False


#-----------------------------------------
# Movie Uploader

def createUploadersTable():
    cursor = connection.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS uploaders(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    balance REAL DEFAULT 0
    )
    """
    cursor.execute(query)
    connection.commit()

def addUploader(name,email,password):
    cursor = connection.cursor()
    query = """
    INSERT INTO uploaders(full_name,email,password) VALUES (?,?,?)
    """
    cursor.execute(query,(name,email,password,))
    connection.commit()


def checkEmailExists(email):
    cursor = connection.cursor()
    query = """
    SELECT id FROM uploaders WHERE email = ?
    """
    cursor.execute(query,(email,))

    if cursor.fetchone():
        return True
    else:
        return False
    
def getUploaderId(email):
    cursor = connection.cursor()
    query = """
    SELECT id FROM uploaders WHERE email = ?
    """
    cursor.execute(query,(email,))
    return cursor.fetchone()[0]

    """
    uploader_id = cursor.fetchone()
    if uploader_id:
        return uploader_id[0]
    else: 
        return False
    """


def loginUploaderDb(email,password):
    cursor = connection.cursor()
    query = """
    SELECT password FROM uploaders WHERE email = ?
    """
    cursor.execute(query,(email,))
    stored_hashpassword = cursor.fetchone()
    if stored_hashpassword:
        if bcrypt.checkpw(password.encode(),stored_hashpassword[0].encode()): #tuple' object has no attribute 'encode' , password and hashed password must be both encoded
            return True
    return False

def getInfoUploader(uploader_id):
    cursor = connection.cursor()
    query = """
    SELECT * FROM uploaders WHERE id = ?
    """
    cursor.execute(query,(uploader_id,))
    return cursor.fetchone()



def update_Uploader_balance(id, new_balance):
    cursor = connection.cursor()
    query = """
    UPDATE uploaders SET Balance = ? WHERE id = ?
    """
    cursor.execute(query, (new_balance, id))
    connection.commit()


#--------------------------
def createMoviesTable():
    cursor = connection.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS movies(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uploader_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT NOT NULL,
    image_url TEXT NOT NULL,
    video_url TEXT NOT NULL,
    no_buyers REAL DEFAULT 0.0,
    FOREIGN KEY (uploader_id) REFERENCES uploaders (id) 
    )
    """
    #Real : Real Number
    cursor.execute(query)
    connection.commit()

def addMovie(uploader_id,movie_name,movie_price,movie_description,movie_image_path,movie_video_path):
    cursor = connection.cursor()
    query = """
    INSERT INTO movies(uploader_id,name,price,description,image_url,video_url) VALUES (?,?,?,?,?,?)
    """  
    cursor.execute(query,(uploader_id,movie_name,movie_price,movie_description,movie_image_path,movie_video_path,))
    connection.commit()

def getAllMovies(): #tlama get fa lazm t3ml return 3shan trg3 data
    cursor = connection.cursor()
    query = """SELECT * FROM movies"""
    cursor.execute(query)
    return cursor.fetchall()  # It will return List of Tuples aftet you loop by jinja you will access by index , I want to show it by practical

    #0 > movie_id , 1>uploader_id, 2>name, 3>price, 4>description, 5>image_url, 6>video_url , 7>nobuyers


def getMovie(movie_id): #search and get the info of movie by id
    cursor = connection.cursor()
    query = """ 
    SELECT * FROM movies WHERE id = ?
    """
    cursor.execute(query,(movie_id,))
    return cursor.fetchone() # that will return a tuple you can access it through index

def CreateBuyingMovie():
    cursor = connection.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS buy_movie(
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTERGER NOT NULL,
    movie_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (movie_id) REFERENCES movies (id)

    )

    """
    cursor.execute(query)
    connection.commit()


def orderBuyMovie(user_id,movie_id):
    cursor = connection.cursor()
    query = """
    INSERT INTO buy_movie (user_id,movie_id) VALUES (?,?)
    """
    cursor.execute(query,(user_id,movie_id,))
    connection.commit()

def checkMovieBoughtSameUser(user_id,movie_id):
    cursor = connection.cursor()
    query = """
    SELECT order_id FROM buy_movie WHERE user_id = ? AND movie_id = ?
    """
    cursor.execute(query,(user_id,movie_id))
    order = cursor.fetchone()
    if order:
        return True
    else: 
        return False
    

def getUploaderOfMovie(movie_id):
    cursor = connection.cursor()
    query = """
    SELECT uploader_id FROM movies WHERE id = ?
    """
    cursor.execute(query,(movie_id,))
    return cursor.fetchone()[0]

def updataBalanceUploader(movie_price,uploaderID):
    cursor = connection.cursor()
    query = """
    UPDATE uploaders SET balance = balance + ? WHERE id = ?
    """
    cursor.execute(query,(movie_price,uploaderID,))
    connection.commit()

def updateNoBuyers(movie_id):
    cursor = connection.cursor()
    query = """
    UPDATE movies SET no_buyers = no_buyers + 1 WHERE id = ?
    """
    cursor.execute(query,(movie_id,))
    connection.commit()

    
def get_user(username):
    cursor = connection.cursor()
    query = '''SELECT * FROM users WHERE username = ?'''
    cursor.execute(query, (username,))
    return cursor.fetchone()

def update_user_balance(username, new_balance):
    cursor = connection.cursor()
    query = """
    UPDATE users SET Balance = ? WHERE username = ?
    """
    cursor.execute(query, (new_balance, username))
    connection.commit()

def checkMovieNameFound(movie_name): #if found that will return the id of the movie
    cursor = connection.cursor()
    query = """
    SELECT id from movies WHERE name = ?
    """
    cursor.execute(query, (movie_name,))
    movie_id = cursor.fetchone()
    if movie_id:
        return movie_id[0]
    else:
        return False
    

#-----------------------------------------
# Comment Section (Create Table - Add comment - get all comments)

def comments_table():
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (movie_id) REFERENCES movies (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    connection.commit()


def add_comment(movie_id, user_id, text):
    cursor = connection.cursor()
    query = '''INSERT INTO comments (movie_id, user_id, text) VALUES (?, ?, ?)'''
    cursor.execute(query, (movie_id, user_id, text))
    connection.commit()

def get_comments_for_movie(movie_id):
    cursor = connection.cursor()
    query = '''
        SELECT  users.username, comments.text, comments.timestamp
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.movie_id = ?
    '''
    cursor.execute(query, (movie_id,))
    return cursor.fetchall()



#Not checked
def checkSameImage(filename):
    cursor = connection.cursor()
    query = """
    SELECT image_url from movies 
    """
    cursor.execute(query)
    all_image_urls = cursor.fetchall() #fetchone() or fetchall()
    pathoffilename = f"/static/uploads_posters/{filename}"
    for image in all_image_urls:
        if image[0] == pathoffilename:
            return True
        
    return False
    

def checkSameVideo(filename):
    cursor = connection.cursor()
    query = """
    SELECT video_url from movies 
    """
    cursor.execute(query)
    all_videos_urls = cursor.fetchall() #fetchone() or fetchall()
    pathoffilename = f"/static/uploads_videos/{filename}"
    for video in all_videos_urls:
        if video[0] == pathoffilename:
            return True
        
    return False


"""
def createRatingTable():

def rating_product():


def CreateCommentTable():

"""