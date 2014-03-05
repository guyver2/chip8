import numpy as np
import pygame
import sys
from random import randint
from threading import Lock
import time
# Definition of a chip 8 CPU

def hex4(nb):
	return "0x%04X"%nb


NAME = "CHIP 8 BASIC EMULATOR"
KEYMAP_FILE = ".chip8_keymap.txt"
MEM_SIZE   = 4096 # CPU RAM
MEM_OFFSET = 512  # memory offset, before that point we enter wonderland
BLACK = 0
WHITE = 1
S_WIDTH = 64 # virtual screen width in Pixels
S_HEIGHT = 32 # virtual screen height in Pixels
P_SIZE = 8 # Pixel size
W_WIDTH = S_WIDTH * P_SIZE # window width
W_HEIGHT = S_HEIGHT * P_SIZE # window height
FPS = 60 # screen frame rate (Hz)
CPUSPEED = 1000 # CPU freq (Hz) max seems to be 20kHz
INSPERFRAME = int(round(CPUSPEED/FPS)) # number of instruction per frame 
                                       # not perfect, but should do the trick

class Pixel(object):
	SPRITES = [pygame.Surface((P_SIZE, P_SIZE)), pygame.Surface((P_SIZE, P_SIZE))]
	SPRITES[0].fill((0,0,0)) #available colors and sprite
	SPRITES[1].fill((255,255,255))
	def __init__(self, x,y,v):
		super(Pixel, self).__init__()
		self.x = x
		self.y = y
		self.v = v


# CPU SIMULATOR
class CPU(object):
	def __init__(self, device):
		super(CPU, self).__init__()
		self.device = device
		self.reset()
		self.initInstructions()
		self.insSeen = []

	# reset CPU to default value
	def reset(self):
		self.memory      = np.zeros(MEM_SIZE, dtype=np.uint8) # RAM
		self.V           = np.zeros(16, dtype=np.uint8) # registers
		self.I           = 0 # single address register
		self.stack       = np.zeros(16, dtype=np.uint16)
		self.keys        = np.zeros(16, dtype=np.uint16)
		self.nbJump      = 0 
		self.timerDelay  = 0 # delay timer
		self.timerSound  = 0 # sound timer
		self.pc          = MEM_OFFSET # program counter
		self.matrix      = [[Pixel(i,j,BLACK) for j in xrange(S_HEIGHT)] for i in xrange(S_WIDTH)]

	def clearScreen(self):
		self.matrix      = [[Pixel(i,j,BLACK) for j in xrange(S_HEIGHT)] for i in xrange(S_WIDTH)]		

	def countDown(self):
		if self.timerDelay > 0 :
			self.timerDelay -= 1
		if self.timerSound > 0 :
			self.timerSound -= 1

	# load program ROM into memory
	def loadRom(self, filename):
		self.romData = np.fromfile(filename, dtype=np.uint8)
		self.romToMem()
		return True

	def romToMem(self):
		l = self.romData.shape[0]
		self.memory[MEM_OFFSET:MEM_OFFSET+l] = self.romData

	# process one instruction
	def step(self):
		oc = self.getOpcode()
		insID = self.getInstructionID(oc)
		X=(oc & 0x0F00) >> 8
		Y=(oc & 0x00F0) >> 4
		N=(oc & 0x000F)
		#print self.pc, hex4(oc), insID
		if insID not in self.insSeen : self.insSeen.append(insID)
		# if bad instruction ID back to the begining
		if insID == -1 :
			print "INSTRUCTION ERROR"
			sys.exit(1)
			self.reset() # reset CPU
			self.romToMem() # reload ROM
			return
		self.instructions[insID](X,Y,N)
		self.pc += 2 # jump to the next instruction (16 bit, hence +2)
		self.countDown()

	def getOpcode(self):
		return (self.memory[self.pc]<<8) + self.memory[self.pc+1]
	
	def getInstructionID(self, opcode):
		for i, ins in enumerate(self.mask):
			if opcode & ins[0] == ins[1] :
				return i
		return -1

	def initInstructions(self):
		self.mask = []
		self.mask.append([ 0x0000, 0x0FFF]) #  0NNN # 0
		self.mask.append([ 0xFFFF, 0x00E0]) #  00E0 
		self.mask.append([ 0xFFFF, 0x00EE]) #  00EE
		self.mask.append([ 0xF000, 0x1000]) #  1NNN
		self.mask.append([ 0xF000, 0x2000]) #  2NNN
		self.mask.append([ 0xF000, 0x3000]) #  3XNN # 5
		self.mask.append([ 0xF000, 0x4000]) #  4XNN
		self.mask.append([ 0xF00F, 0x5000]) #  5XY0
		self.mask.append([ 0xF000, 0x6000]) #  6XNN
		self.mask.append([ 0xF000, 0x7000]) #  7XNN
		self.mask.append([ 0xF00F, 0x8000]) #  8XY0 # 10
		self.mask.append([ 0xF00F, 0x8001]) #  8XY1
		self.mask.append([ 0xF00F, 0x8002]) #  8XY2
		self.mask.append([ 0xF00F, 0x8003]) #  BXY3
		self.mask.append([ 0xF00F, 0x8004]) #  8XY4
		self.mask.append([ 0xF00F, 0x8005]) #  8XY5 # 15
		self.mask.append([ 0xF00F, 0x8006]) #  8XY6
		self.mask.append([ 0xF00F, 0x8007]) #  8XY7
		self.mask.append([ 0xF00F, 0x800E]) #  8XYE
		self.mask.append([ 0xF00F, 0x9000]) #  9XY0
		self.mask.append([ 0xF000, 0xA000]) #  ANNN # 20
		self.mask.append([ 0xF000, 0xB000]) #  BNNN
		self.mask.append([ 0xF000, 0xC000]) #  CXNN
		self.mask.append([ 0xF000, 0xD000]) #  DXYN
		self.mask.append([ 0xF0FF, 0xE09E]) #  EX9E
		self.mask.append([ 0xF0FF, 0xE0A1]) #  EXA1 # 25
		self.mask.append([ 0xF0FF, 0xF007]) #  FX07
		self.mask.append([ 0xF0FF, 0xF00A]) #  FX0A
		self.mask.append([ 0xF0FF, 0xF015]) #  FX15
		self.mask.append([ 0xF0FF, 0xF018]) #  FX18
		self.mask.append([ 0xF0FF, 0xF01E]) #  FX1E # 30
		self.mask.append([ 0xF0FF, 0xF029]) #  FX29
		self.mask.append([ 0xF0FF, 0xF033]) #  FX33
		self.mask.append([ 0xF0FF, 0xF055]) #  FX55
		self.mask.append([ 0xF0FF, 0xF065]) #  FX65

		self.instructions = []
		for i in xrange(len(self.mask)):
			try :
				self.instructions.append(getattr(self, 'ins%d'%i))
			except :
				self.instructions.append(getattr(self, 'NOP'))
		for n, i in enumerate(self.instructions) : print n, i


	# default instruction, does nothing
	def NOP(self, X, Y, N):
		print "nop"
		pass


	# 0NNN : device specific
	def ins0(self, X, Y, N):
		pass

	# 00E0 : clear screen
	def ins1(self, X, Y, N):
		self.clearScreen()

	# 00EE : return from subroutine
	def ins2(self, X, Y, N):
		if self.nbJump < 1 :
			print "STACK UNDERFLOW"
			sys.exit(1)
		else :
			#print 'return ', self.stack, self.nbJump-1
			self.pc = self.stack[self.nbJump-1]
			self.nbJump -= 1

	# 1NNN : jump to address NNNN
	def ins3(self, X, Y, N):
		#print "   jump to address %d"%((X<<8)+(Y<<4)+N)
		self.pc = (X<<8)+(Y<<4)+N
		self.pc -= 2 # because of +2 at the end of the step

	# 2NNN : call subroutine at NNN
	def ins4(self, X, Y, N):
		if self.nbJump >= 15 :
			print "STACK OVERFLOW"
			sys.exit(1)
		else :
			self.stack[self.nbJump] = self.pc # save current address
			self.nbJump += 1
			self.pc = (X<<8)+(Y<<4)+N
			self.pc -= 2 # because of +2 at the end of the step

	# 3XNN : Skips the next instruction if VX equals NN.
	def ins5(self, X, Y, N):
		if self.V[X] == (Y<<4)+N :
			self.pc += 2

	# 4XNN : Skips the next instruction if VX doesn't equal NN.
	def ins6(self, X, Y, N):
		if self.V[X] != (Y<<4)+N :
			self.pc += 2

	# 5XY0 : Skips the next instruction if VX equals VY
	def ins7(self, X, Y, N):
		if self.V[X] == self.V[Y] :
			self.pc += 2

	# 6XNN : Sets VX to NN
	def ins8(self, X, Y, N):
		#print '  set V[%d] to %d'%(X, (Y<<4)+N)
		self.V[X] = (Y<<4)+N

	# 7XNN : Adds NN to VX
	def ins9(self, X, Y, N):
		#print '  add %d to V[%d]'%((Y<<4)+N, X)
		self.V[X] += (Y<<4)+N

	# 8XY0 : Sets VX to the value of VY
	def ins10(self, X, Y, N):
		#print '  set V[%d] to V[%d]'%(X, Y)
		self.V[X] = self.V[Y]

	# 8XY1 : Sets VX to VX or VY
	def ins11(self, X, Y, N):
		self.V[X] = self.V[X] | self.V[Y]

	# 8XY2 : Sets VX to VX and VY
	def ins12(self, X, Y, N):
		self.V[X] = self.V[X] & self.V[Y]

	# 8XY3 : Sets VX to VX xor VY
	def ins13(self, X, Y, N):
		self.V[X] = self.V[X] ^ self.V[Y]

	# 8XY4 : Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there isn't
	def ins14(self, X, Y, N):
		res = int(self.V[X]) + self.V[Y] # cast to catch carry
		if res > 255 : self.V[15] = 1
		else :         self.V[15] = 0
		self.V[X] = res%256

	# 8XY5 : VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there isn't
	def ins15(self, X, Y, N):
		res = int(self.V[X]) - self.V[Y] # cast to catch borrow
		if res < 0 : self.V[15] = 0
		else :       self.V[15] = 1
		self.V[X] = res%256

	# 8XY6 : Shifts VX right by one. VF is set to the value of the least significant bit of VX before the shift
	def ins16(self, X, Y, N):
		self.V[15] = self.V[X]&0x01
		self.V[X] = self.V[X]>>1

	# 8XY7 : Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there isn't
	def ins17(self, X, Y, N):
		res = int(self.V[Y]) - self.V[X] # cast to catch borrow
		if res < 0 : self.V[15] = 0
		else :       self.V[15] = 1
		self.V[X] = res%256

	# 8XYE : Shifts VX left by one. VF is set to the value of the most significant bit of VX before the shift.[
	def ins18(self, X, Y, N):
		self.V[15] = self.V[X]>>7
		self.V[X] = self.V[X]<<1

	# 9XY0 : Skips the next instruction if VX doesn't equal VY.
	def ins19(self, X, Y, N):
		if self.V[X] != self.V[Y] :
			self.pc += 2

	# ANNN : Sets I to the address NNN
	def ins20(self, X, Y, N):
		#print '   set I to address %d'%((X<<8)+(Y<<4)+N)
		self.I = (X<<8)+(Y<<4)+N

	# BNNN : Jumps to the address NNN plus V0
	def ins21(self, X, Y, N):
		self.pc = (X<<8)+(Y<<4)+N + self.V[0]
		self.pc -= 2 # because of +2 at the end of the step

	# CXNN : Sets VX to a random number modulo NN+1
	def ins22(self, X, Y, N):
		self.V[X] = randint(0, (Y<<4)+N)
		#print 'V['+str(X)+'] =', self.V[X]

	# DXYN : draw a sprite
	def ins23(self, X, Y, N):
		#print 'drawing', N, 'lines of 8 pix from', [self.V[X], self.V[Y]], ':', self.memory[self.I:self.I+N]
		self.V[15]=0 # no pixel filp so far
		for k in xrange(N):
			row=self.memory[self.I+k] # //get octet of the current line to draw
			y=(self.V[Y]+k)%S_HEIGHT # // get height of the affected pixels 
			off = 7
			for j in xrange(8) :
				#if row&(0x1<<(7-j)) == 0 : print 0,
				#else : print 1,
				x=(self.V[X]+j)%S_WIDTH # get x of affected pixel
				if (row&(0x1<<(7-j))) != 0 : # does the corresponding bit ask for a flip ?
					if self.matrix[x][y].v == WHITE : # pixel was white
						self.matrix[x][y].v = BLACK #
						self.V[15]=1 # pixel flip happend
					else:
						self.matrix[x][y].v=WHITE #;//on l'allume
			#print ''

	# EX9E : Skips the next instruction if the key stored in VX is pressed
	def ins24(self, X, Y, N):
		if self.keys[self.V[X]] == 1 :
			self.pc += 2

	# EXA1 : Skips the next instruction if the key stored in VX isn't pressed
	def ins25(self, X, Y, N):
		if self.keys[self.V[X]] == 0 :
			self.pc += 2

	# FX07 : Sets VX to the value of the delay timer.
	def ins26(self, X, Y, N):
		self.V[X] = self.timerDelay

	# FX0A : A key press is awaited, and then stored in VX
	def ins27(self, X, Y, N):
		self.V[X] = self.device.waitKey()

	# FX15 : Sets the delay timer to VX
	def ins28(self, X, Y, N):
		self.timerDelay = self.V[X]

	# FX18 : Sets the sound timer to VX
	def ins29(self, X, Y, N):
		self.timerSound = self.V[X]

	# FX1E : Adds VX to I, V15 set to 1 when overflow (I+VX > 0xFFF)
	def ins30(self, X, Y, N):
		res = int(self.I) + self.V[X]
		#print '   add V[%d] to I (%d %% %d = %d)'%(X, res, 0xFFF, res%0xFFF)
		if res > 0xFFF :
			self.V[15] = 1
		else :
			self.V[15] = 0
		self.I = res % 0xFFF

	# FX55 : Stores V0 to VX in memory starting at address I
	def ins33(self, X, Y, N):
		#print '   set %s to %s'%(',V'.join(range(X)), str(self.memory[self.I:self.I+X]))
		for i in xrange(X+1):
			self.memory[self.I+i] = self.V[i]

	# FX65 : Fills V0 to VX with values from memory starting at address I
	def ins34(self, X, Y, N):
		for i in xrange(X+1):
			self.V[i] = self.memory[self.I+i]





class Chip8(object):
	def __init__(self, cpu=None, romFileName=None):
		super(Chip8, self).__init__()
		self.cpu = cpu
		self.romFileName = romFileName
		self.screen = pygame.Surface((W_WIDTH,W_HEIGHT))
		self.clock = pygame.time.Clock()
		self.clock.tick()
		self.keymap = {} #keyboard to chip8 key mapping
		self.eventQueue = []
		self.eventMutex = Lock()
		self.loop = True
	
	def draw(self):
		for l in self.cpu.matrix:
			for p in l:
				self.screen.blit(Pixel.SPRITES[p.v], (p.x*P_SIZE, p.y*P_SIZE))

	def step(self):
		self.cpu.step()

	def process(self):
		self.step()
		dt = self.clock.tick_busy_loop(CPUSPEED) #needs accuracy
		# dt = self.clock.tick(CPUSPEED) #needs accuracy
		self.eventMutex.acquire()
		print 'cpu', dt
		self.eventMutex.release()

	def loadRom(self, filename):
		self.romFileName = filename
		if self.cpu :
			return self.cpu.loadRom(filename)
		else :
			return False

	# process event queue, THE MUTEX SHOULD BE LOCKED BEFOREHAND
	def processQueue(self):
		for e in self.eventQueue :
			k, v = e
			if k in self.keymap :
				self.cpu.keys[self.keymap[k]] = v
		self.eventQueue = []



	def waitKey(self):
		self.eventMutex.acquire()
		self.eventQueue = [] # make sure we get a NEW event
		self.eventMutex.release()
		while self.loop :
			self.eventMutex.acquire()
			if len(self.eventQueue) == 0 :
				self.eventMutex.release()
				time.sleep(0.1)
			else :
				res = None
				for e in self.eventQueue :
					k, v = e
					if k in self.keymap :
						if e[1] == 1 : # keyDown
							self.eventQueue = [] # cleanup
							self.eventMutex.release()
							return self.keymap[k]
				self.eventMutex.release()
		return 0 # doesn't matter, since if we reach this statement it means the main loop is over



		