#!/usr/bin/env python3

import random
import argparse
import re
import os
from pyfiglet import Figlet
import cowsay
import pyglet
from time import sleep
from tabulate import tabulate

from get_links import GetLinks


def clear_screen():
    if os.name == 'nt':
        os.system('cls') 
    else:
        os.system('clear')


def get_words(path_to_file):
    """
    Read the 'file' and return a list of words.
    Assume each line in the 'file' contains one word item.
    """
    words = []
    if os.path.isfile(path_to_file):
        with open(path_to_file) as f:
            for line in f:
                words.append(line.strip())
    return words


def select_n_words(words: list, used_words: list, n: int):
    """
    Get a random sample of 'n' words from 'words' excluding 'used_words'. 
    If not used words left in 'words' less than 'n', 
    additionally select from 'words' ignoring already selected words.
    Return: 
    - list of 'n' randomly selected words, without repetitions
    - True, if 'words' list finished (not used words < 'n'),
      False otherwise.
    """
    # Amount of words to be selected n <= len(words), 
    # otherwise n = len(words)
    n = n if n <= len(words) else len(words)
    
    not_used_words = list(set(words).difference(set(used_words)))
    not_used_amount = len(not_used_words)
    
    if not_used_amount >= n:
        exceeded = False
        selected_words = random.sample(not_used_words, n)
    else:
        exceeded = True
        first_portion: list = random.sample(not_used_words, not_used_amount)
        last_portion, _ = select_n_words(words, first_portion, n - not_used_amount)
        selected_words = first_portion + last_portion
    return selected_words, exceeded
        

def get_correct_input(word):
    """
    Make user input the given 'word'
    correctly.
    """
    while True:
        attempt = input("Spell: ")
        if attempt.strip() == word:
            return


def congratulate():
    """
    Print a 'congratulation', chosen randomly from the 
    hardcoded list using random cowsay charachter.
    Play audio file from "audio/congratulations/"
    with the name {congratulation}.
    """
    congrats = [
        "great", "nice", "brilliant", "magnificent",
        "excellent", "amazing", "cool", "well done",
        "great job", "awesome", "wonderful", "fantastic",
        "terrific", "marvellous", "gorgeous", "splendid",
        "fabulous", "glorious", "impressive", "sublime",
        "clever", "smart", "fine", "wow", "perfect",
        "accurate", "superb"]
    
    congrat = random.choice(congrats)
    character = random.choice(cowsay.char_names)
    audio_file = f"audio/congratulations/{congrat}"
    
    if os.path.isfile(audio_file):
        congrat_sound = pyglet.media.load(audio_file, streaming=False)
        congrat_sound.play()
        
    eval(f"cowsay.{character}('{congrat.capitalize()}!')")


def give_hint(word: str, i: int) -> str:
    """
    Return a hint for a **word** - a string containing 
    **n** letters of the word beginning with the first one,
    and the stars "*" as placeholders for the remaining letters.
    
    >>> give_hint("owl", 1)
    "o**"
    >>> give_hint("tomato", 3)
    "tom***"
    >>> give_hint("a cat", 2)
    "a ***"
    """
    if i < 0:
        err = f"i should be integer >= 0, but '{i}' is given"
        raise ValueError(err)
    hint = word[:i] + re.sub(r"\S", "*", word[i:])
    return hint


def is_spelling_correct(word: str, link: str, level: int, fglt: Figlet) -> bool:
    """
    Check spelling of 'word' interactively:
    1) play pronunciation using 'link',
    2) ask user to input the pronounced 'word',
    3) if correct spelling inputed, congratulate(), return True
    4) if not correct spelling and not the first attempt, 
       give_hint() for the 'word' and according to the 'level',
    5) if 'attempts_amount' reached, but no correct spelling inputed,
       print the correct spelling, play pronunciation,  
       get_correct_input() for the 'word', return False.
    """
    word_sound = pyglet.media.load(link, streaming=False)
    # Attempts amount calculated using 'level'
    attempts_amount = len(word) // level if len(word) > 1 else 1
    attempt = 1
    while attempt <= attempts_amount:
        print("=" * 80)
        word_sound.play()
        if attempt > 1: # first attempt without any hints
            i = attempt - 1 # the first attempt not counted
            print("Hint:", give_hint(word, i))
        user_input = input("Spell: ")
        if user_input.strip() == word:
            congratulate()
            return True
        attempt += 1
    else:
        # After all attempts used and no correct spelling entered:
        print("=" * 80)
        print("Correct spelling:", word)
        word_sound.play()
        get_correct_input(word)
        print(fglt.renderText("Nice work!"))
        return False


def executor(words_links: dict, level: int, fglt: Figlet) -> list:
    """
    Execute is_spelling_correct() for every 
    (word, link) pair from 'words_links' dictionary.
    Return list of correctly spelled words.
    """
    words_number = len(words_links)
    correctly_spelled_words = []
    for i, word in enumerate(words_links, start=1):
        clear_screen()
        print(fglt.renderText("Welcome  to  the  spelling  test!"))
        print(f"Word: {i} of {words_number}")
        if is_spelling_correct(word, words_links[word], level, fglt):
            correctly_spelled_words.append(word)
        # Ask user to press Enter to continue
        input("\n\n\nPress Enter to continue...")
    return correctly_spelled_words


def update_used_words(correctly_spelled_words, used_words_path, exceeded: bool):
    """Update a file by 'used_words_path' 
    with the given 'correctly_spelled_words'.
    Rrewrite file if 'exceeded' == True, 
    append to the file if 'exceeded' == False.
    """
    mode = 'w' if exceeded else 'a'
    
    # check if directory for used words exists, 
    # create it if does not exist
    used_dir = os.path.dirname(used_words_path)
    if not os.path.isdir(used_dir):
        os.mkdir(used_dir)
    
    with open(used_words_path, mode) as f:
        for word in correctly_spelled_words:
            f.write(f"{word}\n")


def create_table(words_links, correctly_spelled_words):
    """Create a table of words with the "OK" for word, if
    correctly spelled, and "Failed" otherwise.
    """
    table = []
    for word in words_links:
        if word in correctly_spelled_words:
            table.append([word, "OK"])
        else:
            table.append([word, "Failed"])
    return table


def main():
    parser = argparse.ArgumentParser(description="English spelling test")
    parser.add_argument("-f", "--file", default="words/animals.txt", 
                        help="path to the file with words (default: './words/animals.txt')")
    parser.add_argument("-n", default=10, type=int,
                        help="number of words to be checked per one session (default: 10)")
    parser.add_argument("-l", "--level", default=1, choices=[1, 2, 3], type=int,
                        help="difficulty level; levels differ in amount of hints (default: 1)")
    args = parser.parse_args()
    
    level = args.level
    words_path, number = args.file, args.n
    used_words_path = f"./words/used/_used_{os.path.basename(words_path)}"
    
    clear_screen()
    fglt = Figlet()
    print(fglt.renderText("Welcome  to  the  spelling  test!"))
    words: list = get_words(words_path)
    used_words: list = get_words(used_words_path)
    selected_words, exceeded = select_n_words(words, used_words, number)
    words_links, notfound_words = GetLinks.get_links(selected_words)
    correctly_spelled_words = executor(words_links, level, fglt)
    score = len(correctly_spelled_words)
    # A word is counted as 'used' if it was spelled correctly (scored).
    update_used_words(correctly_spelled_words, used_words_path, exceeded)
    
    table = create_table(words_links.keys(), correctly_spelled_words)
    
    clear_screen()
    print(fglt.renderText(f"Your  score:  {score} / {len(words_links)}"))
    print(tabulate(table, tablefmt="grid", colalign=("left","center")))
    if notfound_words:
        print(f"Not found {len(notfound_words)} words:", notfound_words)


if __name__ == "__main__":
    main()
