from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask import render_template

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)



posttags = db.Table('posttags',
    db.Column('tag_id',db.Integer, db.ForeignKey('tag.tag_id')),
    db.Column('post_id',db.Integer, db.ForeignKey('post.post_id'))
)



class Post(db.Model):
    __tablename__ = 'post'
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    author = db.Column(db.Text)
    post_text = db.Column(db.Text)
    tags = db.relationship('Tag', secondary=posttags,
                                backref=db.backref('tags',lazy='dynamic'))


class Tag(db.Model):
    __tablename__ = 'tag'
    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    desc = db.Column(db.Text)


db.drop_all()
db.create_all()

p1 = Post(post_id=1,title='First Post',author='Bren', post_text = 'This is my first post')
p2 = Post(post_id=2,title='Second Post',author='Bren', post_text = 'This is my second post')

db.session.add_all([p1,p2])

db.session.commit()

@app.route('/postdb', methods=['GET', 'POST'])
def postdb():
    return render_template('activitiesdb.html')

if __name__ == "__main__":
    app.run()