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

	def __init__(self, title, body):
		self.title = title
		self.body = body

def get_blogs():
    id = Blog.blog_id
    return Blog.query.all()

@app.route("/newpost")
def newpost():

    return render_template('newpost.html')

@app.route("/blog" , methods=['POST'])
def add_blog():
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
    
    return render_template('entry.html' , blog= db.session.query(Blog).order_by(Blog.blog_id.desc()).first())

@app.route("/")
@app.route("/blog", methods=['GET'])
def index():
    
    if request.args:
        blog_id = request.args.get("id")
        blog = Blog.query.get(blog_id)

        return render_template('entry.html' , blog=blog)

    return render_template('blog.html' , blogs= get_blogs())


if __name__ == '__main__':
	app.run()