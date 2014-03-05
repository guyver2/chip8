import numpy as np
import pygame
import sys
import os.path
import time
import threading
import chip8


# get keyboard to work 
def events():
	#print "checking event"
	keysD = []
	keysU = [] 
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			return (False, keysD, keysU)
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				return (False, keysD, keysU)
			keysD.append(event.key)
		elif event.type == pygame.KEYUP:
			keysU.append(event.key)
	return (True, keysD, keysU)


# load or create if none a keydict to map from keyboard to emulator keys
def loadKeyMap(filename):
	res = {}
	if os.path.isfile(filename) :
		fid = open(filename, 'r')
		for i in xrange(16):
			res[int(fid.readline())] = i
		fid.close()
	else :
		print "no keymap file, creating one..."
		tmp = []
		for i in xrange(16):
			k = -1
			while k == -1 :
				print "enter key to match with key", i
				while k == -1 :
					loop, keys, _ = events()
					if not loop :
						sys.exit(0)
					if keys != [] :
						k = keys[0]
						if k in tmp :
							print "key already taken, choose another one"
							k = -1
						else :
							tmp.append(k)
					time.sleep(0.1)

		fid = open(filename, 'w')
		for i in xrange(16):
			fid.write("%d\n"%tmp[i])
			res[tmp[i]] = i
		fid.close()
	return res
			
	
# thread that performs all the simulation. Has to be disconnected 
# from every rendering or event related functions
class ThreadChip(threading.Thread):
	def __init__(self, emu):
		super(ThreadChip, self).__init__()
		self.emu = emu
		self.loop = True

	def run(self):
		while self.loop :
			emu.process()
		




if __name__ == '__main__':
	if len(sys.argv) > 1 :
		romFile = sys.argv[1]
	else :
		romFile = 'c8games/MAZE'
	pygame.init()
	pygame.mixer.init()
	screen = pygame.display.set_mode((chip8.W_WIDTH,chip8.W_HEIGHT))
	pygame.display.set_caption(chip8.NAME+' : '+romFile)
	clock = pygame.time.Clock()
	clock.tick()

	# try loading keymap
	keymap = loadKeyMap(chip8.KEYMAP_FILE)

	emu = chip8.Chip8()
	cpu = chip8.CPU(emu)
	emu.cpu = cpu
	emu.loadRom(romFile)
	emu.keymap = keymap

	chip = ThreadChip(emu)
	chip.start()

	loop = True
	while loop :
		loop, keysD, keysU = events()
		emu.loop = loop
		emu.eventMutex.acquire()
		for k in keysD :
			emu.eventQueue.append([k,1])
		for k in keysU :
			emu.eventQueue.append([k,0])
		emu.processQueue()
		emu.eventMutex.release()
		#print "draw"
		emu.draw()
		screen.blit(emu.screen,(0,0))
		pygame.display.update()
		dt = clock.tick(chip8.FPS)
		emu.eventMutex.acquire()
		print 'render', dt
		emu.eventMutex.release()
		

	print sorted(emu.cpu.insSeen)

	# proper exit
	chip.loop = False
	chip.join()
	pygame.quit()
	sys.exit()
