##Ladder 'name', 'game', 'size'
##Events': [ ] 
##'Players': { 'name': elo}
##
##Event {'date': x, 'Base': { }, 'size': x, 'Sets': [ ]}
##Set = {'P1': 's', 'P2': 's', 'Matches': [ ]
##Match = [WINNER, char1, char2, Stage]
##
##PlayerIDS
##{'name': id}
##
##Players {'PIDs': { }, 'Data': [ ]}
##Data: {'last': EID, 'Ladders': [ ]}
##
##Ladder = {'LID': x, 'played': x, 'Scores': { }}
##Score = 'Opp': {'last': x, 'W': x, 'L': x}
##
##Queue {'Event': LID' 'setups': x, 'InProg': [ ], 'Queue': []}
##InProg {'P1': 's', 'P2': 's'}
##
##Reserved: { 'name': qid }

import json
import datetime

from flask import Flask

app = Flask(__name__)
@app.route("/")
def hello():
	return "1";
#	return render_template('app/index.html')
	
if __name__ == "__main__":
	app.run()

path = "C:/Users/admin/Documents/smash/"
LADDERS = []
PLAYERS = {}
PLDATA = []

QUEUES = []
RESERVED = { }
EVENT = 0

VARI = 32
SEARCH = 2
BASEELO = 1200

##Players {'PIDs': { }, 'Data': [ ]}
def load():
    f = open(path + 'ladder.jsn')
    LADDERS.extend(json.load(f))
    f.close()
    f = open(path + 'player.jsn')
    player = json.load(f)
    PLAYERS.update(player['PIDs'])
    PLDATA.extend(player['Data'])
    f.close()

def save():
    f = open(path + 'ladder.jsn', mode='w+')
    json.dump(LADDERS, f, indent=2)
    f.close()
    player = {'PIDs': PLAYERS, 'Data': PLDATA}
    f = open(path + 'player.jsn', mode='w+')
    json.dump(player, f, indent=2)
    f.close()
    

##Ladder 'name', 'game' 'size' Events': [ ] 'Players': { }
def newLadder(name, game):
    ladder = {'Ladder': name, 'game': game, 'size': 0, 'Events': [], 'Players': {} }
    LADDERS.append(ladder)

##PlayerIDS {'name': id}
##Players {'PIDs': { }, 'Data': [ ]}
##Data: {'last': EID, 'Ladders': [ ]}
def newPlayer(name):
    newid = len(PLAYERS)
    PLAYERS[name] = newid

    data = {'last': -1, 'Ladders': []}
    PLDATA.append(data)

def newEntrant(name):
    newPlayer(name)
    for x in range (len(LADDERS)):
        addPlayer(name, x, BASEELO)
    
##Ladder 'name', 'game' 'size' Events': [ ] 'Players': { }
##'Players': { 'name': elo}
##Ladder = {'LID': x, 'played': x, 'Scores': { }}
def addPlayer(name, lid, elo):
    LADDERS[lid]['Players'][name] = elo
    LADDERS[lid]['size'] += 1

    lad = {'LID': lid, 'played': 0, 'Scores': {}}
    PLDATA[PLAYERS[name]]['Ladders'].append(lad)

    
##Queue {'Event': LID' 'setups': x, 'InProg': [ ], 'Queue': []}
##InProg {'P1': 's', 'P2': 's'}
##Event {'date': x, 'Base': { }, 'size': x, 'Sets': [ ]}
##Reserved: { 'name': qid }

def newEvent(lid, setups):
    newQueue(lid, setups)

    event = {'Date': datetime.date.today().isoformat(), 'Base': dict(LADDERS[lid]['Players']), 'size': 0, 'Sets': []}
    LADDERS[lid]['Events'].append(event)

def newQueue(lid, setups):
    queue = {'Event': lid, 'setups': setups, 'InProg': [], 'Queue': []}
    QUEUES.append(queue)

##Ladder 'name', 'game' 'size' Events': [ ] 'Players': { }
def fillQueue(qid):
    lid = QUEUES[qid]['Event']
    size = LADDERS[lid]['size']
    for x in LADDERS[lid]['Players'].keys():
        addToQueue(qid, x)

def addToQueue(qid, name):
    QUEUES[qid]['Queue'].append(name)
    
def printQueue(qid):
    lid = QUEUES[qid]['Event']
    print("Queue for:", LADDERS[lid]['Ladder'])
    for x in QUEUES[qid]['InProg']:
        print("In Progress:", x['P1'], "vs", x['P2'])
    s = 'Queue: '
    for x in QUEUES[qid]['Queue']:
        s += x + ", "
    print(s)

def findPlayerScore(name, lid):
    pid = PLAYERS[name]
    data = PLDATA[pid]['Ladders']

    for x in range(0, len(data)):
        if(data[x]['LID'] == lid):
            return x
    return -1
	
def getPlayerElo(lid, name):
    return LADDERS[lid]['Players'][name]
	
##Event {'date': x, 'Base': { }, 'size': x, 'Sets': [ ]}
##Set = {'P1': 's', 'P2': 's', 'Matches': [ ]
##Match = [WINNER, char1, char2, Stage]
##Ladder = {'LID': x, 'played': x, 'Scores': { } }
##Score = {'last': x, 'W': x, 'L': x}

def setResult(qid, progid, matches):
    prog = QUEUES[qid]['InProg'][progid]
    lid = QUEUES[qid]['Event']

    #record match in event
    aset = {'P1': prog['P1'], 'P2': prog['P2'], 'Matches': matches}
    eid = len(LADDERS[lid]['Events']) - 1
    LADDERS[lid]['Events'][eid]['Sets'].append(aset)
    LADDERS[lid]['Events'][eid]['size'] += 1

    #update ladder scores between both players
    sc1 = 0
    sc2 = 0
    for x in matches:
        if(x[0] == 0):
            sc1 += 1
        else:
            sc2 += 1
    updateScore(lid, prog['P1'], prog['P2'], sc1, sc2)
    updateScore(lid, prog['P2'], prog['P1'], sc2, sc1)

    #change elos based on results
    one = LADDERS[lid]['Players'][prog['P1']]
    two = LADDERS[lid]['Players'][prog['P2']]

    ch1 = (one / (one + two)) * VARI * sc1
    ch2 = (two / (one + two)) * VARI * sc2
    LADDERS[lid]['Players'][prog['P1']] += ch1
    LADDERS[lid]['Players'][prog['P2']] -= ch1
    LADDERS[lid]['Players'][prog['P1']] -= ch2
    LADDERS[lid]['Players'][prog['P2']] += ch2

    #readd to queue
    QUEUES[qid]['Queue'].append(prog['P1'])
    QUEUES[qid]['Queue'].append(prog['P2'])
    del QUEUES[qid]['InProg'][progid]

##Data: {'last': EID, 'Ladders': [ ]}
##
##Ladder = {'LID': x, 'played': x, 'Scores': { }}
##Score = {'last': x, 'W': x, 'L': x}
def updateScore(lid, p1, p2, sc1, sc2):

    sid = findPlayerScore(p1, lid)
    PLDATA[PLAYERS[p1]]['last'] = EVENT
    PLDATA[PLAYERS[p1]]['Ladders'][sid]['played'] += 1

    scores = PLDATA[PLAYERS[p1]]['Ladders'][sid]['Scores']
    eid = len(LADDERS[lid]['Events']) - 1
    
    if(p2 in scores):
        scores[p2]['W'] += sc1
        scores[p2]['L'] += sc2
        scores[p2]['last'] = eid
    else:
        scores[p2] = {'W': sc1, 'L': sc2, 'last': eid}



##matchmaking holy moly

##InProg {'P1': 's', 'P2': 's'}
def callMatch(qid, p1, p2):
    match = {'P1': p1, 'P2': p2}
    QUEUES[qid]['InProg'].append(match)
    QUEUES[qid]['Queue'].remove(p1)
    QUEUES[qid]['Queue'].remove(p2)
    RESERVED[p1] = qid
    RESERVED[p2] = qid


def matchMake(qid, deep):
    tque = list(QUEUES[qid]['Queue'])
    tque = [tque[x] for x in range(len(tque)) if tque[x] not in RESERVED]
    lad = QUEUES[qid]['Event']
    select = QUEUES[qid]['setups'] * SEARCH

    while(deep > 0 and len(tque) >= 2):
        pl1 = tque[0]
        tque.remove(pl1)
        if(select > len(tque)):
           select = len(tque)
        opp = [tque[x] for x in range(select)]
        pl2 = getBestOpp(qid, pl1, opp)
        print("callMatch(" + str(qid) + ", '" + pl1 + "', '" + pl2 + "')")
        tque.remove(pl2)
        deep -= 1
           
def getBestOpp(qid, pl1, que):
    lid = QUEUES[qid]['Event']
    eid = len(LADDERS[lid]['Events']) - 1

    diff = 10000
    opp = ''

    check = [que[x] for x in range(len(que)) if not isRecent(lid, pl1, que[x])]
    if(len(check) == 0):
        check = que
        
    for x in range(len(check)):
        temp = abs(getPlayerElo(lid, pl1) - getPlayerElo(lid, check[x]))
        if(diff > temp):
            diff = temp
            opp = check[x]
    return opp
        

def isRecent(lid, pl1, pl2):
    eid = len(LADDERS[lid]['Events']) - 1
    sid = findPlayerScore(pl1, lid)
    scores = PLDATA[PLAYERS[pl1]]['Ladders'][sid]['Scores']
    if(pl2 in scores and scores[pl2]['last'] == eid):
        return True
    else:
        return False
        

##Ladder = {'LID': x, 'played': x, 'Scores': { }}
##Score = {'last': x, 'W': x, 'L': x}
def DATAFIX(ver):
    ## Make all names lower case
    if(ver == 0):
        for x in LADDERS:
            #Ladder Elos
            for y in iter(x['Players']):
                if not y.islower():
                    x['Players'][y.lower()] = x['Players'][y]
                    del x['Players'][y]
            #Match names
            for y in x['Events']:
                for z in y['Sets']:
                    if not z['P1'].islower():
                        z['P1'] = z['P1'].lower()
                    if not z['P2'].islower():
                        z['P2'] = z['P2'].lower()   
        for x in iter(PLAYERS):
            if not x.islower():
                PLAYERS[x.lower()] = PLAYERS[x]
                del PLAYERS[x]
        #this will break data if run again at this point
        for x in PLDATA:
            for y in x['Ladders']:
                newscores = {}
                for z in y['Scores']:
                    newscores[z['Opp'].lower()] = {'W': z['W'], 'L': z['L'], 'last': z['last']}
                y['Scores'] = newscores
                    
