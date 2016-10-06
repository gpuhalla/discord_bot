class item:
	
	def __init__(self, id):
		self.id = id
		self.level = 0
		self.exp = 0
		self.points = 0
		self.physicalDamage = 0
		self.fireDamage = 0
		self.iceDamage = 0
		self.shockDamage = 0
		self.primaryHand = 0
		self.secondaryHand = 0
		self.physicalArmor = 0
		self.fireArmor = 0
		self.iceArmor = 0
		self.shockArmor = 0
		self.body = 0
		self.pants = 0
		self.helmet = 0
		self.gloves = 0
		self.boots = 0
		self.getCharacter(id)
		
	def getCharacter(id = 0):
		if id = 0:
			
