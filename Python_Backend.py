import json
import urllib
import requests
from operator import itemgetter

class RequestHandler:

	def __init__(self,requestingPlayerDisplayName,requestingPlayerPlatform):
		self.displayName=urllib.parse.quote(requestingPlayerDisplayName)
		self.platform=str(requestingPlayerPlatform)
		self.API_Key={ "X-API-key" : "0fe5229111d94af791f84552ddf3b4de" }
		self.playerId = self.getPlayerId()
		self.characters = self.getCharacterList()
		self.matchId = self.getMatchId()
		self.unformattedPGCR = self.getUnformattedPGCR()
		self.formattedPGCR = self.returnFormattedPGCR()


	def getPlayerId(self):
		request = requests.get("https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayer/" + self.platform + "/" + self.displayName + "/", headers=self.API_Key)
		request = request.json()
		return request["Response"][0]["membershipId"]

	def getCharacterList(self):
		request = requests.get("https://www.bungie.net/Platform/Destiny2/" + self.platform + "/Profile/" + self.playerId + "/", headers=self.API_Key , params={"components":"100"} )
		request = request.json()
		return request["Response"]["profile"]["data"]["characterIds"]

	def getMatchId(self):
		recentGames=[]
		for character in range(len(self.characters)):
			request = requests.get("https://www.bungie.net/Platform/Destiny2/"+self.platform+"/Account/"+self.playerId+"/Character/"+self.characters[character]+"/Stats/Activities/",headers=self.API_Key,params={"count":"1","mode":"63"})
			request = request.json()
			recentGames.append([request["Response"]["activities"][0]["period"],request["Response"]["activities"][0]["activityDetails"]["instanceId"]])

		recentGames = sorted(recentGames,key=itemgetter(0),reverse=True)
		return recentGames[0][1]

	def getUnformattedPGCR(self):
		request = requests.get("https://www.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/"+self.matchId+"/",headers=self.API_Key)
		unformattedPGCR = request.json()
		return unformattedPGCR

	def returnFormattedPGCR(self):
		formattedPGCR = PGCR_Formatter(self.unformattedPGCR)
		formattedPGCR = formattedPGCR.formattedPGCR

		return formattedPGCR






class PGCR_Formatter:

	def __init__(self,unformattedPGCR):
		self.unformattedPGCR = unformattedPGCR
		self.rawPlayerData = unformattedPGCR["Response"]["entries"]
		self.rawTeamData = unformattedPGCR["Response"]["teams"]
		self.formattedMatchData = self.getMatchDetails()
		self.formattedPlayerData = self.getPlayerDetails()
		self.formattedTeams = self.getTeamDetails()
		self.intermediatePGCR = self.getIntermediatePGCR()
		self.formattedPGCR = CalculateTeamTotals(self.intermediatePGCR)
		self.formattedPGCR = self.formattedPGCR.getPGCR_WithTotals()




	def getIntermediatePGCR(self):
		intermediatePGCR = {}
		intermediatePGCR["matchStats"] = self.formattedMatchData
		intermediatePGCR["teams"] = self.formattedTeams

		return intermediatePGCR

	def getMatchDetails(self):
		formattedMatchData = {
		"date": self.unformattedPGCR["Response"]["period"],
		"score": self.rawTeamData[0]["score"]["basic"]["displayValue"]+"-"+self.rawTeamData[1]["score"]["basic"]["displayValue"],
		"rounds": self.rawTeamData[0]["score"]["basic"]["value"] + self.rawTeamData[1]["score"]["basic"]["value"]

		}
		return formattedMatchData

	def getTeamDetails(self):
		formattedTeams = {"teamOne":[],"teamTwo":[]}
		for player in range(len(self.formattedPlayerData)):
			if self.formattedPlayerData[player]["playerInfo"]["team"] == 17 and self.formattedPlayerData[player]["playerInfo"]["finishedMatch"] == 1:
				formattedTeams["teamOne"].append(self.formattedPlayerData[player])
			elif self.formattedPlayerData[player]["playerInfo"]["team"] == 18 and self.formattedPlayerData[player]["playerInfo"]["finishedMatch"] == 1:
				formattedTeams["teamTwo"].append(self.formattedPlayerData[player])
		return formattedTeams

	def getPlayerDetails(self):
		formattedPlayerData = []
		for player in range(len(self.rawPlayerData)):
			formattedPlayerData.append(self.buildPlayerStats(player))
		return formattedPlayerData

	def buildPlayerStats(self,playerNumber):
		playerStats = {
		"playerInfo": self.getPlayerInfo(playerNumber),
		"efficiencyStats":self.getEfficiencyStats(playerNumber),
		"moteStats": self.getMoteStats(playerNumber),
		"blockerStats": self.getBlockerStats(playerNumber),
		"invasionStats": self.getInvasionStats(playerNumber),
		"primevalStats": self.getPrimevalStats(playerNumber)
		}
		return playerStats

	def getPlayerInfo(self,playerNumber):
		playerInfo = {
		"name": self.rawPlayerData[playerNumber]["player"]["destinyUserInfo"]["displayName"],
		"emblem": self.rawPlayerData[playerNumber]["player"]["destinyUserInfo"]["iconPath"],
		"class": self.rawPlayerData[playerNumber]["player"]["characterClass"],
		"level": self.rawPlayerData[playerNumber]["player"]["characterLevel"],
		"lightLevel": self.rawPlayerData[playerNumber]["player"]["lightLevel"],
		"matchStanding": self.rawPlayerData[playerNumber]["standing"],
		"team": self.rawPlayerData[playerNumber]["values"]["team"]["basic"]["value"],
		"finishedMatch": self.rawPlayerData[playerNumber]["values"]["completed"]["basic"]["value"]

		}
		return playerInfo

	def getEfficiencyStats(self,playerNumber):
		efficiencyStats = {
		"assists": self.rawPlayerData[playerNumber]["values"]["assists"]["basic"]["value"],
		"kills": self.rawPlayerData[playerNumber]["values"]["opponentsDefeated"]["basic"]["value"],
		"deaths": self.rawPlayerData[playerNumber]["values"]["deaths"]["basic"]["value"],
		"K/D" : self.rawPlayerData[playerNumber]["values"]["killsDeathsRatio"]["basic"]["value"],
		"K/D/A" : self.rawPlayerData[playerNumber]["values"]["killsDeathsAssists"]["basic"]["value"],
		"pveKills":self.rawPlayerData[playerNumber]["extended"]["values"]["mobKills"]["basic"]["value"]

		}
		return efficiencyStats

	def getMoteStats(self,playerNumber):
		moteStats = {
		"collected":  self.rawPlayerData[playerNumber]["extended"]["values"]["motesPickedUp"]["basic"]["value"],
		"deposited":  self.rawPlayerData[playerNumber]["extended"]["values"]["motesDeposited"]["basic"]["value"],
		"denied":self.rawPlayerData[playerNumber]["extended"]["values"]["motesDenied"]["basic"]["value"],
		"lost":  self.rawPlayerData[playerNumber]["extended"]["values"]["motesLost"]["basic"]["value"]

		}
		return moteStats

	def getBlockerStats(self,playerNumber):
		blockerStats = {
		"smallBlockersSent":  self.rawPlayerData[playerNumber]["extended"]["values"]["smallBlockersSent"]["basic"]["value"],
		"mediumBlockersSent":  self.rawPlayerData[playerNumber]["extended"]["values"]["mediumBlockersSent"]["basic"]["value"],
		"largeBlockersSent":  self.rawPlayerData[playerNumber]["extended"]["values"]["largeBlockersSent"]["basic"]["value"],
		"blockersKilled":  self.rawPlayerData[playerNumber]["extended"]["values"]["blockerKills"]["basic"]["value"]

		}
		return blockerStats

	def getInvasionStats(self,playerNumber):
		invasionStats = {
		"invasions": self.rawPlayerData[playerNumber]["extended"]["values"]["invasions"]["basic"]["value"],
		"invasionKills": self.rawPlayerData[playerNumber]["extended"]["values"]["invasionKills"]["basic"]["value"],
		"deathsWhileInvading":self.rawPlayerData[playerNumber]["extended"]["values"]["invasionDeaths"]["basic"]["value"],
		"deathsToInvaders": self.rawPlayerData[playerNumber]["extended"]["values"]["invaderDeaths"]["basic"]["value"],
		"invaderKills":self.rawPlayerData[playerNumber]["extended"]["values"]["invaderKills"]["basic"]["value"]

		}
		return invasionStats

	def getPrimevalStats(self,playerNumber):
		primevalStats = {
		"primevalDamage":self.rawPlayerData[playerNumber]["extended"]["values"]["primevalDamage"]["basic"]["value"],
		"primevalHealing":self.rawPlayerData[playerNumber]["extended"]["values"]["primevalHealing"]["basic"]["value"]

		}
		return primevalStats
class CalculateTeamTotals:

	def __init__(self,intermediatePGCR):
		self.intermediatePGCR = intermediatePGCR

	def getPGCR_WithTotals(self):
		self.getTeamTotals()
		PGCR_WithTotals = self.intermediatePGCR
		PGCR_WithTotals = json.dumps(PGCR_WithTotals)

		return PGCR_WithTotals

	def getTeamTotals(self):
		self.intermediatePGCR["teams"]["teamOneTotals"] = {
		"totalledMoteStats": self.totalMoteStats("teamOne"),
		"totalledBlockerStats": self.totalBlockerStats("teamOne"),
		"totalledInvasionStats": self.totalInvasionStats("teamOne"),
		"totalledPrimevalStats": self.totalPrimevalStats("teamOne"),
		"totalledKillDeathStats": self.totalKillDeathStats("teamOne")
		}
		self.intermediatePGCR["teams"]["teamTwoTotals"] = {
		"totalledMoteStats": self.totalMoteStats("teamTwo"),
		"totalledBlockerStats": self.totalBlockerStats("teamTwo"),
		"totalledInvasionStats": self.totalInvasionStats("teamTwo"),
		"totalledPrimevalStats": self.totalPrimevalStats("teamTwo"),
		"totalledKillDeathStats": self.totalKillDeathStats("teamTwo")
		}

	def totalMoteStats(self,teamName):
		totalledMoteStats = {"totalMoteScore": 0, "totalCollected": 0, "totalDeposited":0,"totalDenied":0,"totalLost":0 }
		for player in range(len(self.intermediatePGCR["teams"][teamName])):
			totalledMoteStats["totalCollected"] += self.intermediatePGCR["teams"][teamName][player]["moteStats"]["collected"]
			totalledMoteStats["totalDeposited"] += self.intermediatePGCR["teams"][teamName][player]["moteStats"]["deposited"]
			totalledMoteStats["totalDenied"] += self.intermediatePGCR["teams"][teamName][player]["moteStats"]["denied"]
			totalledMoteStats["totalLost"] +=self.intermediatePGCR["teams"][teamName][player]["moteStats"]["lost"]

		totalledMoteStats["totalMoteScore"] = totalledMoteStats["totalCollected"] + totalledMoteStats["totalDeposited"] + totalledMoteStats["totalDenied"] - totalledMoteStats["totalLost"]

		return totalledMoteStats

	def totalBlockerStats(self,teamName):
		totalledBlockerStats = {"totalBlockerScore": 0, "totalSmallBlockersSent": 0, "totalMediumBlockersSent":0,"totalLargeBlockersSent":0,"totalBlockersKilled":0 }
		for player in range(len(self.intermediatePGCR["teams"][teamName])):
			totalledBlockerStats["totalSmallBlockersSent"] +=self.intermediatePGCR["teams"][teamName][player]["blockerStats"]["smallBlockersSent"]
			totalledBlockerStats["totalMediumBlockersSent"] +=self.intermediatePGCR["teams"][teamName][player]["blockerStats"]["mediumBlockersSent"]
			totalledBlockerStats["totalLargeBlockersSent"] +=self.intermediatePGCR["teams"][teamName][player]["blockerStats"]["largeBlockersSent"]
			totalledBlockerStats["totalBlockersKilled"] +=self.intermediatePGCR["teams"][teamName][player]["blockerStats"]["blockersKilled"]

		totalledBlockerStats["totalBlockerScore"] = totalledBlockerStats["totalSmallBlockersSent"] + totalledBlockerStats["totalMediumBlockersSent"] + totalledBlockerStats["totalLargeBlockersSent"] + totalledBlockerStats["totalBlockersKilled"]

		return totalledBlockerStats

	def totalInvasionStats(self,teamName):
		totalledInvasionStats = {"totalInvasionScore": 0, "totalInvasions": 0, "totalInvasionKills":0,"totalDeathsWhileInvading":0,"totalDeathsToInvaders":0,"totalInvaderKills":0 }
		for player in range(len(self.intermediatePGCR["teams"][teamName])):
			totalledInvasionStats["totalInvasions"]+= self.intermediatePGCR["teams"][teamName][player]["invasionStats"]["invasions"]
			totalledInvasionStats["totalInvasionKills"] += self.intermediatePGCR["teams"][teamName][player]["invasionStats"]["invasionKills"]
			totalledInvasionStats["totalDeathsWhileInvading"] += self.intermediatePGCR["teams"][teamName][player]["invasionStats"]["deathsWhileInvading"]
			totalledInvasionStats["totalDeathsToInvaders"] += self.intermediatePGCR["teams"][teamName][player]["invasionStats"]["deathsToInvaders"]
			totalledInvasionStats["totalInvaderKills"] += self.intermediatePGCR["teams"][teamName][player]["invasionStats"]["invaderKills"]

		totalledInvasionStats["totalInvasionScore"] = totalledInvasionStats["totalInvasions"] + totalledInvasionStats["totalInvasionKills"] + totalledInvasionStats["totalInvaderKills"] - totalledInvasionStats["totalDeathsWhileInvading"] - totalledInvasionStats["totalDeathsToInvaders"]

		return totalledInvasionStats

	def totalPrimevalStats(self,teamName):
		totalledPrimevalStats = {"totalPrimevalScore":0,"totalPrimevalDamage":0,"totalPrimevalHealing":0}
		for player in range(len(self.intermediatePGCR["teams"][teamName])):
			totalledPrimevalStats["totalPrimevalDamage"] += self.intermediatePGCR["teams"][teamName][player]["primevalStats"]["primevalDamage"]
			totalledPrimevalStats["totalPrimevalHealing"] += self.intermediatePGCR["teams"][teamName][player]["primevalStats"]["primevalHealing"]

		totalledPrimevalStats["totalPrimevalScore"] = totalledPrimevalStats["totalPrimevalDamage"]/1000000 + totalledPrimevalStats["totalPrimevalHealing"]

		return totalledPrimevalStats

	def totalKillDeathStats(self,teamName):
		totalledKillDeathStats = {"totalKillDeathScore":0,"totalPveKills":0,"totalDeaths":0}
		for player in range(len(self.intermediatePGCR["teams"][teamName])):
			totalledKillDeathStats["totalPveKills"] += self.intermediatePGCR["teams"][teamName][player]["efficiencyStats"]["pveKills"]
			totalledKillDeathStats["totalDeaths"] += self.intermediatePGCR["teams"][teamName][player]["efficiencyStats"]["deaths"]

		totalledKillDeathStats["totalKillDeathScore"] = totalledKillDeathStats["totalPveKills"] - totalledKillDeathStats["totalDeaths"]

		return totalledKillDeathStats



newrequest = RequestHandler("AcidicSwords#1316",4)
print(newrequest.formattedPGCR)
