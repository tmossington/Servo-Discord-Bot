## Main Wordle file for game
import dictionary
import randomanswer

class Wordle:
    # Main class for the Wordle game, takes arguments and checks against dictionary.
    def __init__(self, word: str = 'hello', enforce_length: bool = True, real_word: bool = True, random_daily: bool = False):
        # Add better description here
        self.word = word.upper()
        self.enforce_length = enforce_length
        self.real_word = real_word
        if random_daily:
            self.word = randomanswer.daily_random_word(daily=True).upper()

        # Track number of guesses
        self.guesses = []

        # make sure guessed word is not a number or special character
        # keep track of the number of guesses
        # make sure there is only 1 word in the guess

    def game(self):
#
        # Make sure the word is 5 characters long and is in the dictionary
        if self.enforce_length and len(self.word) != 5:
            raise ValueError("Word must be 5 characters long.")
        if self.real_word == True and self.word.lower() not in dictionary:
            raise ValueError("word must be present in the dictionary.")
        
        # Being iterating through the game
        for i in range(6): # user gets 6 attempts
            # initialize variable for duplicate guess
            self.word_duplicate = list(self.word)

            # initialize failed_dctionary_test
            # Add later if needed

            # User attempt
            guess = str(input(f"Attempt {i+1}: ")).upper()

            #real_word = TRUE
            if self.real_word == True:
                if guess.lower() not in dictionary.words:
                    failed_dict_test = True
            
            # Failure checking block
            if failed_dict_test == True:
                print("Word is not in the dictionary, please try again.")
            elif " " in guess:
                print("You have multiple words in your guess, please try again.")
            elif len(guess) > len(self.word):
                print("Your guess has too many letters, please try again with a 5 letter word.")
            
            # Prepare response list
            response = []
            for i in range(len(guess)):
                response.append('')
            
            # Check for correct letters in correct position
            for j in range(len(guess)):
                if guess[j] in self.word_duplicate and guess[j] == self.word[j]:
                    response[j] = f"__{guess[j]}__    "
                    self.word_duplicate.remove(guess[j]) # remove the letter from the list

            # next present and absent check for letters in the word, but not the right position
            for j in range(len(guess)):
                # Skip already completed letters
                if response[j] != '':
                    continue
                if guess[j] in self.word_duplicate:
                    response[j] = guess[j] + "    "
                    self.word_duplicate.remove(guess[j])
                # other absent:
                else:
                    response[j] = guess[j].lower() + "    "

            responseString = ""
            for letter in response:
                responseString += letter
            print(responseString)

            if guess == self.word:
                print(f"Congratulations! You have guessed the word in {i+1} attempts.")
        print(f"Sorry, you have run out of attempts. The word was {self.word}.")
        quit()
    

              
            

    def send_guess(self, guess: str, log_guess: bool = True):
    # 
        # send individual guesses to the game and return a tuple where item 1 is the string response, and item 2 is a boolean if the guess was correct

        # For duplicate guess verification
        self.word_duplicate = list(self.word)
        guess = guess.upper()
        failed_dict_test = False
        # cheating checks

        # real_word = true
        if self.real_word == True and guess.lower() not in dictionary.words:
            failed_dict_test = True
        
        if " " in guess:
            return "You have multiple words in your guess, please try again."
        elif self.enforce_length and len(guess) > len(self.word):
            return "Your guess has too many letters, it can't be more than {len(list(self.word))} letters long."
        elif len(guess) < len(self.word):
             return "Your guess has too few letters, it must be {len(list(self.word))} letters long."
        elif failed_dict_test == True:
            return "Word is not in the dictionary, please try again."
            
        # Correct failed dictionary test if real world is guessed
        elif self.real_word and guess.lower() in dictionary.words:
            failed_dict_test = False

        # Prepare response list
        response= ['' for i in range(len(guess))]

        # Check for correct letters in correct position
        for j in range(len(guess)):
            try:
                if guess[j] == self.word[j]:
                    response[j] = f"__{guess[j]}__    "
                    self.word_duplicate.remove(guess[j])
                    continue
            except IndexError:
                pass

        # next present and absent check for letters in the word, but not the right position
        for j in range(len(guess)):
            # Skip already completed letters
            if response[j] != '':
                continue
            # if present
            if guess[j] in self.word_duplicate:
                response[j] = guess[j] + "    "
                self.word_duplicate.remove(guess[j])
            # other absent:
            else:
                response[j] = guess[j].lower() + "    "


        responseString = ""
        for letter in response:
            responseString += letter

        if guess == self.word:
            guessed_correctly = True
        else:  
            guessed_correctly = False   

        # Log the guess
        if log_guess:
            if len(self.guesses) < 6:
                self.guesses.append(guess)
            else:
                return "You have run out of guesses, the word was {self.word}."

        # Return the response

        if guessed_correctly:
            return responseString, True
        else:    
            return responseString, False

    # Reset guesses
        def reset(self):
            self.guesses = []   


    # Game over
    def is_over(self):
        return len(self.guesses) >= 6
