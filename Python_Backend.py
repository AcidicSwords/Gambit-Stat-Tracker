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
		self.PGCR = self.getPGCR()


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

	def getPGCR(self):
		request = requests.get("https://www.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/"+self.matchId+"/",headers=self.API_Key)
		PGCR = request.json()
		return PGCR






class PGCR_Formatter:

	def __init__(self,PGCR):
		self.PGCR = PGCR
		self.playerData = PGCR["Response"]["entries"]
		self.teamData = PGCR["Response"]["teams"]
		self.formattedMatchDetails = self.getMatchDetails()
		self.formattedPlayerDetails = self.getPlayerDetails()
		self.formattedTeams = self.getTeamDetails()
		self.intermediatePGCR = self.getIntermediatePGCR()
		self.finalPGCR = CalculateTeamTotals(self.intermediatePGCR)
		self.finalPGCR.getTeamTotals()

		self.finalPGCR = json.dumps(self.finalPGCR.PGCR)


	def getIntermediatePGCR(self):
		intermediatePGCR = {}
		intermediatePGCR["matchStats"] = self.formattedMatchDetails
		intermediatePGCR["teams"] = self.formattedTeams

		return intermediatePGCR

	def getMatchDetails(self):
		formattedMatchDetails = {
		"date": self.PGCR["Response"]["period"],
		"score": self.teamData[0]["score"]["basic"]["displayValue"]+"-"+self.teamData[1]["score"]["basic"]["displayValue"],
		"rounds": self.teamData[0]["score"]["basic"]["value"] + self.teamData[1]["score"]["basic"]["value"]

		}
		return formattedMatchDetails

	def getTeamDetails(self):
		formattedTeams = {"teamOne":{"teamOnePlayers":[]},"teamTwo":{"teamTwoPlayers":[]}}
		for player in range(len(self.formattedPlayerDetails)):
			if self.formattedPlayerDetails[player]["playerInfo"]["team"] == 17 and self.formattedPlayerDetails[player]["playerInfo"]["finishedMatch"] == 1:
				formattedTeams["teamOne"]["teamOnePlayers"].append(self.formattedPlayerDetails[player])
			elif self.formattedPlayerDetails[player]["playerInfo"]["team"] == 18 and self.formattedPlayerDetails[player]["playerInfo"]["finishedMatch"] == 1:
				formattedTeams["teamTwo"]["teamTwoPlayers"].append(self.formattedPlayerDetails[player])
		return formattedTeams

	def getPlayerDetails(self):
		playerDetails = []
		for player in range(len(self.playerData)):
			playerDetails.append(self.buildPlayerStats(player))
		return playerDetails

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
		"name": self.playerData[playerNumber]["player"]["destinyUserInfo"]["displayName"],
		"emblem": self.playerData[playerNumber]["player"]["destinyUserInfo"]["iconPath"],
		"class": self.playerData[playerNumber]["player"]["characterClass"],
		"level": self.playerData[playerNumber]["player"]["characterLevel"],
		"lightLevel": self.playerData[playerNumber]["player"]["lightLevel"],
		"matchStanding": self.playerData[playerNumber]["standing"],
		"team": self.playerData[playerNumber]["values"]["team"]["basic"]["value"],
		"finishedMatch": self.playerData[playerNumber]["values"]["completed"]["basic"]["value"]

		}
		return playerInfo

	def getEfficiencyStats(self,playerNumber):
		efficiencyStats = {
		"assists": self.playerData[playerNumber]["values"]["assists"]["basic"]["value"],
		"kills": self.playerData[playerNumber]["values"]["opponentsDefeated"]["basic"]["value"],
		"deaths": self.playerData[playerNumber]["values"]["deaths"]["basic"]["value"],
		"K/D" : self.playerData[playerNumber]["values"]["killsDeathsRatio"]["basic"]["value"],
		"K/D/A" : self.playerData[playerNumber]["values"]["killsDeathsAssists"]["basic"]["value"],
		"pveKills":self.playerData[playerNumber]["extended"]["values"]["mobKills"]["basic"]["value"]

		}
		return efficiencyStats

	def getMoteStats(self,playerNumber):
		moteStats = {
		"collected":  self.playerData[playerNumber]["extended"]["values"]["motesPickedUp"]["basic"]["value"],
		"deposited":  self.playerData[playerNumber]["extended"]["values"]["motesDeposited"]["basic"]["value"],
		"denied":self.playerData[playerNumber]["extended"]["values"]["motesDenied"]["basic"]["value"],
		"lost":  self.playerData[playerNumber]["extended"]["values"]["motesLost"]["basic"]["value"]

		}
		return moteStats

	def getBlockerStats(self,playerNumber):
		blockerStats = {
		"smallBlockersSent":  self.playerData[playerNumber]["extended"]["values"]["smallBlockersSent"]["basic"]["value"],
		"mediumBlockersSent":  self.playerData[playerNumber]["extended"]["values"]["mediumBlockersSent"]["basic"]["value"],
		"largeBlockersSent":  self.playerData[playerNumber]["extended"]["values"]["largeBlockersSent"]["basic"]["value"],
		"blockersKilled":  self.playerData[playerNumber]["extended"]["values"]["blockerKills"]["basic"]["value"]

		}
		return blockerStats

	def getInvasionStats(self,playerNumber):
		invasionStats = {
		"invasions": self.playerData[playerNumber]["extended"]["values"]["invasions"]["basic"]["value"],
		"invasionKills": self.playerData[playerNumber]["extended"]["values"]["invasionKills"]["basic"]["value"],
		"deathsWhileInvading":self.playerData[playerNumber]["extended"]["values"]["invasionDeaths"]["basic"]["value"],
		"deathsToInvaders": self.playerData[playerNumber]["extended"]["values"]["invaderDeaths"]["basic"]["value"],
		"invaderKills":self.playerData[playerNumber]["extended"]["values"]["invaderKills"]["basic"]["value"]

		}
		return invasionStats

	def getPrimevalStats(self,playerNumber):
		primevalStats = {
		"primevalDamage":self.playerData[playerNumber]["extended"]["values"]["primevalDamage"]["basic"]["value"],
		"primevalHealing":self.playerData[playerNumber]["extended"]["values"]["primevalHealing"]["basic"]["value"]

		}
		return primevalStats
class CalculateTeamTotals:

	def __init__(self,intermediatePGCR):
		self.PGCR = intermediatePGCR

	def getTeamTotals(self):
		self.PGCR["teams"]["teamOne"]["teamOneTotals"] = {
		"totalledMoteStats": self.totalMoteStats("teamOne"),
		"totalledBlockerStats": self.totalBlockerStats("teamOne"),
		"totalledInvasionStats": self.totalInvasionStats("teamOne"),
		"totalledPrimevalStats": self.totalPrimevalStats("teamOne"),
		"totalledKillDeathStats": self.totalKillDeathStats("teamOne")
		}
		self.PGCR["teams"]["teamTwo"]["teamTwoTotals"] = {
		"totalledMoteStats": self.totalMoteStats("teamTwo"),
		"totalledBlockerStats": self.totalBlockerStats("teamTwo"),
		"totalledInvasionStats": self.totalInvasionStats("teamTwo"),
		"totalledPrimevalStats": self.totalPrimevalStats("teamTwo"),
		"totalledKillDeathStats": self.totalKillDeathStats("teamTwo")
		}

	def totalMoteStats(self,teamName):
		totalledMoteStats = {"totalMoteScore": 0, "totalCollected": 0, "totalDeposited":0,"totalDenied":0,"totalLost":0 }
		for player in range(len(self.PGCR["teams"][teamName][teamName+"Players"])):
			totalledMoteStats["totalCollected"] = totalledMoteStats["totalCollected"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["moteStats"]["collected"]
			totalledMoteStats["totalDeposited"] = totalledMoteStats["totalDeposited"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["moteStats"]["deposited"]
			totalledMoteStats["totalDenied"] = totalledMoteStats["totalDenied"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["moteStats"]["denied"]
			totalledMoteStats["totalLost"] = totalledMoteStats["totalLost"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["moteStats"]["lost"]

		totalledMoteStats["totalMoteScore"] = totalledMoteStats["totalCollected"] + totalledMoteStats["totalDeposited"] + totalledMoteStats["totalDenied"] - totalledMoteStats["totalLost"]

		return totalledMoteStats

	def totalBlockerStats(self,teamName):
		totalledBlockerStats = {"totalBlockerScore": 0, "totalSmallBlockersSent": 0, "totalMediumBlockersSent":0,"totalLargeBlockersSent":0,"totalBlockersKilled":0 }
		for player in range(len(self.PGCR["teams"][teamName][teamName+"Players"])):
			totalledBlockerStats["totalSmallBlockersSent"] = totalledBlockerStats["totalSmallBlockersSent"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["blockerStats"]["smallBlockersSent"]
			totalledBlockerStats["totalMediumBlockersSent"] = totalledBlockerStats["totalMediumBlockersSent"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["blockerStats"]["mediumBlockersSent"]
			totalledBlockerStats["totalLargeBlockersSent"] = totalledBlockerStats["totalLargeBlockersSent"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["blockerStats"]["largeBlockersSent"]
			totalledBlockerStats["totalBlockersKilled"] = totalledBlockerStats["totalBlockersKilled"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["blockerStats"]["blockersKilled"]

		totalledBlockerStats["totalBlockerScore"] = totalledBlockerStats["totalSmallBlockersSent"] + totalledBlockerStats["totalMediumBlockersSent"] + totalledBlockerStats["totalLargeBlockersSent"] + totalledBlockerStats["totalBlockersKilled"]

		return totalledBlockerStats

	def totalInvasionStats(self,teamName):
		totalledInvasionStats = {"totalInvasionScore": 0, "totalInvasions": 0, "totalInvasionKills":0,"totalDeathsWhileInvading":0,"totalDeathsToInvaders":0,"totalInvaderKills":0 }
		for player in range(len(self.PGCR["teams"][teamName][teamName+"Players"])):
			totalledInvasionStats["totalInvasions"] = totalledInvasionStats["totalInvasions"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["invasionStats"]["invasions"]
			totalledInvasionStats["totalInvasionKills"] = totalledInvasionStats["totalInvasionKills"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["invasionStats"]["invasionKills"]
			totalledInvasionStats["totalDeathsWhileInvading"] = totalledInvasionStats["totalDeathsWhileInvading"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["invasionStats"]["deathsWhileInvading"]
			totalledInvasionStats["totalDeathsToInvaders"] = totalledInvasionStats["totalDeathsToInvaders"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["invasionStats"]["deathsToInvaders"]
			totalledInvasionStats["totalInvaderKills"] = totalledInvasionStats["totalInvaderKills"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["invasionStats"]["invaderKills"]

		totalledInvasionStats["totalInvasionScore"] = totalledInvasionStats["totalInvasions"] + totalledInvasionStats["totalInvasionKills"] + totalledInvasionStats["totalInvaderKills"] - totalledInvasionStats["totalDeathsWhileInvading"] - totalledInvasionStats["totalDeathsToInvaders"]

		return totalledInvasionStats

	def totalPrimevalStats(self,teamName):
		totalledPrimevalStats = {"totalPrimevalScore":0,"totalPrimevalDamage":0,"totalPrimevalHealing":0}
		for player in range(len(self.PGCR["teams"][teamName][teamName+"Players"])):
			totalledPrimevalStats["totalPrimevalDamage"] = totalledPrimevalStats["totalPrimevalDamage"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["primevalStats"]["primevalDamage"]
			totalledPrimevalStats["totalPrimevalHealing"] = totalledPrimevalStats["totalPrimevalHealing"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["primevalStats"]["primevalHealing"]

		totalledPrimevalStats["totalPrimevalScore"] = totalledPrimevalStats["totalPrimevalDamage"]/1000000 + totalledPrimevalStats["totalPrimevalHealing"]

		return totalledPrimevalStats

	def totalKillDeathStats(self,teamName):
		totalledKillDeathStats = {"totalKillDeathScore":0,"totalPveKills":0,"totalDeaths":0}
		for player in range(len(self.PGCR["teams"][teamName][teamName+"Players"])):
			totalledKillDeathStats["totalPveKills"] = totalledKillDeathStats["totalPveKills"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["efficiencyStats"]["pveKills"]
			totalledKillDeathStats["totalDeaths"] = totalledKillDeathStats["totalDeaths"] + self.PGCR["teams"][teamName][teamName+"Players"][player]["efficiencyStats"]["deaths"]

		totalledKillDeathStats["totalKillDeathScore"] = totalledKillDeathStats["totalPveKills"] - totalledKillDeathStats["totalDeaths"]

		return totalledKillDeathStats



newrequest = RequestHandler("AcidicSwords#1316",4)
newPGCR = PGCR_Formatter(newrequest.PGCR)
print(newPGCR.finalPGCR)
