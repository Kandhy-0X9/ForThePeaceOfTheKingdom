# imports
import os
import sys
import time
import random

def clearTerminal():# Clear the terminal
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def typing(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.05)

# def slowtyping(text):
#     for char in text:
#         sys.stdout.write(char)
#         sys.stdout.flush()
#         time.sleep(.25)

def loadingAnimation(): # loading effect
    loadingtime = 5
    for i in range(loadingtime):
        clearTerminal()
        typing("_ _ _ _ _ ")
        clearTerminal()
        time.sleep(0.2)

taxes = None
money = None 
population = None 
knights = None 
maintenance = None 
reputation = None
importTax = None

class Alliance:
    def __init__(self, requirement, trustLVL, military):
        self.__requirement = requirement 
        self.__trustLVL = trustLVL
        self.__military = military 

loadingAnimation()
typing("\nThere once was a kingdom who was ruled by a fairly new, young boy who lacked experience with leadership.")
typing("\nAs this kingdom settled upon its new ruler, a kingdom nearby was falling apart and was falling into ruins.")
