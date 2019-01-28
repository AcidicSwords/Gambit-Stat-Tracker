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

def buildTeamContribution(self,PGCR_DataFrame):

		columns = [["percentVsTeam"],list(PGCR_DataFrame.loc[:,"individual"].columns.values)]
		index = pd.MultiIndex.from_product(columns, names=["CATEGORY","STATS"])

		ContributionDataFrame = [] #this initializes a list that will be populated by the loops

		#loop that goes through each player creating a dataframe, list contains imformation that is used in the second loop for isolating components of our big dataframe
		for player in list(PGCR_DataFrame.index.values):

			playerContribution = [] #this initializes a blank list to be filled by the next loop

			#loop that goes through each stat and gets the percent compared to the team and adds it to a list that will be turned into a DataFrame
			for stat in list(PGCR_DataFrame.loc[:,"individual"]):

				playerContribution.append(PGCR_DataFrame.loc[(player[0],player[1]),("individual",stat)]/PGCR_DataFrame.loc[(player[0]),("individual",stat)].sum())

			#creation of the teamcontribution dataframe for an individual player
			playerContribution = pd.DataFrame([playerContribution], columns = index,index = [(player[0],player[1])])
			ContributionDataFrame.append(playerContribution)

		#combination of each players dataframe into one big one to be combined with our "master" Dataframe
		ContributionDataFrame= pd.concat(ContributionDataFrame)
		PGCR_DataFrame = [PGCR_DataFrame,ContributionDataFrame]

		return pd.concat(PGCR_DataFrame,axis=1)



#this collection of methods will query the right stat from the PGCR and add it to a DataFrame that will be added to the players game stats
#sadly without making insane string conecations and methods to build addresses I had to write out each dictionary address
#######################################################################################################################
	def buildPlayerInfo(self,player):
		columns = [["playerInfo"],["name","icon","class","level","lightLevel","emblem","gameResult","team","roundsWon"]]
		index = pd.MultiIndex.from_product(columns, names=["CATEGORY","STATS"])
		playerInfo = pd.DataFrame([[

			self.rawPlayerData[player]["player"]["destinyUserInfo"]["displayName"],
			"https://www.bungie.net" + self.rawPlayerData[player]["player"]["destinyUserInfo"]["iconPath"],
			self.rawPlayerData[player]["player"]["characterClass"],
			self.rawPlayerData[player]["player"]["characterLevel"],
			self.rawPlayerData[player]["player"]["lightLevel"],
			self.rawPlayerData[player]["player"]["emblemHash"],
			self.rawPlayerData[player]["values"]["standing"]["basic"]["displayValue"],
			self.rawPlayerData[player]["values"]["team"]["basic"]["value"],
			self.rawPlayerData[player]["values"]["teamScore"]["basic"]["value"]
			]], columns = index)

		return playerInfo

	def buildKillBreakdown(self,player):
		columns = [["individual"],["allDeaths","allKills","mobkills","blockerKills","highValueKills","precisionKills","grenadeKills","meleeKills","superKills"]]
		index = pd.MultiIndex.from_product(columns, names=["CATEGORY","STATS"])
		killBreakdown = pd.DataFrame([[

			self.rawPlayerData[player]["values"]["deaths"]["basic"]["value"],
			self.rawPlayerData[player]["values"]["opponentsDefeated"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["mobKills"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["blockerKills"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["highValueKills"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["precisionKills"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["weaponKillsGrenade"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["weaponKillsMelee"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["weaponKillsSuper"]["basic"]["value"]
			]], columns = index)

		return killBreakdown

	def buildEfficiencyStats(self,player):
		columns = [["playerInfo"],["K/D","K/D/A"]]
		index = pd.MultiIndex.from_product(columns, names=["CATEGORY","STATS"])
		efficiencyStats = pd.DataFrame([[

			self.rawPlayerData[player]["values"]["killsDeathsRatio"]["basic"]["value"],
			self.rawPlayerData[player]["values"]["killsDeathsAssists"]["basic"]["value"]
			]], columns = index)

		return efficiencyStats

	def buildMoteStats(self,player):
		columns = [["individual"],["motesCollected","motesDeposited","motesLost","moteBankOverfill"]]
		index = pd.MultiIndex.from_product(columns, names=["CATEGORY","STATS"])
		moteStats = pd.DataFrame([[

			self.rawPlayerData[player]["extended"]["values"]["motesPickedUp"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["motesDeposited"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["motesLost"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["bankOverage"]["basic"]["value"]
			]], columns = index)

		return moteStats

	def buildBlockerStats(self,player):
		columns = [["individual"],["smallBlockersSent","mediumBlockersSent","largeBlockersSent"]]
		index = pd.MultiIndex.from_product(columns, names=["CATEGORY","STATS"])
		blockerStats = pd.DataFrame([[

			self.rawPlayerData[player]["extended"]["values"]["smallBlockersSent"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["mediumBlockersSent"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["largeBlockersSent"]["basic"]["value"]
			]], columns = index)

		return blockerStats

	def buildInvasionStats(self,player):
		columns = [["individual"],["numberOfInvasions","invasionKills","invaderKills","deathsWhileInvading","deathsToInvaders","motesDenied"]]
		index = pd.MultiIndex.from_product(columns, names=["CATEGORY","STATS"])
		invasionStats = pd.DataFrame([[

			self.rawPlayerData[player]["extended"]["values"]["invasions"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["invasionKills"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["invaderKills"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["invasionDeaths"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["invaderDeaths"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["motesDenied"]["basic"]["value"]
			]], columns = index)

		return invasionStats

	def buildPrimevalStats(self,player):
		columns = [["individual"],["primevalDamage","primevalHealing"]]
		index = pd.MultiIndex.from_product(columns, names=["CATEGORY","STATS"])
		primevalStats = pd.DataFrame([[

			self.rawPlayerData[player]["extended"]["values"]["primevalDamage"]["basic"]["value"],
			self.rawPlayerData[player]["extended"]["values"]["primevalHealing"]["basic"]["value"]
			]], columns = index)

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
