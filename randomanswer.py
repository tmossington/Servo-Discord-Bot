from dictionary import jumbled_words
from datetime import datetime
import math

# Find UNIX timestamp
current_time = datetime.now()
UNIX_reference = 1645678800

# Function that picks a random word from the dictionary every day
def random_answer(daily: bool = True):
    if daily == True:
        UNIX = datetime.now().timestamp()
        iteration = int(math.floor((UNIX_reference - UNIX) / 86400))
        return jumbled_words[iteration]
        

