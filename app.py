            
import sqlite3
from sqlite3 import Error


from flask import Flask, flash, redirect, render_template, request, session
import http.client
import json
from datetime import datetime
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

# address of football-data
connection = http.client.HTTPConnection('api.football-data.org')
# api token to authenicate
headers = { 'X-Auth-Token': '48c95f2cc36546cfb613a77b3466c08c' }

connectioncounter = 0

# function to create connection to SQLite DB
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

# create the db connection
if __name__ == '__main__':
    try:
        create_connection(r"C:\Users\killi\Documents\VS Code\footyflask\footyflask.db")
        print("db connection success")
    
    except:
        print("db connection fail")
        pass

# function to fetch teams json file 
def getTeams():
    print ("running getTeams")
    connection.request('GET', '/v2/teams/', None, headers )
    response = json.loads(connection.getresponse().read().decode())
    
    global connectioncounter
    connectioncounter += 1
    print("Number of connections made: " + str(connectioncounter))  

    # store teams part of json file as variable 
    try:
        teams = response['teams']
    except:
        print("Error in getTeams:")
        print(response)
    return teams



# function to fetch team id from teams variable for team selected by user in dropdown on index page
def getTeamID(teams):
    print ("running getTeamID")
    # fetch the value of the chosen team
    searchTeam = str(request.form.get("TeamPick"))

    # cycle through each team in file to check if a match is found for the team chosen
    for team in teams:
        if team['name'] == searchTeam:
            #print (team)
            # set teamid as string when match is found
            teamID = str(team['id'])
            break
    return teamID

# function to fetch the matches associated with the teamID supplied
def getMatchesForTeam(teamID):
    print ("running getMatchesForTeam")
    # connection.request('GET', '/v2/teams/' + teamID + '/matches?status=SCHEDULED', None, headers )
    # create a connection to the address of teams, including authentication header
    connection.request('GET', '/v2/teams/' + teamID + '/matches', None, headers)
    # store response json file in response variable
    response = json.loads(connection.getresponse().read().decode())
    global connectioncounter
    connectioncounter += 1
    print("Number of connections made: " + str(connectioncounter))

    # set matches variable to store matches part of json file
    matches = response['matches']
    print ("Matches pulled")
    matchcounter = 0
    for match in matches:
        matchcounter += 1
        
        try:
            teamID = str(match['homeTeam']['id'])
            match['homeTeam']['crestUrl'] = str(fetchteamCrestUrlfromTeamID(teamID))
            print ("Crest added for " + match['homeTeam']['name'])
            print (match['homeTeam']['crestUrl'])
            teamID = str(match['awayTeam']['id'])
            match['awayTeam']['crestUrl'] = str(fetchteamCrestUrlfromTeamID(teamID))
            print ("Crest added for " + match['awayTeam']['name']) 
            print (match['awayTeam']['crestUrl'])
        except:
            print ("failed to fetch crest for " + match['homeTeam']['crestUrl'] + " vs " + match['awayTeam']['id'])
            pass

        print ("pulled crest for " + str(matchcounter) + " teams")
    print ("Finished pulling crests for Matches")
    return matches

# function to fetch competitions json file and store as a variable
def getCompetitions():
    print ("running getCompetitions")
    connection.request('GET', '/v2/competitions/', None, headers )
    response = json.loads(connection.getresponse().read().decode())
    global connectioncounter
    connectioncounter += 1
    print("Number of connections made: " + str(connectioncounter))

    tidiedComps = []

    competitions = response['competitions']
    for comp in competitions:
        # if comp['code'] == None:
        #     print (str(comp['name']) + " deleted - no league code")
        #     del comp
            
        # elif comp['plan'] != "TIER_ONE":
        #     print (str(comp['name']) + " deleted - not tier one")
        #     del comp
        if comp['plan'] == "TIER_ONE":
            print (str(comp['name']) + " added to tidied list")
            tidiedComps.append(comp)

    #print(tidiedComps)
    return tidiedComps


# function to retrieve competition code from a competition selected in page
def getCompetitionCode(competitions):
    print ("running getCompetitionCode")
    # retrieve competition selected by user
    searchComp = str(request.form.get("CompPick"))
    # set competitions variable to hold the correct section
    #competitions = competitions['competitions']
    print ("Competition selected is: " + searchComp)
    for competition in competitions:
        if competition['name'] == searchComp and competition['code'] != None and competition['plan'] == "TIER_ONE":
            print ("Match found for Competition Selected")
            competitionCode = str(competition['code'])
            print("Competition code is: " + competitionCode)
            break
    return competitionCode
# function to retrieve teams belonging to competition identified by code passed in
def getTeamsFromCompetitionCode(competitionCode):
    print ("running getTeamsFromCompetitionCode")
    request = '/v2/competitions/' + competitionCode + '/teams'
    connection.request('GET', '/v2/competitions/' + competitionCode + '/teams', None, headers)
    response = json.loads(connection.getresponse().read().decode())
    global connectioncounter
    connectioncounter += 1
    print("Number of connections made: " + str(connectioncounter))
    
    #print("compteams response below:")
    #print (request)
    #print (response)
    compTeams = response['teams']

    return compTeams

# function to generate the url of team logos displayed on page
def fetchteamCrestUrlfromTeamID(teamID):
    print ("running fetchteamCrestUrlfromTeamID for team #" + teamID)

    # #####################################
    # #####  THIS BLOCK OF CODE WAS CAUSING TOO MANY REQUESTS FROM API
    # #####################################
    # #connection.request('GET', '/v2/teams/' + teamID + '/matches?status=SCHEDULED', None, headers )
    # # create a connection to the address of teams, including authentication header
    # connection.request('GET', '/v2/teams/' + teamID , None, headers)
    # # store response json file in response variable
    # response = json.loads(connection.getresponse().read().decode())

    # # set matches variable to store matches part of json file
    # teamCrestUrl = str(response['crestUrl'])
    
    ########################################
    # simplified version - just assumes crest URL format
    teamCrestUrl = "https://crests.football-data.org/" + str(teamID) + ".svg"

    return teamCrestUrl

# tasks run prior to loading pages

# use get comps function to retrieve competitions and store in variable for searching
#competitions = getCompetitions()
# use the function to store teams for searching
#teams = getTeams()

teams = []
compTeams = []

# homepage code
@app.route("/", methods=["GET", "POST"])
def home():
    global teams
    global compTeams
    if request.method == "POST":
        # try:
        #     competitions = getCompetitions()
        #     #competitions = competitions['competitions']
        # except:
        #     pass

        if "searchTeamBtn" in request.form:

            print("HERES WHATS IN REQUEST.FORM")
            print(request.form)

            # fetch matches for a team selected
            print ("running fetch matches for homepage")
            try:
                print ("got this far 1")
                competitions = getCompetitions()
                print ("got this far 2")
                teams = getTeams()
                print ("got this far 3")
                try:
                    teamID = getTeamID(compTeams)
                except:
                    print("failed to find team in compTeams var, trying with default teams list")
                    teamID = getTeamID(teams)
                print ("got this far 4")
                matches = getMatchesForTeam(teamID)
                print ("got this far 5")

                # code to format date of matches nicely
                for match in matches:
                    #print (str(match) + '\n')
                    print ("formatting date of " + match['homeTeam']['name'] + " vs " + match['awayTeam']['name'])
                    date = datetime.strptime(match['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
                    #date = str(datetime.date(date))
                    match['utcDate'] = date
                    print(match)
                print ("finished formatting dates for matches")

                return render_template("index.html", matches=matches, teams=teams, competitions=competitions)
                #return render_template("index.html", matches=matches)
                #return render_template("index.html", teams=teams, competitions=competitions)
            except:
                print ("Failed running fetch matches")
                pass
        
        elif "searchCompBtn" in request.form:

            # fetch teams for a selected competition
            print ("running fetch teams for selected competition")
            try:
                #teams = getTeams()
                competitions = getCompetitions()
                #print ("1homepage output:")
                #print (competitions)
                competitionCode = getCompetitionCode(competitions)
                #print ("2homepage output:")
                #print (competitionCode)
                compTeams = getTeamsFromCompetitionCode(competitionCode)
                teams = compTeams
                #print ("3homepage output:")
                #print (compTeams)

                return render_template("index.html", teams=teams, compTeams=compTeams, competitions=competitions)
            except:
                print ("failed running fetch teams for selected comps")

                print ("loading default homepage")
                teams = getTeams()
                competitions = getCompetitions()
                #competitions = competitions['competitions']
                #print ("Following comps are pulled:")
                #print (competitions)

                return render_template("index.html", teams=teams, competitions=competitions)
        
        
    # get request / default page - load teams and competitions into dropdowns
    else: 
        print ("loading default homepage")
        #check if teams exists, if not - get default teams list
        try: teams
        except NameError: teams = getTeams()
        #teams = getTeams()
        competitions = getCompetitions()
        #competitions = competitions['competitions']
        #print ("Following comps are pulled:")
        #print (competitions)

        return render_template("index.html", teams=teams, competitions=competitions)
        
@app.route("/about")
def about():
    return render_template("about.html")






    # for match in matches:
    #     #print (str(match) + '\n')
    #     date = datetime.strptime(match['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
    #     print (match['homeTeam']['name'] + ' vs ' + match['awayTeam']['name'] + ' ' + str(datetime.date(date)))
    #     print ('\n')


# def home():
#     if request.method == "POST":
#         searchTeam = str(request.form.get("TeamPick"))
#         print('Search team = ' + searchTeam)
        
#         for team in teams:
#             if team['name'] == searchTeam:
#                 print (team)
#                 teamID = str(team['id'])

#         connection.request('GET', '/v2/teams/' + teamID + '/matches?status=SCHEDULED', None, headers )
#         response = json.loads(connection.getresponse().read().decode())

#         matches = response['matches']
#         for match in matches:
#             #print (str(match) + '\n')
#             date = datetime.strptime(match['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
#             date = str(datetime.date(date))
#             match['utcDate'] = date

#             #print (match['homeTeam']['name'] + ' vs ' + match['awayTeam']['name'] + ' ' + str(datetime.date(date)))
#             #print ('\n')
#         return render_template("index.html", matches=matches, teams=teams)

#     

    #return render_template("index.html", userlist = users, transactionsList = transactions, stocksList = stocks, userCash = userCash)


