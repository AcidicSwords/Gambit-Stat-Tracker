import json
import urllib
import requests
from operator import itemgetter
from time import sleep

#Class to Pull a user's Game list from the bungie API
class NewRequest:

#Master API key used in all requests
	API_Key = { "X-API-key" : "0fe5229111d94af791f84552ddf3b4de" }

#class method so that all API requests are handled by one module, has built in sleep to avoid throttling
	@classmethod
	def getPostGameCarnageReport(cls,matchId):

		sleep(0.05)
		request = requests.get("https://www.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/" + matchId + "/",headers=cls.API_Key)
		request = request.json()

		return request

#On every request instance, this script will generate the required user info then attempt to get a game list for the user
	def __init__(self,requestingPlayerDisplayName,requestingPlayerPlatformCode):

		#The request structure is as follows: Entrypoint(user display name and platform) -> BungieId -> CharacterList -> ActivityReportPerCharacter
		self.requestingPlayerDisplayName = urllib.parse.quote(requestingPlayerDisplayName)
		self.requestingPlayerPlatformCode = str(requestingPlayerPlatformCode)
		self.requestingPlayerId = self.getRequestingPlayerId()
		self.requestingPlayerCharacters = self.getRequestingPlayerCharacters()
		self.requestingPlayerGameList = self.getRequestingPlayerGameList()

#These 2 methods are responsible for getting the inital data needed to access the activity data

###############################################################################################
	def getRequestingPlayerId(self):

		request = requests.get("https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayer/" + self.requestingPlayerPlatformCode + "/" + self.requestingPlayerDisplayName + "/", headers=NewRequest.API_Key)
		request = request.json()

		return request["Response"][0]["membershipId"]

	def getRequestingPlayerCharacters(self):

		request = requests.get("https://www.bungie.net/Platform/Destiny2/" + self.requestingPlayerPlatformCode + "/Profile/" + self.requestingPlayerId + "/", headers=NewRequest.API_Key , params={"components":"100"})
		request = request.json()

		return request["Response"]["profile"]["data"]["characterIds"]
###############################################################################################

#This method is responsible for checking each activity request to make sure valid data is returned and the request goes through, this method also ensures the request limit is not hit
#if true this method returns the date and id for the activities pulled from the request
#if false this method returns False altering the behaviour of the next method
	def getMatchDateAndID(self,characterId,count,page):
		activityData=[]
		request = requests.get("https://www.bungie.net/Platform/Destiny2/" + self.requestingPlayerPlatformCode + "/Account/" + self.requestingPlayerId + "/Character/" + characterId + "/Stats/Activities/",headers=NewRequest.API_Key,params={"count":count,"mode":"63","page":page})
		request = request.json()
		sleep(0.05)
		#checks validity of response ensuring at least one activity is returned
		if request["ErrorStatus"] == "Success" and request["Response"]:
			#this loop will add the date and id to a list
			for activity in request["Response"]["activities"]:

				activityData.append([activity["period"],activity["activityDetails"]["instanceId"]])

			return activityData

		else:

			return False


#This method contains the main logic for game retrieval. The main idea is to attempt getting the most games per request.
#if the remaining games in the character's activity list are 100+ it pulls 100
#if the remaining games are less than 100 it pulls 10 and finally if the remaining games are less than 10 it pulls 1
	def getRequestingPlayerGameList(self):
		gameList = []
		#this ten second wait essentially resets the request limit of 25/s average over a rolling 10s window. A full reset is done to ensure minimum wait when we start pulling mass amounts of games
		sleep(10.0)

		#loop to iterate over each character and reset values for the next character
		for character in self.requestingPlayerCharacters:

			status = True
			count = 100
			page = 0
			#loop to request batches of activity data for a character and add it to the master list. Every call to "getMatchDateAndId" is another request to the api
			while status:

				activityData = self.getMatchDateAndID(character,count,page)

				if activityData != False:

					for activity in activityData:

						gameList.append(activity)
				#the variables page and count are query parameters to the api and are responsible for tracking games processed and ensuring that every game is pulled without missing one
					page += 1

				elif count > 1:

					count /= 10
					page *= 10

				else:

					status = False
		#formatting of the gamelist ordered by date in json format for databasing
		gameList = {"gameList":sorted(gameList,key=itemgetter(0),reverse=True)}

		return gameList

#simple test to ensure the script functions
print(NewRequest("AcidicSwords#1316",4).requestingPlayerGameList)
