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
		"score": { 17:self.rawTeamData[0]["score"]["basic"]["displayValue"], 18:self.rawTeamData[1]["score"]["basic"]["displayValue"]},
		"rounds": self.rawTeamData[0]["score"]["basic"]["value"] + self.rawTeamData[1]["score"]["basic"]["value"],
		"winningTeam": self.getWinningTeam()

		}
		return formattedMatchData

	def getWinningTeam(self):
		if self.rawTeamData[0]["score"]["basic"]["value"] == 2:
			return 17
		else:
			return 18

	def getTeamDetails(self):
		formattedTeams = {17:[],18:[]}
		for player in range(len(self.formattedPlayerData)):
			if self.formattedPlayerData[player]["playerInfo"]["team"] == 17 and self.formattedPlayerData[player]["playerInfo"]["finishedMatch"] == 1:
				formattedTeams[17].append(self.formattedPlayerData[player])
			elif self.formattedPlayerData[player]["playerInfo"]["team"] == 18 and self.formattedPlayerData[player]["playerInfo"]["finishedMatch"] == 1:
				formattedTeams[18].append(self.formattedPlayerData[player])
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
		"allKills": self.rawPlayerData[playerNumber]["values"]["opponentsDefeated"]["basic"]["value"],
		"deaths": self.rawPlayerData[playerNumber]["values"]["deaths"]["basic"]["value"],
		"K/D" : self.rawPlayerData[playerNumber]["values"]["killsDeathsRatio"]["basic"]["value"],
		"K/D/A" : self.rawPlayerData[playerNumber]["values"]["killsDeathsAssists"]["basic"]["value"],
		"pveKills":self.rawPlayerData[playerNumber]["extended"]["values"]["mobKills"]["basic"]["value"]

		}
		efficiencyStats["individualEfficiencyScore"] = efficiencyStats["pveKills"] - efficiencyStats["deaths"]
		return efficiencyStats

	def getMoteStats(self,playerNumber):
		moteStats = {
		"collected":  self.rawPlayerData[playerNumber]["extended"]["values"]["motesPickedUp"]["basic"]["value"],
		"deposited":  self.rawPlayerData[playerNumber]["extended"]["values"]["motesDeposited"]["basic"]["value"],
		"denied":self.rawPlayerData[playerNumber]["extended"]["values"]["motesDenied"]["basic"]["value"],
		"lost":  self.rawPlayerData[playerNumber]["extended"]["values"]["motesLost"]["basic"]["value"]

		}
		moteStats["individualMoteScore"] = moteStats["deposited"] + moteStats["denied"] - moteStats["lost"]
		return moteStats

	def getBlockerStats(self,playerNumber):
		blockerStats = {
		"smallBlockersSent":  self.rawPlayerData[playerNumber]["extended"]["values"]["smallBlockersSent"]["basic"]["value"],
		"mediumBlockersSent":  self.rawPlayerData[playerNumber]["extended"]["values"]["mediumBlockersSent"]["basic"]["value"],
		"largeBlockersSent":  self.rawPlayerData[playerNumber]["extended"]["values"]["largeBlockersSent"]["basic"]["value"],
		"blockersKilled":  self.rawPlayerData[playerNumber]["extended"]["values"]["blockerKills"]["basic"]["value"]

		}
		blockerStats["individualBlockerScore"] = blockerStats["smallBlockersSent"] + blockerStats["mediumBlockersSent"] + blockerStats["largeBlockersSent"] + blockerStats["blockersKilled"]
		return blockerStats

	def getInvasionStats(self,playerNumber):
		invasionStats = {
		"invasions": self.rawPlayerData[playerNumber]["extended"]["values"]["invasions"]["basic"]["value"],
		"invasionKills": self.rawPlayerData[playerNumber]["extended"]["values"]["invasionKills"]["basic"]["value"],
		"deathsWhileInvading":self.rawPlayerData[playerNumber]["extended"]["values"]["invasionDeaths"]["basic"]["value"],
		"deathsToInvaders": self.rawPlayerData[playerNumber]["extended"]["values"]["invaderDeaths"]["basic"]["value"],
		"invaderKills":self.rawPlayerData[playerNumber]["extended"]["values"]["invaderKills"]["basic"]["value"]

		}
		invasionStats["individualInvasionScore"] = invasionStats["invasions"] + invasionStats["invasionKills"] + invasionStats["invaderKills"] - invasionStats["deathsWhileInvading"] - invasionStats["deathsToInvaders"]
		return invasionStats

	def getPrimevalStats(self,playerNumber):
		primevalStats = {
		"primevalDamage":self.rawPlayerData[playerNumber]["extended"]["values"]["primevalDamage"]["basic"]["value"],
		"primevalHealing":self.rawPlayerData[playerNumber]["extended"]["values"]["primevalHealing"]["basic"]["value"]

		}
		primevalStats["individualPrimevalScore"] = primevalStats["primevalDamage"]/1000000 + primevalStats["primevalHealing"]
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
		self.intermediatePGCR["teams"]["team17Totals"] = {
		"teamMoteStats": self.totalMoteStats(17),
		"teamBlockerStats": self.totalBlockerStats(17),
		"teamInvasionStats": self.totalInvasionStats(17),
		"teamPrimevalStats": self.totalPrimevalStats(17),
		"teamEfficiencyStats": self.totalEfficiencyStats(17)
		}
		self.intermediatePGCR["teams"]["team18Totals"] = {
		"teamMoteStats": self.totalMoteStats(18),
		"teamBlockerStats": self.totalBlockerStats(18),
		"teamInvasionStats": self.totalInvasionStats(18),
		"teamPrimevalStats": self.totalPrimevalStats(18),
		"teamEfficiencyStats": self.totalEfficiencyStats(18)
		}

	def totalMoteStats(self,teamName):
		teamMoteStats = {"teamMoteScore": 0, "teamCollected": 0, "teamDeposited":0,"teamDenied":0,"teamLost":0 }
		for player in range(len(self.intermediatePGCR["teams"][teamName])):
			teamMoteStats["teamDeposited"] += self.intermediatePGCR["teams"][teamName][player]["moteStats"]["deposited"]
			teamMoteStats["teamDenied"] += self.intermediatePGCR["teams"][teamName][player]["moteStats"]["denied"]
			teamMoteStats["teamLost"] +=self.intermediatePGCR["teams"][teamName][player]["moteStats"]["lost"]

		teamMoteStats["teamMoteScore"] = teamMoteStats["teamDeposited"] + teamMoteStats["teamDenied"] - teamMoteStats["teamLost"]

		return teamMoteStats

	def totalBlockerStats(self,teamName):
		teamBlockerStats = {"teamBlockerScore": 0, "teamSmallBlockersSent": 0, "teamMediumBlockersSent":0,"teamLargeBlockersSent":0,"teamBlockersKilled":0 }
		for player in range(len(self.intermediatePGCR["teams"][teamName])):
			teamBlockerStats["teamSmallBlockersSent"] +=self.intermediatePGCR["teams"][teamName][player]["blockerStats"]["smallBlockersSent"]
			teamBlockerStats["teamMediumBlockersSent"] +=self.intermediatePGCR["teams"][teamName][player]["blockerStats"]["mediumBlockersSent"]
			teamBlockerStats["teamLargeBlockersSent"] +=self.intermediatePGCR["teams"][teamName][player]["blockerStats"]["largeBlockersSent"]
			teamBlockerStats["teamBlockersKilled"] +=self.intermediatePGCR["teams"][teamName][player]["blockerStats"]["blockersKilled"]

		teamBlockerStats["teamteamBlockerScore"] = teamBlockerStats["teamSmallBlockersSent"] + teamBlockerStats["teamMediumBlockersSent"] + teamBlockerStats["teamLargeBlockersSent"] + teamBlockerStats["teamBlockersKilled"]

		return teamBlockerStats

	def totalInvasionStats(self,teamName):
		teamInvasionStats = {"teamInvasionScore": 0, "teamInvasions": 0, "teamInvasionKills":0,"teamDeathsWhileInvading":0,"teamDeathsToInvaders":0,"teamInvaderKills":0 }
		for player in range(len(self.intermediatePGCR["teams"][teamName])):
			teamInvasionStats["teamInvasions"]+= self.intermediatePGCR["teams"][teamName][player]["invasionStats"]["invasions"]
			teamInvasionStats["teamInvasionKills"] += self.intermediatePGCR["teams"][teamName][player]["invasionStats"]["invasionKills"]
			teamInvasionStats["teamDeathsWhileInvading"] += self.intermediatePGCR["teams"][teamName][player]["invasionStats"]["deathsWhileInvading"]
			teamInvasionStats["teamDeathsToInvaders"] += self.intermediatePGCR["teams"][teamName][player]["invasionStats"]["deathsToInvaders"]
			teamInvasionStats["teamInvaderKills"] += self.intermediatePGCR["teams"][teamName][player]["invasionStats"]["invaderKills"]

		teamInvasionStats["teamInvasionScore"] = teamInvasionStats["teamInvasions"] + teamInvasionStats["teamInvasionKills"] + teamInvasionStats["teamInvaderKills"] - teamInvasionStats["teamDeathsWhileInvading"] - teamInvasionStats["teamDeathsToInvaders"]

		return teamInvasionStats

	def totalPrimevalStats(self,teamName):
		teamPrimevalStats = {"teamPrimevalScore":0,"teamPrimevalDamage":0,"teamPrimevalHealing":0}
		for player in range(len(self.intermediatePGCR["teams"][teamName])):
			teamPrimevalStats["teamPrimevalDamage"] += self.intermediatePGCR["teams"][teamName][player]["primevalStats"]["primevalDamage"]
			teamPrimevalStats["teamPrimevalHealing"] += self.intermediatePGCR["teams"][teamName][player]["primevalStats"]["primevalHealing"]

		teamPrimevalStats["teamPrimevalScore"] = teamPrimevalStats["teamPrimevalDamage"]/1000000 + teamPrimevalStats["teamPrimevalHealing"]

		return teamPrimevalStats

	def totalEfficiencyStats(self,teamName):
		teamEfficiencyStats = {"teamEfficiencyScore":0,"teamPveKills":0,"teamDeaths":0}
		for player in range(len(self.intermediatePGCR["teams"][teamName])):
			teamEfficiencyStats["teamPveKills"] += self.intermediatePGCR["teams"][teamName][player]["efficiencyStats"]["pveKills"]
			teamEfficiencyStats["teamDeaths"] += self.intermediatePGCR["teams"][teamName][player]["efficiencyStats"]["deaths"]

		teamEfficiencyStats["teamEfficiencyEfficiencyScore"] = teamEfficiencyStats["teamPveKills"] - teamEfficiencyStats["teamDeaths"]

		return teamEfficiencyStats



newrequest = RequestHandler("AcidicSwords#1316",4)
print(newrequest.formattedPGCR)
