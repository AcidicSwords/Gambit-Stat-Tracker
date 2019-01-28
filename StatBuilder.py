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
