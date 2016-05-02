import os
import json
import pygame
from pygame.locals import *

from twisted.internet.protocol import Protocol, Factory
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

from objects import Player, Tower, Playable

PLAYER_ONE_PORT = 40075
PLAYER_TWO_PORT = 40083

player_one_connected = False
player_two_connected = False
p1Server = None
p2Server = None
gs = None

class GameSpace:
	def __init__(self):
		self.size = self.width, self.height = 480, 852
		self.speed = 12.0

		self.player1 = Player(self)
		self.player2 = Player(self)

		self.lc = LoopingCall(self.game_loop_iterate)
		self.lc.start(1.0/20)	

	def game_loop_iterate(self):
		self.player1.tick()
		self.player2.tick()

		p1Server.transport.write(self.to_json() + "?")
		p2Server.transport.write(self.to_json() + "?")

	def to_json(self):
		""" Creates a dictionary @gsData that represents the gamestate.
				Important for sending game data over our server so that a client
				can properly display the GameState
			  Returns: @gsData converted to json
		"""
		gsData = {
			"players": {
				"p1": self.player1.to_dict(),
				"p2": self.player2.to_dict(),
			},
		}
		return json.dumps(gsData)


class P1ServerFactory(Factory):
	def buildProtocol(self, addr):
		global p1Server
		p1Server = P1Server(addr)
		return p1Server

class P1Server(Protocol):
	def __init__(self, addr):
		self.addr = addr

	def dataReceived(self, data):
		#print "Received data: "  + data
		pass

	def connectionMade(self):
		print "Player 1 connected"
		global player_one_connected, player_two_connected
		player_one_connected = True
		if player_two_connected:
			print "Both players connected"
			global gs
			gs = GameSpace()

	def connectionLost(self, reason):
		print "Connection lost to player 1"
		global player_one_connected, player_two_connected
		player_one_connected = False

class P2ServerFactory(Factory):
	def buildProtocol(self, addr):
		global p2Server
		p2Server = P2Server(addr)
		return p2Server

class P2Server(Protocol):
	def __init__(self, addr):
		self.addr = addr

	def dataReceived(self, data):
		#print "Received data: "  + data
		pass

	def connectionMade(self):
		print "Player 2 connected"
		global player_one_connected, player_two_connected
		player_two_connected = True
		if player_one_connected:
			print "Both players connected"
			global gs
			gs = GameSpace()

	def connectionLost(self, reason):
		print "Connection lost to player 2"
		global player_one_connected, player_two_connected
		player_two_connected = False


if __name__ == '__main__':
	reactor.listenTCP(
		PLAYER_ONE_PORT,
		P1ServerFactory()
	)
	reactor.listenTCP(
		PLAYER_TWO_PORT,
		P2ServerFactory()
	)
	reactor.run()
