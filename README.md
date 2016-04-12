# TVtime
In the folder "app", project_api.py includes the code that communicates with TVmedia's API to access television programming information. More information on the API can be found at developer.tvmedia.ca
An example of the data received from the API is included in data.txt
The main functionality of our program is in recommender.py, where a user's genre preferences, periods of free time (date and time), provider, and location are used to filter the show listings given by the API. The shows that meet the requirements are then ranked according to their IMDb rating and the top results are recommended to the user.

To run recommender: Execute recommender.py using test2.txt as sample API data. 
