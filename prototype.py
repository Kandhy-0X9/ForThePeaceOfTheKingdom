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
name = None

class Alliance:# Alliances class
    def __init__(self, requirement, trustLVL, military):
        self.__requirement = requirement 
        self.__trustLVL = trustLVL
        self.__military = military 

loadingAnimation()
typing(f"What will you be known as (King... or Queen...)\n")
name = input("Name: ")
loadingAnimation()
typing("--INTRO--")
typing(f"\nThere once was a kingdom who was ruled by a fairly new ruler, {name}, who lacked experience with leadership.")
typing(f"\nAs this kingdom settled upon its new ruler, a kingdom nearby was falling apart and was falling into ruins.")
