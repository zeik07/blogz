from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

	blog_id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120))
	body = db.Column(db.String(500))

	def __init__(self, title):
		self.title = title
		self.body = ""

def get_blogs():
    id = Blog.blog_id
    return db.session.query(id)

@app.route("/newpost")
def newpost():

    return render_template('newpost.html')

@app.route("/add" , methods=['POST'])
def add_blog():
    error = False
    title_error = ""
    blog_error = ""
    blog_title = request.form['title']
    blog_body = request.form['blog']
    if len(blog_title) == 0 or len(blog_body) == 0:
        if len(blog_title) == 0:
            error = True
            title_error = "Must enter a title for your blog."
        if len(blog_body) == 0:
            error = True
            blog_error = "Must enter text for your blog."
    if error == True:
        return render_template('newpost.html' , title_error=title_error , blog_error=blog_error , title=blog_title , blog=blog_body)

    title = Blog(blog_title)
    body = Blog(blog_body)
    db.session.add(title)
    db.session.add(body)
    db.session.commit()
    return render_template('blog.html')


@app.route("/", methods=['POST' , 'GET'])
def index():
    return render_template('blog.html' , blogs= get_blogs())


if __name__ == '__main__':
	app.run()