
     ___    _                     _       ___                      _           _                
    (  _`\ ( )     _            /'_`\    (  _`\                   (_ )        ( )_              
    | ( (_)| |__  (_) _ _      ( (_) )   | (_(_)  ___ ___   _   _  | |    _ _ | ,_)   _    _ __ 
    | |  _ |  _ `\| |( '_`\     > _ <'   |  _)_ /' _ ` _ `\( ) ( ) | |  /'_` )| |   /'_`\ ( '__) 
    | (_( )| | | || || (_) )   ( (_) )   | (_( )| ( ) ( ) || (_) | | | ( (_| || |_ ( (_) )| |   
    (____/'(_) (_)(_)| ,__/'   `\___/'   (____/'(_) (_) (_)`\___/'(___)`\__,_)`\__)`\___/'(_)   
                     | |                                                                        
                     (_)                                                                        
                                                                                            
                                                                                           


# Abstract :  

- Quick launch :  
	`python main.py`  
- Download :  
	`git clone https://github.com/guyver2/chip8.git`  



# Introduction :  

This is a small project I was very interested to try for a long time without actually dare to give it a shot. It seemed to me that writing an emulator would require deep knowledge in optimisation and other low-level programming skills. Turns out I might have them because it all went quite fine. I started this project by following a [tutorial ](http://fr.openclassrooms.com/informatique/cours/l-emulation-console) but ended up doing most of the code by myself, in python, using pygame for the rendering part.  



# Installation :   


- Requirements :  
	* python 2.7 (or more I guess...)
	* pygame 1.9.2
	* the emulator itself
	`git clone https://github.com/guyver2/chip8.git`

- Opening a ROM :  
	You may specify which ROM you want to play within the emulator using the following command :  
	`python main.py [path to the ROM]`  
	The root folder contains multiple ROMs under free licence found on the web.  
	All files ending in .ch8 are valid and tested ROM files.  

- Keyboard configuration :  
	The first time you'll launch the emulator it will ask you to map your computer	keyboard to the Chip8 16 keys-keyboard. Keys are numerated from 0 to 9 and then from A to F. Usually keys 2-4-6-8 are mapped to up-left-right-down and 5 is the	_action_ button. Just press the buttons as asked in the terminal.  
	If you're not satisfied with your mapping you can remove the `.chip8_keymap.txt` previously created and the emulator will ask you to re-do the mapping process.



# Credits & Licence :  

- Code :   
	Antoine Letouzey -- [antoine.letouzey@gmail.com](antoine.letouzey@gmail.com)
- Licence :   
	WTFPL



# Links :

- Step by step [tutorial](http://fr.openclassrooms.com/informatique/cours/l-emulation-console)
- Complete documentation : [http://mattmik.com/chip8.html](http://mattmik.com/chip8.html)


# Screenshots :  
![im1](http://sxbn.org/~antoine/git/chip8/screenshots/chip8_00.jpg)
![im2](http://sxbn.org/~antoine/git/chip8/screenshots/chip8_01.jpg)
![im3](http://sxbn.org/~antoine/git/chip8/screenshots/chip8_02.jpg)
![im4](http://sxbn.org/~antoine/git/chip8/screenshots/chip8_03.jpg)
![im5](http://sxbn.org/~antoine/git/chip8/screenshots/chip8_04.jpg)
![im6](http://sxbn.org/~antoine/git/chip8/screenshots/chip8_05.jpg)
![im7](http://sxbn.org/~antoine/git/chip8/screenshots/chip8_06.jpg)
![im8](http://sxbn.org/~antoine/git/chip8/screenshots/chip8_07.jpg)
![im9](http://sxbn.org/~antoine/git/chip8/screenshots/chip8_08.jpg)
![im10](http://sxbn.org/~antoine/git/chip8/screenshots/chip8_09.jpg)
