#(examples)http://api.tvmaze.com/schedule?country=US&date=2014-12-01
#http://api.tvmedia.ca/tv/v4/lineups/41626/listings?api_key=8d1f9b837ede40c9acb3f1d793b3a15a

import sys
import os
import operator
import urllib
import requests
import json
from requests.auth import HTTPBasicAuth

API_KEY = '8d1f9b837ede40c9acb3f1d793b3a15a'
ID_LOCATION = 'id_location.txt'

class ApiQuery:
	def __init__(self, query, start_time, end_time, search_date, result_num):
		self.query = query
		self.search_type = start_time
		self.search_zip = end_time
		self.search_date = search_date
		self.result_num = result_num


# class LocationIdentifier:
# 	def __init__(self, zip_code, lineups_id, provider):
# 		self.zip_code = zip_code
# 		self.lineups_id = lineups_id
# 		self.provider = provider


# def api_location_id_finder(api_query):

# 	url = 'http://api.tvmedia.ca/tv/v4/lineups/41626/listings?api_key=' + API_KEY 
# 	response_data = requests.get(url) 
# 	json_result = response_data.json()
# 	print json_result
# 	open_output_file = open(ID_LOCATION, 'a') 
# 	for result in json_result:
# 		print result
# 		#test2 = result["lineupID"]
# 		#open_output_file.write(api_query.search_zip + "," + test + "," + test2 + "\n\n")
# 	print "api location id searches stored"

#Returns the decoded json response content
def api_call(api_query):

	url = "http://api.tvmedia.ca/tv/v4/lineups/41626/listings?api_key=" + API_KEY 

	#auth = HTTPBasicAuth(api_key, api_key)
	# = requests.get(url, auth = auth)

	response_data = requests.get(url)
	print response_data
	
	json_result = response_data.json()
	#print json_result
	print "end json result"
	#for result in json_result:
		#print result
		#print result["listDateTime"]
	return json_result

def store_api_searches(json_results, output_file):
	open_output_file = open(output_file, 'a')
	count = 0 
	for result in json_results:
		open_output_file.write(str(result["showName"].encode("ascii", "ignore")) + ";" + str(result["showType"]) + ";" + str(result["starRating"]) + ";" + result["listDateTime"] + ";" + str(result["duration"]) + ";" +  str(result["stationType"]) + "\n")
		count = count + 1
	print "api searches stored" + str(count)

#main code
#title,g,r,st,duration,provider

main_query = ApiQuery("not used q","asdf","77840",2016-03-11,"not used")
json_result = api_call(main_query)
store_api_searches(json_result, "data.txt")
