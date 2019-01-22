# MoteReport

# Concept and Vision

The idea behind the web application "MoteReport" is to develop a comprehensive stat tracker and post-game analysis for the game mode "Gambit" in Bungie's Destiny 2 By utilizing the publicly available Bungie API. The application will place emphasis of highlighting important stats vs a text dump of everything found on the API. As a Gambit player with 1200 games I have hand picked stats I believe important to showing player skill and contribution. 

There will be two main aspects to the web apllication. The first being career stats and the second being post-game analysis. Both aspects will combine a common set of stat categories as well as unique stats, these stats will then be displayed using powerful data visualization tools on the front end.

# Career

Career stats will be divided into all time and past 25 game averages. The thought process behind this is that although all time stats are useful they do not provide a snapshot of profile consistancy or improvement. When you have 1200 Games it requires a significant deviation from your previous stats over many games to move the stat even a marginal amount. By using the 25 game snapshot you will be able to realistiaclly gauge your performance. Below are the career specific stats being considered 

**Career Specific stats**
  * average winrate
  * weapon proficiency
  * medal collection
  * average team contribution to each category
  * custom tracker on profile for specific stat, ie army of one medals

# Post Game Report

Post game stats will be based off of your last Gambit match between all characters for the specified account and have a focus on displaying the relative strenghs of each player relative to their team. By taking each stat in each category for each player and comparing it to the team's total in that stat we will get a percentage contribution. For negative stats (such as deaths) the 1.0 - %contribution will be taken in order to accurately display the players "positive" impact. Furthermore each category will be totalled and averaged so that you can see the percent contribution in each category (example Motes, more on categories down below). These statistics are entirely based off of one PostGameCarnageReport and will be handled backend due to the massive amount of data needing to be reformmated.

**Post Game Specific Stats**
  * team roster
  * score (rounds for each team)
  * team totals

# How Data is Collected and manipulated

Using a users displayname and chosen platform a series of requests will get the PostGameCarnageReport from Bungie. From there a series of backend functions written in python will parse the PGCR into a JSON roughly 1/10th the size. This will be an intermediate datastructure that will be further augmented before being sent to the client.

Further augmentations will: analyze the data, build team totals, calculate player contribution in each category/stat, query the Destiny manifest to return weapon data (weapon name and image), get medals(not sure of the best way to do that), and export the searching players dataset to a database for career stat purposes. **The other player's data will not be databased unless they themselves request career stats**. The fully augmented data structure can then be sent client side where a JS frontend will be able to easily search the data by referencing the object hierachy and display the data using a mix of data visualisation tools. 

# Closing Thoughts

This project code is open source but I'd also like to say the project ideas are open source. I would love not only code contributions but idea contribution as well. If you know of any excellent frameworks or libraries that would synergize please contribute those. 

The project has an admirable goal and building career stats will be a computational nightmare as pulling the data will take hundreds of requests with a lot of missed requests (can pull 250 games at time but if there are not 250 you have to backtrack and request a different number until requesting one doesnt return anything, then you have to do that for all characters). I personally want to tackle this challenge providing we build or find an architecture to support it. The other idea would be to implement leaderboards but this relies on the successful creation of a database with an adequate number of users. **At this time we will not attempt to re-engineer every Gambit game played**

**Thanks For reading**

# TL;DR

  * Gambit stat tracker
  * Career and post game stats
  * Focus on displaying relevant stats
  * Focus on displaying player contribution to team in categories 
  * Usage of strong visual data representation
  

