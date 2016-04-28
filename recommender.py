import sys, os, math, operator, urllib, urllib2, json, io
from decimal import Decimal
from datetime import datetime, timedelta
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from operator import attrgetter

#app = Flask(__name__)
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

class User:
	def __init__(self, likes, dislikes, location, provider, startTime, endTime, ratings):
		self.likes = likes
		self.dislikes = dislikes
		self.location = location
		self.provider = provider
		self.startTime = startTime
		self.endTime = endTime
		self.ratings = ratings

class Show:
	def __init__(self, title, genre, rating, startTime, duration, provider, image):
		self.title = title
		self.genre = genre
		self.rating = rating
		self.startTime = startTime
		self.duration = duration
		self.provider = provider
		self.image = image
		
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
		showTitle = urllib.quote(show.title)
		url = 'http://www.omdbapi.com/?t='+showTitle+'&y=&plot=short&r=json'
		request = urllib2.Request(url)
		request_opener = urllib2.build_opener()
		response = request_opener.open(request) 
		response_data = response.read()
		json_result = json.loads(response_data)
		if 'imdbRating' in json_result.keys():
			if json_result['imdbRating'] != 'N/A':
				rating_list.append(int(float(json_result['imdbRating'])))
			else:
				rating_list.append(0)	
		else:
			rating_list.append(0)

	return rating_list
		
# def filter(location, date, startTime, userDuration, database):

def showPoster(show_list):
	posterlist =[]

	for show in show_list:
		showTitle = urllib.quote(show.title)
		url = 'http://www.omdbapi.com/?t='+showTitle+'&y=&plot=short&r=json'
		request = urllib2.Request(url)
		request_opener = urllib2.build_opener()
		response = request_opener.open(request) 
		response_data = response.read()
		json_result = json.loads(response_data)
		if 'Poster' in json_result.keys():
			if json_result['Poster'] != 'N/A':
				posterlist.append(str(json_result['Poster']))
			else:
				posterlist.append('http://www.makeupstudio.lu/html/images/poster/no_poster_available.jpg')
		else:
			posterlist.append('http://www.makeupstudio.lu/html/images/poster/no_poster_available.jpg')

	return posterlist


def filter(date, startTime, userDuration, database):
	tvList = []
	for show in database.shows:	
		if(show.startTime >= startTime):
			if ((show.startTime == startTime) and (show.duration <= userDuration)): #if show starts at the same time that the user is free, then the show can run the entire length that the user is free or less
				tvList.append(show)
			if (show.startTime > startTime): #if the show starts at a later time than the beginning of the users free time then check if it can be watched within the duration the user is free
				#print "start of time for show" + show.title + ":showstarttime - start time" + str(show.startTime) + " " + str(startTime) + " " + str(show.startTime - startTime) + " time= " + str(((show.startTime - startTime).seconds/60)) + " User duration= " + str(userDuration)
				diff = show.startTime - startTime #find out how long the shows starts after the beginnning of the user's free time (measured in hours so using ceiling)
				time = (diff.seconds/60)
				dur = userDuration #created temp variable so i wouldn't alter userDuration
				if ((dur - (time)) >= show.duration): #check if the item runs and finishes in good time even after including the shows delayed start 
					tvList.append(show)
	# for i in tvList:
		# print i.title + " " + str(i.rating)
	return tvList
		
def recommender(user, database):
	count = 0
	tvRecommend = []

	ratings = showRatings(database)
	i=0
	for show in database:
		if ratings[i] != 0:
			show.rating = ratings[i]
		
		tvRecommend.append(show)
		tvRecommend[i].rating = 0
		
		rated = False
		
		last = len(user.likes) - 1
		for userGenre in user.likes:
			if userGenre in show.genre:
				tvRecommend[i].rating = tvRecommend[i].rating + 1
				if(rated == False):
					tvRecommend[i].rating = tvRecommend[i].rating + show.rating*2
					rated = True
			elif(userGenre == user.likes[-1]):
				if(rated == False):
					tvRecommend[i].rating = tvRecommend[i].rating + show.rating
					rated = True
			else:
				continue;
		
		for genre in user.dislikes: # if user dislikes genre, get rid of it in results
			if genre in show.genre:
				del tvRecommend[i]
		i = i + 1
	
	
	
	# sorted(tvRecommend.items(), key=operator.itemgetter(1), reverse = True)
	
	# for keys in tvRecommend:
		# print keys + " : " + str(tvRecommend[keys])
	
	return tvRecommend

def printTopShows(dShows, fileName):
	showsList = []
	finalShowsList = []
	print len(dShows)
	i = 0
	while i < min(len(dShows),10):
		topShow = max(dShows, key=attrgetter('rating'))
		if not any(show.title == topShow.title for show in showsList):
			showsList.append(topShow)
		else:
			i = i - 1
		i = i + 1
		dShows.remove(topShow) 
	posterList = showPoster(showsList)
	j=0
	for show in showsList:
		finalShowsList.append(posterList[j] + ";" + show.title + " " + str(show.startTime.time()))
		j = j + 1
	return finalShowsList
		
def parseFile(fileName):
	list = []
	with open(fileName) as f:
		for line in f:
			data = line.split(";")
			startTime = datetime.strptime(data[3], "%Y-%m-%d %H:%M:%S")
			s = Show(data[0], data[1], int(data[2]), startTime, int(data[4]), data[5].rstrip(), "")
			
			list.append(s)
			
	db = Database(list)
	return db

def deleteMovies(fileName):
	with open(fileName) as oldfile, open('removedMovies.txt', 'w') as newfile:
		for line in oldfile:
			if not line.startswith("Movie"):
				newfile.write(line)

def parseUser(username):
	#User = likes, dislikes, location, provider, startTime, endTime, ratings
	#User file = zip,provider,likes,stime,etime,
	userFile = open(username + ".txt",'r')
	#rawUserRatings = open(username + "ratings.txt",'r')
	#userRatings = rawUserRatings.readline().split(';')
	userRatings = ""
	rawUserData = userFile.readline().split(';')
	likes = rawUserData[2].split(',')
	print len(rawUserData)
	if(len(rawUserData) <= 4):
		#rawUserData[3] = datetime.now.strftime("%Y-%m-%d %H:%M:%S")
		#rawUserData[4] = (datetime.now + 1).strftime("%Y-%m-%d %H:%M:%S")
		user = User(likes, "", rawUserData[0], rawUserData[1], datetime.now(), (datetime.now() + timedelta(days=1)), userRatings)
	else:
		user = User(likes, "", rawUserData[0], rawUserData[1], datetime.strptime(rawUserData[3], "%Y-%m-%d %H:%M:%S"), datetime.strptime(rawUserData[4], "%Y-%m-%d %H:%M:%S"), userRatings)
	return user
	


def recommend(username):
	user = parseUser(username)
	#time = datetime.now()
	today = datetime.today()
	fileName = "data.txt"
	db = parseFile(fileName)
	validShows = filter(today, user.startTime, ((user.endTime - user.startTime).seconds/60), db)
	#print validShows
	recommendedShows = recommender(user, validShows)
	outputedShows = printTopShows(recommendedShows, fileName)
	return outputedShows

@app.route('/test', methods=['POST', 'GET'])
def main():
	message = []
	if request.method == 'GET':

		# deleteMovies("app/data.txt")
		bobDate = datetime(2016, 4, 10, 19, 0, 0)
		Bob = User(["Comedy", "Sci-Fi", "Fantasy"], ["Mystery"], 77840, "suddenlink", "calendar", {"Doctor Who": 4, "Big Bang Theory": 3})
		
		# db = parseFile("removedMovies.txt")
		db = parseFile("test2.txt")
		
		validShows = filter("4-5-2016", bobDate, 180, db)
		recommendedShows = recommender(Bob, validShows)
		message = printTopShows(recommendedShows, "test2.txt")
		return render_template('questionaire.html')

	#request.form['questionaire']
	
	# deleteMovies("app/data.txt")
	bobDate = datetime(2016, 4, 10, 19, 0, 0)
	Bob = User(["Comedy", "Sci-Fi", "Fantasy"], ["Mystery"], 77840, "suddenlink", "calendar", {"Doctor Who": 4, "Big Bang Theory": 3})
	
	# db = parseFile("removedMovies.txt")
	db = parseFile("test2.txt")
	
	validShows = filter("4-5-2016", bobDate, 180, db)
	recommendedShows = recommender(Bob, validShows)
	printTopShows(recommendedShows)
	return render_template('questionaire.html')


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
	username = session["username"]
	shows = recommend(username)

	return render_template('calendar.html', shows = shows)

@app.route('/questionaire', methods=['POST', 'GET'])
def questionaire():
	likes = ""
	if request.method == 'GET':
		return render_template('questionaire.html')
	if request.method == 'POST':
		try:
			likes += "Action"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "Animated"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "Business"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "Comedy,Sitcom"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "Crime"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "Drama"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "Family"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "Fantasy"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "Horror"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "Children"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "News"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "Reality TV"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "Romance"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "Sci-Fi,Science"
		except KeyError:
			likes += "off"
		likes += ","
		try:
			likes += "Sports"
		except KeyError:
			likes += "off" 
		user = open(session["username"] + ".txt", 'a')
		user.write(likes + ';')
		return redirect(url_for('importcalender'))

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
