from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import json
import pygame
from pygame.locals import *
import sys

server = 'student01.cse.nd.edu'
port = 40083

def getRect(x_pos, y_pos, width, height):
	return pygame.Rect(x_pos - width / 2, y_pos - height / 2, width, height)

class ClientConnFactory(ClientFactory):
	def buildProtocol(self, addr):
		return  ClientConnection()

def is_json(data):
	try:
		json.loads(data)
		return True
	except ValueError, e:
		return False

class ClientConnection (Protocol):
	def __init__(self):
		pygame.init()
		self.size = self.width, self.height = 640, 480
		self.black = 0, 0, 0
		self.white = 255, 255, 255
		self.red = 255, 0, 0
		self.screen = pygame.display.set_mode(self.size)
		self.count = 0

	def dataReceived(self, data):
		self.count += 1
		print self.count
		# get game data sent over
		json_data = data.split('?', 1)[0]
		if is_json(json_data):
			game = json.loads(json_data)
		else:
			# This can happen when the transport stream is fragmented and the
			# end of one json string is sent over that is incomplete
			# This is uncommon, and can be ignored
			return
		p1 = game["players"]["p1"]
		p2 = game["players"]["p2"]
		
		# determine areas to draw players and ball
		p1rect = getRect(p1["x_pos"], p1["y_pos"], p1["width"], p1["height"])
		p2rect = getRect(p2["x_pos"], p2["y_pos"], p2["width"], p2["height"])
		ballPos = (int(game["ball"]["x_pos"]), int(game["ball"]["y_pos"]))
		
		# draw background, players and ball
		self.screen.fill(self.black)
		pygame.draw.rect(self.screen, self.white, p1rect)
		pygame.draw.rect(self.screen, self.white, p2rect)
		pygame.draw.circle(self.screen, self.red, ballPos, int(game["ball"]["radius"]))
		
		# draw the score
		myfont = pygame.font.SysFont("monospace", 42)
		score_label = myfont.render(str(p1["score"]) + " | " + str(p2["score"]), 1, self.white)
		self.screen.blit(score_label, (260, 20))

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
		#print str(up) + "|" + str(down)
		self.transport.write( str(up) + "|" + str(down) + "?" )
		
	def connectionMade(self):
		print "connected to game server"
		# draw menu
		self.screen.fill(self.black)
		myfont = pygame.font.SysFont("monospace", 72)
		title_label = myfont.render("Pong", 1, self.white)
		myfont = pygame.font.SysFont("monospace", 32)
		select_label = myfont.render("Select a number of players:", 1, self.white)
		oneOrTwo_label = myfont.render("1 or 2", 1, self.white)
		self.screen.blit(title_label, (220, 100))
		self.screen.blit(select_label, (60, 250))
		self.screen.blit(oneOrTwo_label, (250, 300))
		pygame.display.flip()
		key = self.waitForKey()
		if key == 2:
			self.transport.write("two players")
			self.screen.fill(self.black)
			myfont = pygame.font.SysFont("monospace", 32)
			connected_label = myfont.render("CONNECTED TO SERVER", 1, self.white)
			waiting_label = myfont.render("WAITING FOR PLAYER 2", 1, self.white)
			self.screen.blit(connected_label, (120, 100))
			self.screen.blit(waiting_label, (112, 200))
			pygame.display.flip()
		elif key == 1:
			self.tranport.write("one player")
		else:
			pass
			
	def waitForKey(self):
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					reactor.stop()
				if event.type == KEYDOWN and event.key == K_1:
					return 1
				if event.type == KEYDOWN and event.key == K_2:
					return 2
		
	def connectionLost(self, reason):
		reactor.stop()
	
if __name__ == '__main__':
	reactor.connectTCP(server, port, ClientConnFactory())
	reactor.run()
