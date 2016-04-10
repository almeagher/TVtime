import sys, os, math, operator, datetime
from datetime import datetime

# timeSlot = day time, preference = list of genres, data = json whole tv list for that day

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
		
# def filter(location, date, startTime, userDuration, database):
def filter(date, startTime, userDuration, database):
	tvList = []
	for show in database.shows:
		# if(item.location == location and item.startTime >= startTime):
		if(show.startTime >= startTime):
			if ((show.startTime == startTime) and (show.duration <= userDuration)): #if show starts at the same time that the user is free, then the show can run the entire length that the user is free or less
				tvList.append(show)
			if (show.startTime > startTime): #if the show starts at a later time than the beginning of the users free time then check if it can be watched within the duration the user is free 
				diff = show.startTime - startTime #find out how long the shows starts after the beginnning of the user's free time (measured in hours so using ceiling)
				time = (diff.seconds//60)%60
				dur = userDuration #created temp variable so i wouldn't alter userDuration
				if ((dur - (time)) >= show.duration): #check if the item runs and finishes in good time even after including the shows delayed start 
					tvList.append(show)
	
	return tvList
		
def recommender(user, database):
	# tvList = []
	count = 0
	# for show in data:
		# if(airtime < timeSlot and showduration < duration):
			# del show
	tvRecommend = {}
	for show in database:
		showTitle = show.title
		tvRecommend[showTitle] = 0
		
		rated = False

		for userGenre in user.likes:
			if userGenre in show.genre:
				tvRecommend[showTitle] = tvRecommend[showTitle] + 1
				
				if(rated == False):
					tvRecommend[showTitle] = tvRecommend[showTitle] + show.rating*2
					rated = True
			else: 
				if(rated == False):
					tvRecommend[showTitle] = tvRecommend[showTitle] + show.rating
					rated = True
		# if user dislikes genre, get rid of it in results
		for bad in user.dislikes:
			if bad in show.genre:
				del tvRecommend[showTitle]
		
		
	sorted(tvRecommend.items(), key=operator.itemgetter(1), reverse = True)
	# tvRecommend.sort(key= itemgetter(1), reverse = True)
	 
	return tvRecommend

def printTopShows(dShows):
	print max(dShows, key=dShows.get)
	print dShows
		
def parseFile(fileName):
	list = []
	with open(fileName) as f:
		for line in f:
			 
			data = line.split(";")
			#year-mon-day hh:mm:ss
			startTime = datetime.strptime(data[3], "%Y-%m-%d %H:%M:%S")
			s = Show(data[0], data[1], int(data[2]), startTime, int(data[4]), data[5].rstrip())
			list.append(s)
			
	db = Database(list)
	return db

def main():
	# parseFile("test2.txt")
	
	
	bobDate = datetime(2016, 4, 9, 19, 0, 0)
	Bob = User(["comedy", "romance"], ["fantasy"], 77840, "suddenlink", "calendar", {"Doctor Who": 4, "Big Bang Theory": 3})
	
	# dw = Show("Doctor Who", "fantasy", 4, bobDate, 90, "cable")
	# bbt = Show("Big Bang Theory", "comedy", 2, bobDate, 30, "cable")
	# sh = Show("Sherlock", "mystery", 4, bobDate, 90, "cable")
	# got = Show("Game of Thrones", "fantasy", 2, bobDate, 30, "cable")
	# db = Database([dw, bbt, sh, got])
	db = parseFile("test2.txt")
	
	validShows = filter("4-5-2016", bobDate, 180, db)
	recommendedShows = recommender(Bob, validShows)
	printTopShows(recommendedShows)
	
		
if __name__ == '__main__':
	main()
	
# used hw0_part2 as reference