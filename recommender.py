import sys, os, math, operator, datetime, urllib, urllib2, json, io
from decimal import Decimal
from datetime import datetime
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for

#app = Flask(__name__)
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

class User:
	def __init__(self, likes, dislikes, location, provider, calendar, ratings):
		self.likes = likes
		self.dislikes = dislikes
		self.location = location
		self.provider = provider
		self.calendar = calendar
		self.ratings = ratings

class Show:
	def __init__(self, title, genre, rating, startTime, duration, provider):
		self.title = title
		self.genre = genre
		self.rating = rating
		self.startTime = startTime
		self.duration = duration
		self.provider = provider
		
class Database:
	def __init__(self, shows):
		self.shows = shows

#Given a list of tv show titles, it returns a list of ratings on a 
#scale of 1-10 from IMDb
#Example Input: ["Supernatural", "NCIS", "7th Heaven"] 
#Output: [8.6, 7.9, 5.1] 
def showRatings(show_list):
	rating_list = []

	for show in show_list:
		show = urllib.quote(show)
		url = 'http://www.omdbapi.com/?t='+show+'&y=&plot=short&r=json'
		request = urllib2.Request(url)
		request_opener = urllib2.build_opener()
		response = request_opener.open(request) 
		response_data = response.read()
		json_result = json.loads(response_data)
		rating_list.append(Decimal(json_result['imdbRating']))

	return rating_list
		
# def filter(location, date, startTime, userDuration, database):

def filter(date, startTime, userDuration, database):
	tvList = []
	for show in database.shows:	
		if(show.startTime >= startTime):
			if ((show.startTime == startTime) and (show.duration <= userDuration)): #if show starts at the same time that the user is free, then the show can run the entire length that the user is free or less
				tvList.append(show)
			if (show.startTime > startTime): #if the show starts at a later time than the beginning of the users free time then check if it can be watched within the duration the user is free 
				diff = show.startTime - startTime #find out how long the shows starts after the beginnning of the user's free time (measured in hours so using ceiling)
				time = (diff.seconds//60)%60
				dur = userDuration #created temp variable so i wouldn't alter userDuration
				if ((dur - (time)) >= show.duration): #check if the item runs and finishes in good time even after including the shows delayed start 
					tvList.append(show)
	# for i in tvList:
		# print i.title + " " + str(i.rating)
	return tvList
		
def recommender(user, database):
	count = 0
	tvRecommend = {}
	
	for show in database:
		showTitle = show.title
		tvRecommend[showTitle] = 0
		
		rated = False
		
		last = len(user.likes) - 1
		for userGenre in user.likes:
			# print "hello"
			if userGenre in show.genre:
				tvRecommend[showTitle] = tvRecommend[showTitle] + 1
				if(rated == False):
					tvRecommend[showTitle] = tvRecommend[showTitle] + show.rating*2
					rated = True
			elif(userGenre == user.likes[-1]):
				if(rated == False):
					tvRecommend[showTitle] = tvRecommend[showTitle] + show.rating
					rated = True
			else:
				continue;
		
		for genre in user.dislikes: # if user dislikes genre, get rid of it in results
			if genre in show.genre:
				del tvRecommend[showTitle]
	
	
	
	# sorted(tvRecommend.items(), key=operator.itemgetter(1), reverse = True)
	
	# for keys in tvRecommend:
		# print keys + " : " + str(tvRecommend[keys])
	
	return tvRecommend

def printTopShows(dShows):
	print dShows
	for i in range(3):
		topShow = max(dShows, key=dShows.get)
		print topShow + " :: " + str(dShows[topShow])
		del dShows[topShow]
		
def parseFile(fileName):
	list = []
	with open(fileName) as f:
		for line in f:
			data = line.split(";")
			startTime = datetime.strptime(data[3], "%Y-%m-%d %H:%M:%S")
			s = Show(data[0], data[1], int(data[2]), startTime, int(data[4]), data[5].rstrip())
			
			list.append(s)
			
	db = Database(list)
	return db

def deleteMovies(fileName):
	with open(fileName) as oldfile, open('removedMovies.txt', 'w') as newfile:
		for line in oldfile:
			if not line.startswith("Movie"):
				newfile.write(line)

@app.route('/test', methods=['POST', 'GET'])
def main():
	message = ""
	if request.method == 'GET':

		# deleteMovies("app/data.txt")
		bobDate = datetime(2016, 4, 10, 19, 0, 0)
		Bob = User(["Comedy", "Sci-Fi", "Fantasy"], ["Mystery"], 77840, "suddenlink", "calendar", {"Doctor Who": 4, "Big Bang Theory": 3})
		
		# db = parseFile("removedMovies.txt")
		db = parseFile("test2.txt")
		
		validShows = filter("4-5-2016", bobDate, 180, db)
		recommendedShows = recommender(Bob, validShows)
		printTopShows(recommendedShows)
		return render_template('questionaire.html', message=message)

	#request.form['questionaire']
	
	# deleteMovies("app/data.txt")
	bobDate = datetime(2016, 4, 10, 19, 0, 0)
	Bob = User(["Comedy", "Sci-Fi", "Fantasy"], ["Mystery"], 77840, "suddenlink", "calendar", {"Doctor Who": 4, "Big Bang Theory": 3})
	
	# db = parseFile("removedMovies.txt")
	db = parseFile("test2.txt")
	
	validShows = filter("4-5-2016", bobDate, 180, db)
	recommendedShows = recommender(Bob, validShows)
	printTopShows(recommendedShows)
	try:
		message += str(request.form['Checkbox1'])
	except KeyError:
		message += "off"
	message += ","
	try:
		message += str(request.form['Checkbox2'])
	except KeyError:
		message += "off"
	message += ","
	try:
		message += str(request.form['Checkbox3'])
	except KeyError:
		message += "off"
	message += ","
	try:
		message += str(request.form['Checkbox4'])
	except KeyError:
		message += "off"
	message += ","
	try:
		message += str(request.form['Checkbox5'])
	except KeyError:
		message += "off"
	message += ","
	try:
		message += str(request.form['Checkbox6'])
	except KeyError:
		message += "off"
	message += ","
	try:
		message += str(request.form['Checkbox7'])
	except KeyError:
		message += "off"
	message += ","
	try:
		message += str(request.form['Checkbox8'])
	except KeyError:
		message += "off"
	message += ","
	try:
		message += str(request.form['Checkbox9'])
	except KeyError:
		message += "off"
	message += ","
	try:
		message += str(request.form['Checkbox10'])
	except KeyError:
		message += "off"
	message += ","
	try:
		message += str(request.form['Checkbox11'])
	except KeyError:
		message += "off"
	message += ","
	try:
		message += str(request.form['Checkbox12'])
	except KeyError:
		message += "off"
	message += ","
	try:
		message += str(request.form['Checkbox13'])
	except KeyError:
		message += "off"
	message += ","
	try:
		message += str(request.form['Checkbox14'])
	except KeyError:
		message += "off"
	message += ","
	try:
		message += str(request.form['Checkbox15'])
	except KeyError:
		message += "off"
	return render_template('questionaire.html', message=message)


@app.route('/', methods=['POST', 'GET'])
def index():

	return render_template('index.html')

@app.route('/login' , methods=['POST', 'GET'])
def login():
	error = ""
	mockeddatafilename = ""
	if request.method == 'GET':

		return render_template('login2.html')

	if request.method == 'POST':
		if (str(request.form["username"]) is not None and str(request.form["submit-btn"]) is not None and str(request.form["password"]) is not None):
			if(request.form["submit-btn"] == "Login"): 
				with open("users.txt") as usersfile:
					for line in usersfile:
						if str(request.form["username"]) in line:
							if str(request.form["password"]) in line.split(';')[1]:
								session['username'] = request.form['username']
								return redirect(url_for('calendar'))
				error = "user/password pair not found"
			if(request.form["submit-btn"] == "Register"):
				#add user
				users = open("users.txt", 'a')
				users.write("\n" + request.form["username"] + ";" + request.form["password"])
				#add users info file
				userfile = open(request.form["username"] + ".txt", 'w')
				#zipcode, tv provider, likes(in questionair)
				userfile.write(request.form["zipcode"] + ";" + request.form["provider"] + ";");
				session["username"] = request.form["username"]
				return redirect(url_for("questionaire"))
		else:
			error = "invalid data entry"
		return render_template('login2.html', error=error)

@app.route('/calendar', methods=['POST', 'GET'])
def calendar():

	return render_template('calendar.html')

@app.route('/questionaire', methods=['POST', 'GET'])
def questionaire():
	likes = ""
	if request.method == 'GET':
		return render_template('questionaire.html')
	if request.method == 'POST':
		try:
			likes += "action"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "adultanimation"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "business"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "comedy"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "crime"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "drama"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "family"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "fantasy"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "horror"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "kidsanimation"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "news"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "reality"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "romance"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "scifi"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "sports"
		except KeyError:
			likes += "off" 
		user = open(session["username"] + ".txt", 'a')
		user.write(likes + ';')
		return redirect(url_for('calendar'))

@app.route('/importcalendar', methods=['POST', 'GET'])
def importcalender():

	if request.method == 'GET':

		return render_template('importcalendar.html')

	if request.method == 'POST':

		return redirect(url_for('calendar'))
	
@app.route('/logout', methods=['POST', 'GET'])
def logout():
	session.pop("username", None)
	return redirect(url_for('login'))
		
if __name__ == '__main__':
	app.run(debug=True)
