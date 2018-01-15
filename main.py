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
	body = db.Column(db.String())

	def __init__(self, title):
		self.title = title
		self.body = body

@app.route('/', methods=['POST', 'GET'])
def index():
	return render_template('index.html')













if __name__ == '__main__':
	app.run()