import os,json
import requests
from flask import Flask, session,request,render_template,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    
    return render_template("signup.html")
@app.route("/sign")
def sign():
    return render_template("signin.html")

@app.route("/check",methods=["POST"])
def check():
    name=request.form.get("name")
    username= request.form.get("username")
    password= request.form.get("password")
    r_password=request.form.get("r_password")
    
    #condition check
    if db.execute("SELECT * FROM users WHERE username = :username ",{"username": username }).rowcount == 1:
        return render_template("signup.html",message="username exist")
    if password != r_password:
        return render_template("signup.html",message="password does not match")
    #if name == None:
    #   return render_template("signup.html",message="enter the name")
    
    #database entry
    db.execute("INSERT INTO users ( username , password , name ) VALUES ( :username , :password , :name )",
        {"username": username,"password":password,"name":name})
    db.commit()
    
    return render_template("signup.html",message="succesfully registered now sign in")
    #if everthing is correct then it will show succes
    #user have to click on sign in button then only he will go to login page
    #index will have a link of going directly to signin.html page that will call signup to check
    #3 files 
    # index.html-signup
    # signin.html
    # main.html -main web page after login


@app.route("/signin", methods=["POST"])
def signin():
    #signin

    username= request.form.get("username")
    password= request.form.get("password")
    if db.execute("SELECT * FROM users WHERE username = :username ",{ "username" : username }).rowcount == 1 :
        if db.execute("SELECT * FROM users WHERE password = :password ",{ "password" :password }).rowcount == 1 :
            if request.method == "POST":  
                session['username']=request.form['username']  
            return render_template("main.html")
    
    return render_template("signin.html",message="username or password incorrect")

@app.route('/logout')  
def logout():  
    if 'username' in session:  
        session.pop('username',None)  
        return render_template('signup.html')  
    else:  
        return render_template('signup.html')  



@app.route("/search",methods=["POST"])
def search():
    
    bname=request.form.get("bname")
    bname='%' + bname + '%'
    
    books=db.execute("select * from books where isbn like :bname or title like :bname or author like :bname LIMIT 10",{"bname":bname})
    #print(books)
    books=books.fetchall()
    return render_template("main.html",books=books)

@app.route("/search/<int:book_title>")
def book(book_title):

    books = db.execute("SELECT * FROM books WHERE book_id = :id", {"id": book_title}).fetchone()
    isbn_no=db.execute("select isbn from books where book_id = :id", {"id":book_title}).fetchone()
    reviews=db.execute("select r from review where b_id = :id ",{"id":book_title}).fetchall()
    #reviews=db.execute("select * from books inner join review on review.b_id=:book_id limit 5",{"book_id":books.book_id}).fetchall()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "AUQ9LyQCff270Hc3Nr6FIw", "isbns": isbn_no})
    data=res.json()
    data=data['books'][0]
    data=data['average_rating']
    return render_template('book_info.html', books=books,reviews=reviews,data=data)

@app.route("/search/<int:book_title>/review",methods=['POST'])
def reviews_1(book_title):

    books = db.execute("SELECT * FROM books WHERE book_id = :id", {"id": book_title}).fetchone()
    isbn_no=db.execute("select isbn from books where book_id = :id", {"id":book_title}).fetchone()
    reviews=db.execute("select r from review where b_id = :id ",{"id":book_title}).fetchall()
    #reviews=db.execute("select * from books inner join review on review.b_id=:book_id limit 5",{"book_id":books.book_id}).fetchall()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "AUQ9LyQCff270Hc3Nr6FIw", "isbns": isbn_no})
    data=res.json()
    data=data['books'][0]
    data=data['average_rating']

    s_r=request.form.get("review")
    u = session["username"]
    if db.execute("select * from review where b_id= :id and id_user= :user",{"id":book_title,"user":u}).rowcount==1:
        return render_template("book_info.html",books=books,reviews=reviews,data=data,message="Review already written")

    db.execute("INSERT INTO review ( b_id , r,id_user ) VALUES ( :book_title , :s_r , :id )",
    {"book_title": book_title,"s_r":s_r,"id":u})
    db.commit()
    reviews=db.execute("select r from review where b_id = :id ",{"id":book_title}).fetchall()
    return render_template("book_info.html",books=books,reviews=reviews,data=data)

@app.route("/api/<isbn>", methods=['GET'])
def api(isbn):

    row=db.execute("Select * from books where isbn=:id",{"id":isbn})
    tmp = row.fetchone()
    result = dict(tmp.items())
    #result['average_score'] = float('%.2f'%(result['average_score']))

    return jsonify(result)



