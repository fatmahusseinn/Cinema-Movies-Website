from db import *
from validators import *
from security import *
from flask import Flask , request , redirect, render_template,flash, url_for, session ,send_file
import sqlite3
import hashlib
import bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os



app = Flask(__name__)
app.secret_key = SECRET_KEY
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["50 per minute"])
#user (guest)

@app.route("/login",methods=["GET","POST"])
@limiter.limit("10 per minute") #decorator , uses the limiter object above which is object from Class Limiter
def loginUser():
    if request.method == "GET":
        return render_template("signin.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if loginUserDb(username,password):
            session['logged_in'] = True
            session['is_user'] = True
            session['is_uploader'] = False
            session['username'] = username
            return redirect("/home")
            #return render_template("task.html",username=username,password=password)
        else:
            flash("Wrong username of password","danger")
            return render_template("signin.html")
    


@app.route("/register",methods=["GET","POST"])
@limiter.limit("10 per minute") #n3mlha fy pages ely mmkn mn khlalha y3ml brute forcing
def registerUser():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        full_name = request.form["name"] #mwgod fy html name attribute
        username = request.form["username"]
        password = request.form["password"]
        print (password)
        if checkUsernameExists(username):
            flash("There is an account by this user","danger")
            return render_template("register.html")
        if (not(check_password_length(password) and check_password_characters(password))):
            flash("Invalid Password, Password should contain digits , lowercase character , upercase characters ,special characters","danger")
            return render_template("signup.html")

        hashed_password = hashPassword(password)
        addUser(full_name,username,hashed_password)     
        return redirect("/login")




#Movie Uploader
@app.route("/login-uploader",methods=["GET","POST"])
@limiter.limit("10 per minute")
def loginUploader():
    if request.method == "GET":
        return render_template("signin-uploader.html")
    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if not checkEmail(email):
            flash("Invalid Email or Password","danger")
            return render_template("signin-uploader.html")


        if loginUploaderDb(email,password):
            session['logged_in'] = True
            session['is_uploader'] = True
            session['is_user'] = False
            session['email'] = email
            return redirect("/home")
            #return render_template("task.html",username=username,password=password)
        else:
            flash("Wrong username of password","danger")
            return render_template("signin-uploader.html")

@app.route("/register-uploader",methods=["GET","POST"])
@limiter.limit("10 per minute")
def registerUploader():
    if request.method=="GET":
        return render_template("signup-uploader.html")
    elif request.method == "POST":
        full_name = request.form["name"] #mwgod fy html name attribute
        email = request.form["email"]
        password = request.form["password"]

        if checkEmailExists(email):
            flash("There is an account by this user","danger")
            return render_template("signup-uploader.html")
        
        if not checkEmail(email):
            flash("Invalid Email or Password","danger")
            return render_template("signin-uploader.html")
        

        if (not(check_password_length(password) and check_password_characters(password))):
            flash("Invalid Password, Password should contain digits , lowercase character , upercase characters ,special characters","danger")
            return render_template("signup-uploader.html")

        hashed_password = hashPassword(password)
        addUploader(full_name,email,hashed_password)     
        return redirect("/login-uploader")


@app.route("/",methods = ["GET"])
def root_dir(): #index : home : root
    return redirect("/home")


@app.route("/home",methods=["GET","POST"])
def home():
    if check_isUploader():
        return render_template("home_uploader.html",uploader=getInfoUploader(getUploaderId(session['email'])))
    if check_isUser():
        return render_template("view_movies.html",movies = getAllMovies())
    return "Forbidden,You dont have access to this page , Please log in" #if he is not user and not uploader
   
    
@app.route("/upload-movie",methods=["GET","POST"])
@limiter.limit("10 per minute")
def uploadMovie():
    if request.method == "GET":
        if check_isUploader():
            return render_template("upload-movie.html") 
        return "Forbidden,You dont have access to this page , Please log in"
            
    elif request.method == "POST":
        #LAZM FY HTML YKON FORM FEHA MULTIPART 3shan file ytb3t 3la kza request
        if not check_isUploader():
            return "Forbidden,You dont have access to this page , Please log in"

        movie_name = request.form["movie_name"]
        movie_price = request.form["price"]
        movie_description = request.form["description"]
        movie_image = request.files["movie_image"]
        movie_video = request.files["movie_video"]

        #check if user didnt upload image or video or name is empty
        # NONE returns FALSE
        if not movie_image or movie_image.filename=='':
            flash("Image Is Required", "danger")
            return render_template("upload-movie.html")
        
        if not movie_video or movie_video.filename == '':
            flash("Video Is Required", "danger")
            return render_template("upload-movie.html")
        
        #Check the extension of image and video and the size

        if not (allowed_fileImage(movie_image.filename)) or not allowed_file_sizeImage(movie_image) :
            flash("Invalid File is Uploaded", "danger")
            return render_template("upload-movie.html")
			
        
        if not (allowed_fileVideo(movie_video.filename)) or not allowed_file_sizeVideo(movie_video):
            flash("Invalid File is Uploaded", "danger")
            return render_template("upload-movie.html")

        #movie_image and movie_video object has 1 attributes which is ".filename" and 1 method which is ".save()"

        #Save Movie Image
        movie_image_url = f"uploads_posters/{movie_image.filename}" #path
        movie_image.save(os.path.join("static",movie_image_url))

        #Save Movie Video
        movie_video_url = f"uploads_videos/{movie_video.filename}"
        movie_video.save(os.path.join("static",movie_video_url))

        uploader_id = getUploaderId(session['email'])

        print(uploader_id,movie_name,movie_price,movie_description,movie_image_url,movie_video_url)
        addMovie(uploader_id,movie_name,movie_price,movie_description,movie_image_url,movie_video_url)
        return redirect(url_for('home'))


@app.route("/movie/<movie_id>",methods=["GET","POST"])
def view_movie(movie_id):
    if not check_isUser():
        flash("Forbidden,you dont have access to this page","Danger")
        return redirect(url_for('home'))
    comments = get_comments_for_movie(movie_id)
    print("Comments:", comments)
    return render_template("movie_page.html",movie=getMovie(movie_id),show_buy_button=True,comments=comments)

@app.route("/buy-movie/<movie_id>",methods=["POST"])
def buyMovie(movie_id):
    if not check_isUser():
        flash("Forbidden,you dont have access to this page","Danger")
        return redirect(url_for('home'))
    #movie = getMovie(movie_id)
    #show_hidden_button = False
    movieid = request.form['id']
    movie_ = getMovie(movieid)
    user_id = getUserId(session['username'])
    print(user_id,movie_[0],movie_id)
    #3ayzen nzwd balance bta3 uploader ely rag3 movie dh w n3mlh update in database
    # 3ayzen n3ml check hoa eluser dh eshtra movie dy 2bl kda wla laa
    # 3ayzen lw mshtrhash kbl kda ndef order dh fy table bta3 add order

    check_boughtbefore = checkMovieBoughtSameUser(user_id,movie_id)
    comments = get_comments_for_movie(movie_id)
    print("Comments:", comments)
    if check_boughtbefore:
        flash("You bought this movie before","Danger")
        return render_template("movie_page.html",show_hidden_button=True,movie=getMovie(movie_id),show_buy_button=False,comments=comments)
    
    # lw wsl hna that means en awl mra yshtry movie dy
    orderBuyMovie(user_id,movie_[0])
    uploader_id = getUploaderOfMovie(movie_[0]) # or = movie_[1]
    updataBalanceUploader(movie_[3],uploader_id)
    updateNoBuyers(movie_[0])
    
    return render_template("movie_page.html",show_hidden_button=True,movie=getMovie(movie_id),show_buy_button=False,comments=comments)


# Route to download the sample text file
@app.route('/download/<movie_id>',methods=["GET"]) #get
def download_video(movie_id):
    if not check_isUser():
        flash("Forbidden,you dont have access to this page","Danger")
        return redirect(url_for('home'))
    movie = getMovie(movie_id)
    file_path = movie[6]  # Path to your file to be downloaded
    return send_file(file_path, as_attachment=True)

@app.route('/logout')
def logout():
	session.pop('username', None)
	session.pop('logged_in', None)
	session.pop('is_uploader', None)
	session.pop('is_user', None)
	session.pop('email', None)
	return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if check_isUploader() :
        uploaders_info = getInfoUploader(getUploaderId(session["email"]))
        if uploaders_info:
            return render_template("view_profile.html", uploader=uploaders_info)

    flash("You are Not Logged In", "danger")
    return redirect(url_for("loginUser"))

@app.route('/withdraw')
def withdraw():
    if check_isUploader():
        uploaders_info =  getInfoUploader(getUploaderId(session["email"]))
        update_Uploader_balance(getUploaderId(session["email"]), 0)
        flash(f"Withdrawn successfully. New balance: 0$", "success")
        return render_template("withdraw.html", uploader=uploaders_info)
    
    flash("You are Not Logged In", "danger")
    return redirect(url_for("loginUser"))


@app.route("/search",methods=["POST"])
def seachByName():
    movie_name = request.form["search_input"]
    movieid = checkMovieNameFound(movie_name)
    if movieid: #if there is id for movie
        return redirect(url_for('view_movie', movie_id=movieid))
    else: #if the movie name has no id that means it is not in movie table
        return "Sorry We dont have this movie"
    

@app.route('/add-comment/<movie_id>', methods=['POST'])
def addComment(movie_id):
    text = request.form['comment']
    user_id = getUserId(session['username'])
    add_comment(movie_id, user_id, text)
    comments = get_comments_for_movie(movie_id) 
    return render_template("movie_page.html", movie=getMovie(movie_id), show_buy_button=True, comments=comments)






if __name__ == "__main__":
    createUsersTable()
    createUploadersTable()
    createMoviesTable()
    CreateBuyingMovie()
    comments_table()
    if session: #lw session object mwgoda (Cookies ely esmha session)
        session.pop('username', None)
        session.pop('logged_in', None)
        session.pop('is_uploader', None)
        session.pop('is_user', None)
        session.pop('email', None)
    app.run(debug=True)