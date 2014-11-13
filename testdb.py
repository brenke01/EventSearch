from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask import render_template
from flask import request
from sqlalchemy.schema import Sequence
from sqlalchemy.sql import *

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

# attendencerecord = db.Table('attendencerecord',
#     db.Column('event_id',db.Integer, db.ForeignKey('event.eid')),
#     db.Column('person_id',db.Integer, db.ForeignKey('person.pid')),
#     db.Column('arid',db.Integer, Sequence('ar_id_seq', optional=False, start=0, increment=1),unique=True,primary_key=True)
#     )

class AttendenceRecord(db.Model):
    __tablename__ = 'attendencerecord'
    event_id = db.Column(db.Integer, db.ForeignKey('event.eid'),primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.pid'),primary_key=True)
    ar_id = db.Column('arid',db.Integer, Sequence('ar_id_seq', optional=False, start=0, increment=1),unique=True,primary_key=True)
    #person = db.relationship("Person", backref="attendence_record")
    person = db.relationship("Person", backref="attendance_records")

class Event(db.Model):
    __tablename__ = 'event'
    eid = db.Column(db.Integer, Sequence('event_eid_seq', start=0, increment=1), unique=True, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    host = db.Column(db.Text, nullable=False)
    loc = db.Column(db.Text, nullable=False, default='Luther')
    desc = db.Column(db.Text)
    month = db.Column(db.Text)
    date = db.Column(db.Text)
    #attendees = db.relationship('Person', secondary=attendencerecord,
     #                           backref=db.backref('people',lazy='dynamic'))
    attendees = db.relationship('AttendenceRecord', backref='event')

class Person(db.Model):
	__tablename__ = 'person'
	pid = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
	name = db.Column(db.Text, nullable=False)
	gradYr = db.Column(db.Integer)
	gender = db.Column(db.Text)

db.drop_all()
#db.create_all()
#@app.route('/', methods=['GET', 'POST'])
#def events():
db.create_all()
e1 = Event(title="Men's Baseball",host="Sports", desc = "Men's Baseball Home vs Wartburg", month="May", date= "1999,12,31")
p1 = Person(pid=6,name="Jacob Albee",gradYr="2015",gender="Male")
#ar1 = attendencerecord()
db.session.add_all([e1,p1])

e2 = Event(title="Test",host="Sports", desc = "Men's Baseball Home vs Wartburg", month="May", date= "1999,12,31")

ar = AttendenceRecord(event_id=0,person_id=6)
e2.attendees.append(ar)   
db.session.commit()
print("Yeah")
#return 'Yup'

#return "Printed"
#if __name__ == "__main__":
#    app.run()
