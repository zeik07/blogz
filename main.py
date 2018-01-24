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
 
@app.route("/blog" , methods=['GET'])
def index():
    
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
        error = False
        title_error = ""
        body_error = ""
        blog_title = request.form['title']
        blog_body = request.form['body']
        if len(blog_title) == 0 or len(blog_body) == 0:
            if len(blog_title) == 0:
                error = True
                title_error = "Must enter a title for your blog."
            if len(blog_body) == 0:
                error = True
                body_error = "Must enter text for your blog."
        if error == True:
            return render_template('newpost.html' , title_error=title_error , body_error=body_error , title=blog_title , body=blog_body)

        new_blog = Blog(blog_title, blog_body)
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

        return render_template('newpost.html')
    else:
        return render_template('signup.html')

endpoints_without_login = ['login', 'signup']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/signup")

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == '__main__':
    app.run()