import sys, os, math, operator, datetime
from datetime import datetime

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

def main():
	# deleteMovies("app/data.txt")
	bobDate = datetime(2016, 4, 10, 19, 0, 0)
	Bob = User(["Comedy", "Sci-Fi", "Fantasy"], ["Mystery"], 77840, "suddenlink", "calendar", {"Doctor Who": 4, "Big Bang Theory": 3})
	
	# db = parseFile("removedMovies.txt")
	db = parseFile("test2.txt")
	
	validShows = filter("4-5-2016", bobDate, 180, db)
	recommendedShows = recommender(Bob, validShows)
	printTopShows(recommendedShows)
	
		
if __name__ == '__main__':
	main()
