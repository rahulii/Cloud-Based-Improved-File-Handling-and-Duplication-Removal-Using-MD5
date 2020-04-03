from flask import Flask,render_template,flash, redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/rahul/Downloads/database.db'
db = SQLAlchemy(app)

app.secret_key = "super secret key"

class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))

class user_files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    fileName = db.Column(db.String(200))
    md5 = db.Column(db.String(200))

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/deletefile",methods=["GET", "POST"])
def deletefile():
    fileName = request.form.get('delete')
    
    return render_template("home.html")


@app.route("/viewRecords")
def records():
    all_files=[]
    files = user_files.query.filter_by(username=session.get('user')).all()
    for file in files:
        all_files.append(file.fileName)
    return render_template("viewRecords.html",len = len(all_files),records=all_files)

@app.route("/home")
def home():
    username = request.args.get('user')
    return render_template("home.html",user=username)


@app.route("/login",methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        
        login = user.query.filter_by(username=uname, password=passw).first()
        if login is not None:
            session['user'] = uname
            return redirect(url_for("home",user=uname))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']

        register = user(username = uname, email = mail, password = passw)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")

@app.route('/upload')  
def upload():
    username = session.get('user')  
    return render_template('file_upload_form.html',user=username)

@app.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':  
        f = request.files['file']
        img_key = hashlib.md5(f.read()).hexdigest()
        check = user_files.query.filter_by(md5=img_key).first()
        if check is None: 
            f.save(f.filename)
            file = user_files(username = session.get('user'),fileName = f.filename,md5=img_key)
            db.session.add(file)
            db.session.commit()
            return render_template("success.html", name = f.filename + " successfully uploaded")
        return render_template("success.html", name = f.filename + " already exists")  
  


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
