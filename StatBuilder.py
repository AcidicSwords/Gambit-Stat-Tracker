import numpy as np
import pandas as pd
#my other file that handles getting a full game list for the player
import BungieRequestHandler



#file for doing all the ugly work, this class will take an unformatted PostGameCarnageReport and build a Pandas dataframe structure that contains each player's data and performance vs the team.
class PGCR_Scraper:

#initialization of class will immediatly begin the process to get the data frame
	def __init__(self,postGameCarnageReportToScrape):

		self.rawPlayerData = postGameCarnageReportToScrape["Response"]["entries"]
		self.PGCR_DataFrame = self.buildPGCR_DataFrame()

#this method is responsible for taking the dataframe and adding all of the team stats for each player
	def computeTeamContribution(self,PGCR_DataFrame):
		updatedPGCR = PGCR_DataFrame

		#this may not be efficient but I thought explicitly stating the stats I wanted to be totalled would be easiest
		statsToTotal = [
			"allDeaths",
			"allKills",
			"mobkills",
			"blockerKills",
			"highValueKills",
			"precisionKills",
			"grenadeKills",
			"meleeKills",
			"superKills",
			"motesCollected",
			"motesDeposited",
			"motesLost",
			"moteBankOverfill",
			"smallBlockersSent",
			"mediumBlockersSent",
			"largeBlockersSent",
			"numberOfInvasions",
			"invasionKills",
			"invaderKills",
			"deathsWhileInvading",
			"deathsToInvaders",
			"motesDenied",
			"primevalDamage",
			"primevalHealing",
			"moteScore",
			"invasionScore",
			"primevalScore",
			"blockerScore"
		]

		#for loop to handle iterating through the data frame and getting all the data, quite proud of this actually
		for i in list(PGCR_DataFrame.index.values):
			#to avoid errors with matching columns I initialized the entire row to NaN before calculating the actual values
			updatedPGCR.loc[(i[0],i[1],'vsTeam')] = np.NaN

			for h in statsToTotal:

				updatedPGCR.loc[(i[0],i[1],'vsTeam'),h] = PGCR_DataFrame.loc[(i[0],i[1],i[2]),h] / PGCR_DataFrame.loc[i[0],h].sum()

		return updatedPGCR



#the main logic loop, this loop will call functions to build each player's stats and then call the function to get the team totals
	def buildPGCR_DataFrame(self):

		playerData = []
		#by making sure each player has completed the match we ensure we don't get more than 8 players
		for player in range(len(self.rawPlayerData)):
			
			if self.rawPlayerData[player]["values"]["completed"]["basic"]["value"] == 1:

				playerData.append(self.buildPlayerSeries(player))

		#set of variable actions to make it all look pretty!
		PGCR_DataFrame = pd.DataFrame(playerData)
		PGCR_DataFrame.insert(1,"stats","individual")
		PGCR_DataFrame = PGCR_DataFrame.set_index(["gameResult","name","stats"]).sort_index()
		PGCR_DataFrame = self.computeTeamContribution(PGCR_DataFrame).sort_index()

		return PGCR_DataFrame

#this is the main logic loop for building the player stats, this will make a series of series to represent the complete stat data for an individual character.
	def buildPlayerSeries(self,player):

		playerSeries = self.buildPlayerInfo(player)

		#calls to build the stats in each category
		playerSeries = playerSeries.append([

			self.buildKillBreakdown(player),
			self.buildEfficiencyStats(player),
			self.buildMoteStats(player),
			self.buildBlockerStats(player),
			self.buildInvasionStats(player),
			self.buildPrimevalStats(player),

			])

		return playerSeries

#this collection of methods will query the right stat from the PGCR and add it to a series that will be added to the players game stats
#sadly without making insane string conecations and methods to build addresses I had to write out each dictionary address
#######################################################################################################################
	def buildPlayerInfo(self,player):
		playerInfo = pd.Series({

			"name"      : self.rawPlayerData[player]["player"]["destinyUserInfo"]["displayName"],
			"icon"      : "https://www.bungie.net" + self.rawPlayerData[player]["player"]["destinyUserInfo"]["iconPath"],
			"class"     : self.rawPlayerData[player]["player"]["characterClass"],
			"level"     : self.rawPlayerData[player]["player"]["characterLevel"],
			"lightLevel": self.rawPlayerData[player]["player"]["lightLevel"],
			"emblem"    : self.rawPlayerData[player]["player"]["emblemHash"],
			"gameResult": self.rawPlayerData[player]["values"]["standing"]["basic"]["displayValue"],
			"team"      : self.rawPlayerData[player]["values"]["team"]["basic"]["value"],
			"roundsWon" : self.rawPlayerData[player]["values"]["teamScore"]["basic"]["value"]
			})

		return playerInfo

	def buildKillBreakdown(self,player):
		killBreakdown = pd.Series({

			"allDeaths"      : self.rawPlayerData[player]["values"]["deaths"]["basic"]["value"],
			"allKills"       : self.rawPlayerData[player]["values"]["opponentsDefeated"]["basic"]["value"],
			"mobkills"       : self.rawPlayerData[player]["extended"]["values"]["mobKills"]["basic"]["value"],
			"blockerKills"   : self.rawPlayerData[player]["extended"]["values"]["blockerKills"]["basic"]["value"],
			"highValueKills" : self.rawPlayerData[player]["extended"]["values"]["highValueKills"]["basic"]["value"],
			"precisionKills" : self.rawPlayerData[player]["extended"]["values"]["precisionKills"]["basic"]["value"],
			"grenadeKills"   : self.rawPlayerData[player]["extended"]["values"]["weaponKillsGrenade"]["basic"]["value"],
			"meleeKills"     : self.rawPlayerData[player]["extended"]["values"]["weaponKillsMelee"]["basic"]["value"],
			"superKills"     : self.rawPlayerData[player]["extended"]["values"]["weaponKillsSuper"]["basic"]["value"]
			})

		return killBreakdown

	def buildEfficiencyStats(self,player):
		efficiencyStats = pd.Series({

			"K/D"   : self.rawPlayerData[player]["values"]["killsDeathsRatio"]["basic"]["value"],
			"K/D/A" : self.rawPlayerData[player]["values"]["killsDeathsAssists"]["basic"]["value"]
			})

		return efficiencyStats

	def buildMoteStats(self,player):
		moteStats = pd.Series({

			"motesCollected"   : self.rawPlayerData[player]["extended"]["values"]["motesPickedUp"]["basic"]["value"],
			"motesDeposited"   : self.rawPlayerData[player]["extended"]["values"]["motesDeposited"]["basic"]["value"],
			"motesLost"        : self.rawPlayerData[player]["extended"]["values"]["motesLost"]["basic"]["value"],
			"moteBankOverfill" : self.rawPlayerData[player]["extended"]["values"]["bankOverage"]["basic"]["value"]
			})

		moteStats["moteScore"] = moteStats["motesDeposited"]-moteStats.loc[["motesLost","moteBankOverfill"]].sum()

		return moteStats

	def buildBlockerStats(self,player):
		blockerStats = pd.Series({

			"smallBlockersSent" : self.rawPlayerData[player]["extended"]["values"]["smallBlockersSent"]["basic"]["value"],
			"mediumBlockersSent": self.rawPlayerData[player]["extended"]["values"]["mediumBlockersSent"]["basic"]["value"],
			"largeBlockersSent" : self.rawPlayerData[player]["extended"]["values"]["largeBlockersSent"]["basic"]["value"]
			})

		blockerStats["blockerScore"] = blockerStats.sum()

		return blockerStats

	def buildInvasionStats(self,player):
		invasionStats = pd.Series({

			"numberOfInvasions"  : self.rawPlayerData[player]["extended"]["values"]["invasions"]["basic"]["value"],
			"invasionKills"      : self.rawPlayerData[player]["extended"]["values"]["invasionKills"]["basic"]["value"],
			"invaderKills"       : self.rawPlayerData[player]["extended"]["values"]["invaderKills"]["basic"]["value"],
			"deathsWhileInvading": self.rawPlayerData[player]["extended"]["values"]["invasionDeaths"]["basic"]["value"],
			"deathsToInvaders"   : self.rawPlayerData[player]["extended"]["values"]["invaderDeaths"]["basic"]["value"],
			"motesDenied"        : self.rawPlayerData[player]["extended"]["values"]["motesDenied"]["basic"]["value"]
			})

		invasionStats["invasionScore"] = invasionStats.loc[["numberOfInvasions","invasionKills","motesDenied"]].sum() - invasionStats.loc[["deathsWhileInvading","deathsToInvaders"]].sum() 

		return invasionStats

	def buildPrimevalStats(self,player):
		primevalStats = pd.Series({

			"primevalDamage" : self.rawPlayerData[player]["extended"]["values"]["primevalDamage"]["basic"]["value"],
			"primevalHealing": self.rawPlayerData[player]["extended"]["values"]["primevalHealing"]["basic"]["value"]
			})

		primevalStats["primevalScore"] = primevalStats["primevalDamage"]/1000000 + primevalStats["primevalHealing"]

		return primevalStats
#######################################################################################################################



#testing data because why not, not representative of the final structure
gamelist = BungieRequestHandler.NewRequest("AcidicSwords#1316",4).requestingPlayerGameList
postGameCarnageReportToScrape = BungieRequestHandler.NewRequest.getPostGameCarnageReport(gamelist["gameList"][0][1])
test = PGCR_Scraper(postGameCarnageReportToScrape)

pd.set_option('display.max_columns',None)
print(test.PGCR_DataFrame)

#side notes:
#depending on how we display data on the front end it may be possible to send data directly from the dataframe vs transforming it into a json or csv
