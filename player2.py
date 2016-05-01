from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import json
import pygame
from pygame.locals import *
import sys

server = 'student03.cse.nd.edu'
port = 40083

def is_json(data):
	try:
		json.loads(data)
		return True
	except ValueError, e:
		return False

class ClientConnFactory(ClientFactory):
	def buildProtocol(self, addr):
		return  ClientConnection()

class ClientConnection (Protocol):
	def __init__(self):
		pygame.init()
		self.size = self.width, self.height = 480, 852
		self.black = 0, 0, 0
		self.green = 0, 255, 0
		self.white = 255, 255, 255
		self.screen = pygame.display.set_mode(self.size)
		self.tower_image = pygame.image.load("tower.png")

	def dataReceived(self, data):
		# get game data sent over
		json_data = data.split('?', 1)[0]
		if is_json(json_data):
			game = json.loads(json_data)
			print "Received data: " + json_data
		else:
			# This can happen when the transport stream is fragmented and the
			# end of one json string is sent over that is incomplete
			# This is uncommon, and can be ignored
			return

		playersDict = game["players"]
		for player in playersDict:
			towers = player["towers"]
			for tower in towers:
				x_pos = tower["x_pos"]
				y_pos = tower["y_pos"]
    			screen.blit(
					self.tower_image,
					(x_pos, y_pos)
				)		
			army = player["army"]
			for troop in army:
				troop_image = pygame.image.load(filename) 
				x_pos = tower["x_pos"]
				y_pos = tower["y_pos"]
    			screen.blit(
					troop_image,	
					(x_pos, y_pos)
				)		
			playerMana = player["mana"]
			playerMaxMana = player["max_mana"]

		# draw background, players and ball
		self.screen.fill(self.green)
		
		pygame.display.flip()
		
		for event in pygame.event.get():
			if event.type == QUIT:
				print "Quit event found"
				#pygame.quit()
		        #self.transport.loseConnection()

		#send back key presses
		keysPressed = pygame.key.get_pressed()
		up = keysPressed[pygame.K_UP]
		down = keysPressed[pygame.K_DOWN]
		self.transport.write( str(up) + "|" + str(down) + "?" )
		
	def connectionMade(self):
		print "connected to game server"
			
	def connectionLost(self, reason):
		reactor.stop()
	
if __name__ == '__main__':
	reactor.connectTCP(server, port, ClientConnFactory())
	reactor.run()
