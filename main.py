from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
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

@app.route("/signup", methods=['POST'])
def signup():
    error=False
    username_error = ""
    verify_error = ""
    email_error = ""
    username = request.form['username']
    password = request.form['password']
    verify = request.form['verify']
    email = request.form['email']
    userlist = User.query.all()

    if len(username) < 3:
        username_error = "Username is too short.".format(username)
        error=True
    elif len(username) > 20:
        username_error = "Username is too long.".format(username)
        error=True
    elif " " in username:
        username_error = "Username can't contain a space.".format(username)
        error=True
    elif username in userlist:
        username_error = "Username already exists.".format(username)
        error=True

    if len(password) < 3 or len(password) > 20 or " " in password:
        password_error = "Not a valid password."
        error=True

    if password != verify:
        verify_error = "Passwords do not match.".format(verify)
        error=True

    if error == True:
        return render_template('signup.html' , username=username , username_error=username_error , password_error=password_error , verify_error=verify_error)

    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()

    return render_template('newpost.html')


if __name__ == '__main__':
    app.run()