import pygame
import random
from sets import Set
from math import hypot

class Player():
	def __init__(self, gs=None):
		self.gs = gs
		self.army = Set([
			Playable(),
			Playable(),
			Playable(),
			Playable()
		])
		self.mana = 6
		self.max_mana = 10
		self.towers = Set([
			Tower(gs.width * 1 / 4.0, gs.height / 4.0, 2000), 
			Tower(gs.width * 2 / 4.0, gs.height / 6.0, 3000), 
			Tower(gs.width * 3 / 4.0, gs.height / 4.0, 2000)
			#Tower(30, 30, 2000), 
			#Tower(60, 60, 3000), 
			#Tower(90, 90, 2000), 
		])

	def tick(self):
		pass

	def to_dict(self):
		armyDict = {}
		troopCount = 0
		for troop in self.army:
			armyDict["troop#" + str(troopCount)] = troop.to_dict()
			troopCount += 1
		towerDict = {}
		towerCount = 0
		for tower in self.towers:
			towerDict["tower#" + str(towerCount)] = tower.to_dict()
			towerCount += 1
		playerDict = {
			"mana": self.mana,
			"max_mana": self.max_mana,
			"army": armyDict,
			"towers": towerDict
		}
		return playerDict

class Tower(pygame.sprite.Sprite):
	def __init__(self, x_pos, y_pos, hp):
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.hp = hp

	def to_dict(self):
		return {
			"x_pos": self.x_pos,				
			"y_pos": self.y_pos,				
			"hp": self.hp
		}

class Playable(pygame.sprite.Sprite):
	def __init__(self):
		self.hp = 0
		self.attack_range = 0
		self.cost = 0
		self.x_pos = 0
		self.y_pos = 0
		self.damage_per_tick = 0
		self.move_amount_per_tick = 0
		self.image_name = None

	def to_dict(self):
		return {
			"x_pos": self.x_pos,				
			"y_pos": self.y_pos,				
			"hp": self.hp,
			"image_name": self.image_name
		}

	def attack(self, otherObject):
		otherObject.hp -= self.damage_per_tick

	def shouldDie(self):
		return self.hp <= 0

	def distanceTo(self, otherObject):
		return math.hypot(
			self.x_pos - otherObject.x_pos,
			self.y_pos, otherObject.y_pos
		)

	def isInRangeOf(self, otherObject):
		return self.distanceTo(otherObject) <= self.attack_range

	def moveTowards(self, otherObject):
		""" Moves this character towards the otherObject
			Param @otherObject: another Playable or Tower type object to move towards
			Returns: Nothing
		"""
		x_diff = otherObject.x_pos - self.x_pos
		y_diff = otherObject.y_pos - self.y_pos
		# Find the unit vector along the desired path
		x_diff /= self.distanceTo(otherObject)
		y_diff /= self.distanceTo(otherObject)
		# Find the scaled vector values to move
		x_diff *= self.move_amount_per_tick
		y_diff *= self.move_amount_per_tick
		
		self.x_pos += x_diff
		self.y_pos += y_diff

	def tick(self, opponentsArmy, opponentsTowers):
		# Find closest Enemy or tower
		assert(len(opponentsTowers) != 0)
		closestEnemy = None
		closestDistance = 1000000
		for enemy in opponentsArmy | opponentsTowers:
			distanceTo = self.distanceTo(enemy)
			if distanceTo < closestDistance:
				closestDistance = distanceTo
				closest = enemy
		if self.isInRangeOf(closestEnemy):
			self.attack(closestEnemy)
		else:
			self.moveTowards(closestEnemy)			

if __name__ == '__main__':
	p1 = Player()
	p2 = Player()
