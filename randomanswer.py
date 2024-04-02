from dictionary import words
from datetime import datetime
import math
import random

# Find UNIX timestamp
current_time = datetime.now()
UNIX_reference = 1645678800

# Function that picks a random word from the dictionary every day
def daily_random_word(daily: bool = True):
    if daily == True:
        UNIX = datetime.now().timestamp()
        iteration = int(math.floor((UNIX_reference - UNIX) / 86400))
        daily_answer = words[iteration]
        return daily_answer
    
def random_word():
    answer = words[random.randint(0, len(words))]
    return answer
        

