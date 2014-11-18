from flask.ext.heroku import Heroku
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask import render_template
from flask import request
from sqlalchemy.schema import Sequence
from sqlalchemy.sql import *
import os

app = Flask(__name__)
app.debug = True
#The following line is from https://github.com/kennethreitz/flask-heroku
#It took care of all the database stuff
heroku = Heroku(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
db.session.expire_on_commit = False


#####################################
#TODO:
#	API
#####################################


#####################################
#Current pages:
#/home leads to all the pages
#/reset resets the database
#####################################

class AttendanceRecord(db.Model):
    __tablename__ = 'attendancerecord'
    ar_id = db.Column(db.Integer, Sequence('ar_arid_seq', start=2, increment=1),unique=True,primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.eid'))
    person_id = db.Column(db.Integer, db.ForeignKey('person.pid'))
    person = db.relationship("Person", backref="attendance_records")

class Event(db.Model):
    __tablename__ = 'event'
    eid = db.Column(db.Integer, Sequence('event_eid_seq', start=2, increment=1), unique=True, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    host = db.Column(db.Text, nullable=False)
    loc = db.Column(db.Text, nullable=False, default='Luther')
    desc = db.Column(db.Text)
    month = db.Column(db.Text)
    date = db.Column(db.Text)
    attendees = db.relationship('AttendanceRecord', backref='event')

class Person(db.Model):
	__tablename__ = 'person'
	pid = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
	name = db.Column(db.Text, nullable=False)
	gradYr = db.Column(db.Integer)


chosenevents = []

def searchstudents():
	studentName = request.form['studentname']
	results = Person.query.filter_by(name=studentName).all()
	if len(results) > 0:
		#print(results[0])
		return ""+results[0].name+" Grad Year: "+str(results[0].gradYr)
	else:
		return "No students found!"

def addeventtodb():
	C_SUCCESS = "Successfully Added"
	C_FAILURE = "Your event already exists!"

	title = request.form['title']
	host = request.form['host']
	loc = request.form['loc']
	desc = request.form['desc']
	month = request.form['month']
	date = request.form['date']

	event_query = Event.query.filter_by(title=title).all()
	if len(event_query)>0:
		return C_FAILURE
	else:
		event = Event(title=title,host=host,loc=loc,desc=desc,month=month,date=date)
		db.session.add(event)
		db.session.commit()
		return C_SUCCESS

def addpersontodb():
	C_SUCCESS = "Successfully Added"
	C_FAILURE = "You already exist in the database!"
	personID = int(request.form['studentid'])
	name = request.form['name']
	gradYr = int(request.form['gradyr'])
	person_query = Person.query.filter_by(pid=personID).all()
	if len(person_query)>0:
		return "You already exist!"
	else:
		person = Person(pid=personID,name=name,gradYr=gradYr)
		db.session.add(person)
		db.session.commit()
		return C_SUCCESS

def joinevent():
	evtID = int(request.form['eventid'])
	personID = int(request.form['personid'])
	person=Person.query.filter_by(pid=personID).all()
	evt = Event.query.filter_by(eid=evtID).all()
	archeck = AttendanceRecord.query.filter_by(event_id=evtID,person_id=personID).all()
	ar = AttendanceRecord(event_id=evtID,person_id=personID)
	if len(archeck)>0:
		return "You've already joined this event!"
	elif len(person)<1:
		return "Person not found!"
	elif len(evt)<1:
		return "Event not found!"
	else:
		for i in range(len(evt)):
			evt[i].attendees.append(ar)
			db.session.commit()
		return "Event successfully joined!"

def buildar():
	arattendees = []
	evtID = int(request.form['eventid'])
	evt = Event.query.filter_by(eid=evtID).all()
	for i in range(len(evt)):
		ar = AttendanceRecord.query.filter_by(event_id=evtID).all()
		for j in range(len(ar)):
			print(ar[j].person_id)
			person=Person.query.filter_by(pid=ar[j].person_id).all()
			for k in range(len(person)):
				#This should only ever be one since it's a unique key
				arattendees.append(person[k].name)
	return arattendees

def buildevents():
	value = request.form.getlist("eventtype")
	monthvalue = request.form['month']
	eventslist = []
	evt1 = Event.query.filter_by(host="Sports", month=monthvalue).all()
	evt2 = Event.query.filter_by(host="Music", month=monthvalue).all()
	evt3 = Event.query.filter_by(host="School", month=monthvalue).all()
	for i in range(len(value)):

		if value[i] == "Sports":
			for j in range(len(evt1)):
				chosenevents.append(evt1[j].eid)
				eventslist.append(("ID# "+ str(evt1[j].eid)+ " " + evt1[j].desc + " " + evt1[j].date))

		if value[i] == "Music":
			for j in range(len(evt2)):
				chosenevents.append(evt2[j].eid)
				eventslist.append(("ID# " + str(evt2[j].eid)+ " " + evt2[j].desc + " " + evt2[j].date))
		if value[i] == "School":
			for j in range(len(evt3)):
				chosenevents.append(evt3[j].eid)
				eventslist.append(("ID# "+ str(evt3[j].eid)+ " " + evt3[j].desc + " " + evt3[j].date))

	return eventslist

@app.route('/searchforstudent', methods=['GET', 'POST'])
def searchforstudent():
	return render_template('searchstudent.html')

@app.route('/studentresults', methods=['GET','POST'])
def studentresults():
	entity = 'Student Search'
	results = searchstudents()
	print("here")
	return render_template('added.html',entity=entity,message=results)

@app.route('/searchevents', methods=['GET', 'POST'])
def events():
    return render_template('searchevents.html')

@app.route('/activitiesResults', methods=['GET', 'POST'])
def activitiesResults():

	eventslist = buildevents()
	if eventslist == []:
		eventslist.append("No events found.")
	return render_template('activitiesResults.html', events = eventslist )

@app.route('/attendancerecord',  methods=['GET', 'POST'])
def attendancerecord():
	print("Starting to build attendance records")
	arattendees = buildar()
	if len(arattendees) > 0:
		print("Found attendees")
	else:
		arattendees=['No attendees yet!']
	print("Attendance record built")
	return render_template('attendancerecord.html', eventattendees = arattendees)

@app.route('/evtjoined', methods=['GET', 'POST'])
def evtjoined():
	message = joinevent()
	entity = "Event Join"
	return render_template('added.html',entity=entity, message = message)

@app.route('/addperson',methods=['GET', 'POST'])
def addperson():
	return render_template('addperson.html')


@app.route('/personadded',methods=['GET','POST'])
def personadded():
	entity = "Person Added"
	message = addpersontodb()
	return render_template('added.html',entity=entity,message=message)

@app.route('/addevent',methods=['GET','POST'])
def addevent():
	return render_template('addevent.html')

@app.route('/eventadded',methods=['GET','POST'])
def eventadded():
	entity = "Event Added"
	message = addeventtodb()
	return render_template('added.html',entity=entity,message=message)


@app.route('/home',methods=['GET','POST'])
def home():
	return render_template('index.html')


@app.route('/reset')
def reset():
	db.drop_all()
	db.create_all()

	p1 = Person(pid=196080, name="Jacob Albee",gradYr="2015")
	p2 = Person(pid=389061, name="Kevin Bren",gradYr="2015")

	e1 = Event(title="Men's Baseball",host="Sports", desc = "Men's Baseball Home vs Wartburg", month="May", date= "05/10/15")
	e2 = Event(title="Women's Softball",host="Sports", desc = "Women's Softball Home vs Wartburg", month="April", date= "04/11/15")
	e3 = Event(title="Jazz Concert",host="Music", desc = "Jazz Band Concert at the CFL", month="May", date= "05/12/15")
	e4 = Event(title="Choir Concert",host="Music", desc = "Choir Band Concert at the CFL", month="May", date= "05/13/15")
	e5 = Event(title="Graduation",host="School", desc = "Graduation", month="May", date= "05/14/15")
	e6 = Event(title="Graduation Rehearsal",host="School", desc = "Graduation Rehearsal at Luther Football Field", month="May", date= "05/15/15")
	e7 = Event(title="Conference Track & Field Meet",host="Sports", desc = "Conference Track & Field Meet at I have no idea", month="May", date= "05/09/15")
	e8 = Event(title="Summer Classes",host="School", desc = "First day of summer classes", month="June", date= "06/05/15")
	e9 = Event(title="Christmas @ Luther",host="School", desc = "Christmas at Luther band/choir concert", month="December", date= "12/05/14")
	e10 = Event(title="Football vs. Simpson",host="Sports", desc = "Luther Football at Simpson", month="November", date= "11/09/14")
	e11 = Event(title="Resume and Cover Letter Workshop",host="School", desc = "Career Center", month="November", date= "11/15/14")
	e12 = Event(title="Art Show",host="School", desc = "In the CFA studio", month="December", date= "12/09/14")
	e13 = Event(title="Ochestra Concert",host="Music", desc = "In the CFL", month="November", date= "11/20/14")



	db.session.add_all([e1,e2,e3,e4,e5,e6,e7,e8,e9,e10,e11,e12,e13,p1,p2])
	ar = AttendanceRecord(event_id=1,person_id=196080)
	ar2 = AttendanceRecord(event_id=1,person_id=389061)
	e1.attendees.append(ar)
	e1.attendees.append(ar2)

	db.session.commit()
	return "Database was reset"


if __name__ == "__main__":
    app.run()
