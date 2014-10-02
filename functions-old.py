import re
from datetime import datetime
from datetime import timedelta
import cards
from random import shuffle

def actioner(g, line, username, channel, gamechannel):

    lower = line.lower()

    messages = []

    if g.inprogress:          
        if lower == "start":
            messages.append({"message": "Could not start because game is already in progress", "channel": gamechannel})
    else:
        if lower == "start":
            if len(g.players) >= g.minplayers:
                starttime = datetime.now()
                timetostart = 2
                g.starttime = datetime.now() + timedelta(seconds = timetostart)
                messages.append({"message": "Starting game in %s seconds" % timetostart, "channel": gamechannel})
            else:
                messages.append({"message": "Could not start because there aren't enough players", "channel": gamechannel})


    if lower == "stop":
        messages.append({"message": "The game is over! The final scores are as follows:", "channel": channel})
        for player in g.players:
            messages.append({"message": "%s: %s" %(player.username, player.score), "channel": channel})
        stopmessage = g.stop()
        messages.append({"message": stopmessage, "channel": gamechannel})


    elif lower == "gamestatus":
        messages.append({"message": g.inprogress, "channel": gamechannel})

    elif lower == "players":
        if g.players:
            playernames = []
            for player in g.players:
                playernames.append(player.username)
            playerstring = " ".join(playernames)
            messages.append({"message": "Players: %s" % playerstring, "channel": gamechannel})
        else:
            messages.append({"message": "No players have joined the game", "channel": gamechannel})

    elif lower == "join":
        newplayer = g.getPlayerByName(username)
        block = 0
        for player in g.players:
            if username == player.username:
                block = 1
        if block == 1:
            messages.append({"message": "Error, cannot join game, you're already in it", "channel": gamechannel})
        else:
            newPlayer = Player(username)
            g.players.append(newPlayer)
            messages.append({"message": "%s joined the game" %username, "channel": gamechannel})
            g.dealCards()
            if g.inprogress:
                messages += [{"message": g.blackcard, "channel": username}]
                messages += newPlayer.printCards()

    elif lower == "part":
        message = g.part(username)
        if message:
            messages += [{"message": message, "channel": gamechannel}]

    elif lower == "czar":
        if g.inprogress:
            messages.append({"message": "The Card Czar is %s" %g.czar.username, "channel": gamechannel})
        else:
            messages.append({"message": "There is no Card Czar yet", "channel": gamechannel})
    elif lower[:5] == "kill ":
        messages.append({"message": "DIE %s DIE!" % line[5:].upper(), "channel": gamechannel})

    elif lower == "cards":
        player = g.getPlayerByName(username)
        messages += player.printCards()

    elif lower == "countcards":
        messages.append({"message": "There are %s cards remaining" % len(g.wcards), "channel": gamechannel})

    elif lower == "$playedcards":
        messages.append({"message": g.playedCards, "channel": channel})

    elif lower == "scores":
        messages.append({"message": "The scores are as follows:", "channel": channel})
        for player in g.players:
            messages.append({"message": "%s: %s" %(player.username, player.score), "channel": channel})

    elif lower == "random":
        g.wcards = cards.wcards()
        g.bcards = cards.bcards()
        g.bcards2 = cards.bcards2()
        g.allbcards = []
        for card in g.bcards:
            g.allbcards += [{"card": card, "type": 1}]
        for card in g.bcards2:
            g.allbcards += [{"card": card, "type": 2}]
        shuffle(g.allbcards)
        shuffle(g.wcards)
        blackcard = g.allbcards.pop(0)
        g.blackcard = blackcard["card"]
        g.blacktype = blackcard["type"]
        if g.blacktype == 2:
            whitecard1 = g.wcards.pop(0)
            whitecard2 = g.wcards.pop(0)
            messages.append({"message": g.blackcard, "channel": gamechannel})
            messages.append({"message": whitecard1, "channel": gamechannel})
            messages.append({"message": whitecard2, "channel": gamechannel})
        else:
            whitecard = g.wcards.pop(0)
            messages.append({"message": g.blackcard, "channel": gamechannel})
            messages.append({"message": whitecard, "channel": gamechannel})

    elif lower == "test":
        messages.append({"message": "testing functions", "channel": gamechannel})
    elif lower == "wcards":
        print g.wcards
    elif lower == "bcards":
        print g.bcards
    elif lower == "bcards2":
        print g.bcards2
    elif lower == "quit res0n4t0r":
        exit("Asked to quit by %username")
    return messages

def gameLogic(g, line, username, channel, gamechannel):
    if line:
        lower = line.lower()
    messages = []

    if len(g.players) < g.minplayers:
        if g.starttime or g.inprogress:
            g.stop()


    if g.starttime:
        currtime = datetime.now()
        if currtime > g.starttime:
            g.starttime = None
            g.inprogress = True
            shuffle(g.players)
            messages.append({"message": "Starting game now!", "channel": gamechannel})

    elif g.newround > g.round:
        if not g.czar:
            g.czar = g.players[0]
        g.round = g.newround
        if g.currentround < g.totalrounds:
            messages.append({"message": "Starting round %s. The Card Czar is %s" %(g.newround, g.czar.username), "channel": gamechannel})
            g.dealCards()
            blackcard = g.allbcards.pop(0)
            g.blackcard = blackcard["card"]
            g.blacktype = blackcard["type"]
            for player in g.players:
                if not g.czar == player:
                    messages += [{"message": g.blackcard, "channel": player.username}]
                    if g.blacktype == 2:
                        messages.append({"message": "Please select your cards by typing in the format x y", "channel": player.username})
                    messages += player.printCards()
            #g.setTopic()
            messages.append({"message": g.blackcard, "channel": gamechannel})
            g.waitPlayers = 1
            g.currentround += 1
        else:
            messages.append({"message": "The game is over! The final scores are as follows:", "channel": channel})
            for player in g.players:
                messages.append({"message": "%s: %s" %(player.username, player.score), "channel": channel})
            g.stop()

    elif g.waitPlayers > 0:
        #print g.playedCards
        if g.waitPlayers == 1:
            messages.append({"message": "The Players must each pick a card, by messaging the number to bah", "channel": gamechannel})
            if g.blacktype == 2:
                messages.append({"message": "Please select your cards by typing in the format x y", "channel": gamechannel})
            g.waitPlayers = 2
        if len(g.playedCards) == len(g.players) - 1:
            g.waitPlayers = 0
            g.waitCzar = 1
        elif line:
            if g.blacktype == 1:
                if re.search("^[0-9]+$", line) and not username == g.czar.username:
                    id = int(line)
                    if id == 0:
                        id = 10
                    id -= 1
                    if id < 10 and id >= 0:
                        player = g.getPlayerByName(username)
                        card = player.hand.pop(id)
                        messages += [{"message": "Thank you for playing %s" %(card), "channel": player.username}]
                        g.playedCards.append({"card": card, "owner": player})
            elif g.blacktype == 2:
                if re.search("^[0-9]+ [0-9]+$", line) and not username == g.czar.username:
                    ids = line.split()
                    id1 = int(ids[0])
                    id2 = int(ids[1])
                    if id1 == 0:
                        id1 = 10
                    id1 -= 1
                    if id2 == 0:
                        id2 = 10
                    id2 -= 1
                    if id1 < 10 and id1 >= 0 and id2 < 10 and id2 >=0:
                        player = g.getPlayerByName(username)
                        card1 = player.hand[id1]
                        card2 = player.hand[id2]
                        messages += [{"message": "Thank you for playing %s / %s" %(card1, card2), "channel": player.username}]
                        g.playedCards.append({"card": "%s / %s" %(card1, card2), "owner": player})
                        player.hand.remove(card1)
                        player.hand.remove(card2)
    elif g.waitCzar > 0:
        if g.waitCzar == 1:
            shuffle(g.playedCards)
            messages.append({"message": "The Czar, %s, must pick a card" % g.czar.username, "channel": gamechannel})
            messages.append({"message": g.blackcard, "channel": gamechannel})
            i = 1
            spacer = "  "
            for card in g.playedCards:
                if i > 9:
                    spacer = " "
                messages.append({"message": "%s)%s%s" %(i, spacer, card["card"]),"channel": gamechannel})
                i += 1
            g.waitCzar = 2
        elif line and g.waitCzar == 2:
            if re.search("^[0-9]+$", line) and username == g.czar.username:
                cardID = int(line) - 1
                if cardID < len(g.playedCards) and cardID >= 0:
                    cardText = g.playedCards[cardID]["card"]
                    cardOwner = g.playedCards[cardID]["owner"]
                    messages.append({"message": "The Czar picked card %s: %s %s has won the round!" %(cardID + 1, cardText, cardOwner.username), "channel": gamechannel})
                    cardOwner.score += 1
                    g.waitCzar = 0
                    g.newround += 1
                    g.discardedCards.append(g.playedCards)
                    g.playedCards = []
                    i = 0
                    for player in g.players:
                        if player == g.czar:
                            czarid = i
                        i += 1
                    czarid +=1
                    if czarid > len(g.players) -1:
                        czarid = 0
                    g.czar = g.players[czarid]

    return messages

class Player():
    def __init__ (self, username):
        self.username = username
        self.hand = []
        self.score = 0

    def printCards(self):
        messages = [{"message": "Your cards are:", "channel": self.username}]
        i = 1
        cards = ""
        for card in self.hand:
            cards += "%s) %s " % (i,card)
            i += 1
        messages.append({"message": cards, "channel": self.username})
        return messages



class Game():
    def __init__(self, s):
        self.inprogress = False
        self.players = []
        self.starttime = None
        self.inchannel = False
        self.minplayers = 3
	self.totalrounds = 21
	self.currentround = 1
        self.round = 0
        self.newround = 1
        self.played = []
        self.czar = None
        self.wcards = cards.wcards()
        self.bcards = cards.bcards()
        self.bcards2 = cards.bcards2()
        self.allbcards = []
        self.playedCards = []
        self.discardedCards = []
        self.blackcard = None
        self.blacktype = None
        for card in self.bcards:
            self.allbcards += [{"card": card, "type": 1}]
        for card in self.bcards2:
            self.allbcards += [{"card": card, "type": 2}]
        shuffle(self.wcards)
        shuffle(self.allbcards)
        self.threadDetails = s

    def stop(self):
        self.__init__(self.threadDetails)
    #    self.inprogress = False
    #    self.starttime = None
    #    self.players = []
    #    self.round = 0
    #    self.czar = 0
    #    self.wcards = cards.wcards()
    #    self.bcards = cards.bcards()
    #    self.bcards2 = cards.bcards2()
    #    self.waitPlayers = 0
    #    self.playedCards = []
    #    self.newround = 1
    #    
    #    shuffle(self.wcards)
        #self.threadDetails.s.send("TOPIC %s :Welcome to Chat Against Humanity. Visit http://www.chatagainsthumanity.com for a list of commands.\n" %(self.threadDetails.channel))
        return "Stopping game"
    def dealCards(self):
        for player in self.players:
            toDeal = 10 - len(player.hand)
            while toDeal > 0:
                if len(self.wcards) == 0:
                    shuffle(self.discardedCards)
                    self.wcards = self.discardedCards
                    self.discardedCards = []
                card = self.wcards.pop()
                player.hand.append(card)
                toDeal -= 1

    def getPlayerByName(self, username):
        for player in self.players:
            if player.username == username:
                return player
        return False

    #def setTopic(self):
    #    self.threadDetails.s.send("TOPIC %s :%s\n" %(self.threadDetails.channel, self.blackcard))

    def part(self, playername):
        cont = False
        for player in self.players:
            if player.username == playername:
                cont = True
        if cont:
            message = "%s left the game." %playername
            if len(self.players) -1 < self.minplayers and self.inprogress:
                message += "Not enough players to continue! Stopping game."
                stop = self.stop()
            else:
                if self.inprogress:
                    for player in self.players:
                        if player.username == playername:
                            if player == self.czar:
                                if self.playedCards:
                                    for card in self.playedCards:
                                        owner = card["owner"]
                                        owner.hand.append(card["card"])
                                self.playedcards = []
                                self.blackcard = None
                                self.newround += 1
                                self.waitPlayers = 0
                                self.waitCzar = 0
                                i = 0
                                for newplayer in self.players:
                                    if newplayer == self.czar:
                                        czarid = i
                                    i += 1
                                czarid +=1
                                if czarid > len(self.players) -1:
                                    czarid = 0
                                self.czar = self.players[czarid]
                            self.players.remove(player)

                else:
                    for player in self.players:
                        if player.username == playername:
                            self.players.remove(player)
        else:
            message = None
        return message

