from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password        
 
@app.route("/blog" , methods=['GET', 'POST'])
def blog():
    
    if request.args:
        id = request.args.get("id")
        blog = Blog.query.get(id)
        
        return render_template('entry.html' , blog=blog)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html' , blogs=blogs)

@app.route("/newpost" , methods=['POST' , 'GET'])
def add_blog():
    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        if len(blog_title) == 0 or len(blog_body) == 0:
            if len(blog_title) == 0:
                flash("Must enter a title for your blog.")
                return redirect("/newpost", blog_body=blog_body)
            if len(blog_body) == 0:
                flash("Must enter text for your blog.")
                return redirect("newpost", blog_title=blog_title)

        owner = User.query.filter_by(username=session['user']).first()
        new_blog = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()
        
        query_param_url = "/blog?id=" + str(new_blog.id)
        return redirect(query_param_url)

@app.route("/signup", methods=['POST' , 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(username) == 0 or len(password) == 0 or len(verify) == 0:
            flash("One or more fields are invalid.")
            return redirect('/signup')
        if len(username) < 3:
            flash("Username is too short.")
            return redirect('/signup')
        elif len(username) > 20:
            flash("Username is too long.")
            return redirect('/signup')
        elif " " in username:
            flash("Username can't contain a space.")
            return redirect('/signup')

        user_db_count = User.query.filter_by(username=username).count()
        if user_db_count > 0:
            flash("Username " + username + " already exists.")
            return redirect('/signup')

        if len(password) < 3 or len(password) > 20 or " " in password:
            flash("Not a valid password.")
            return redirect('/signup')

        if password != verify:
            flash("Passwords do not match.")
            return redirect('signup')

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        session['user'] = new_user.username

        return redirect('/newpost')
    else:
        return render_template('signup.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.username
                flash('Welcome back, ' + user.username)
                return redirect("/newpost")
            else:
                flash('Incorrect password.')
                return redirect("/login")
        flash('Username does not exist.')
        return redirect("/login")

@app.route("/", methods=['GET', 'POST'])
def index():

    if request.args:
        id = request.args.get("id")
        owner = User.query.get(id)
        blogs = Blog.query.filter_by(owner_id=owner)
        return render_template('blog.html' , blogs=blogs , owner=owner)
    else:
        users = User.query.all()
        return render_template('index.html' , users=users)

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/blog")

endpoints_without_login = ['login', 'signup', 'index', 'blog']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/login")

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == '__main__':
    app.run()