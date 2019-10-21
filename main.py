from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(360))
    body = db.Column(db.Text())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(360), unique = True)
    password = db.Column(db.String(360))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'] )
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if "user" in request.args:
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner=user).all()
        return render_template("singleUser.html", user_blogs=user_blogs)
    
    if "id" in request.args:
        blog_id = request.args.get('id')
        blogs = Blog.query.filter_by(id=blog_id).all()
        return render_template('singlepost.html', blogs=blogs)
        
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', page_title="All Blog Posts!", blogs=blogs)


@app.route('/login', methods=['POST', 'GET'])
def login():  

    username = ""
    username_error = ""
    password_error = ""
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html', username = username, username_error = username_error, password_error = password_error)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username = ""
    username_error = ""
    password_error = ""
    verify_error = ""

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username = username).first()

        if len(username) < 3:
            username_error = "Usernames must be longer than 3 characters."
            if username == "":
                username_error = "Please enter a desired username."

        if password != verify:
            password_error = "Passwords must match."
            verify_error = "Passwords must match."
            
        if len(password) < 3:
            password_error = "Password must be longer than 3 characters."
            if password == "":
                password_error = "Please enter a valid password."

        if password != verify:
            password_error = "Passwords must match."
            verify_error = "Passwords must match."

        if not username_error and not password_error and not verify_error:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                username_error = "Username is already claimed."

    return render_template('signup.html', username = username, username_error = username_error, password_error = password_error, verify_error = verify_error)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    blog_title = ""
    body= ""
    title_error = ""
    body_error = ""
    owner = User.query.filter_by(username = session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        body = request.form['body']

        if blog_title == "":
            title_error = "Please enter a title!"

        if body == "":
            body_error = "Please enter a post!"

        if not title_error and not body_error:
            new_post = Blog(blog_title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            blog_id = Blog.query.order_by(Blog.id.desc()).first()
            user = owner
        return redirect('/blog?id={}'.format(blog_id.id, user.username))
   
    return render_template('newpost.html',title = "Add a new post", blog_title = blog_title, body = body, title_error = title_error, body_error = body_error)

 
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == "__main__":
    app.run()
