# ENGLISH SPELLING TEST
#### Video Demo:  https://youtu.be/V1Ga1UStEJQ	
This is my final project for the [CS50 Introduction to Programming with Python course](https://cs50.harvard.edu/python/2022/)

## Options: 
**-h, --help** - show help message
**-f FILE, --file FILE** - path to the file containing words
   (default: './words/animals.txt')
**-n N** - number of words to be checked per one session
   (default: 10)
**-l {1,2,3}, --level {1,2,3}** - difficulty level; 
   levels differ in amount of hints (default: 1)
   
## Project file structure:
+ audio/
  - congratulations/
  - audio_getter.py
+ get_links.py
+ project.py
+ README.md
+ requirements.txt
+ test_get_links.py
+ test_project.py
+ words/
  - animals.txt
  - presentation.txt
  - test_words_file.txt
  - used/

## Description

English Spelling Test is an interactive command line tool for 
checking English spelling of a given amount of words with
nice feedback in ASCII texts and art pictures.

Program reads a **FILE** with words
randomly selects **N** words
from the file and checks the user's spelling for every of the selected words.

How the spelling is checked:
1) plays an audio with pronunciation of the word
2) checks user's input
3) gives a hint and one more try, if wrong spelling (according to the **LEVEL**)
4) expresses approval in a form of 
   - ASCII text (if wrong spelled)
   - ASCII art picture with printed and pronounced
     words of compliment (if correct spelling).
  
Finally an overall score and a results table are printed. 

> [!NOTE]
> ALSA or other corresponding audio drivers needed for correct work.

> [!NOTE]
> FFmpeg needed for correct work (probably other audio codecs may work, not tested).

### Words and used words
Every **FILE** with words has it's usage history:
a **FILE_USED** is created or updated
(for details see [Updating FILE_USED](#Updating-FILE-USED)).

When program started, function get_words(path_to_file) from [project.py](./project.py)
is used to create two lists: **words** and **used_words**, 
populated with the words found in **FILE** and **FILE_USED**
correspondingly. If no words are found in a file, an empty list is created.

Assuming each line in the files contains one word item.

### N random words selection
Function select_n_words(**words**, **used_words**, **N**) from [project.py](./project.py)
is used to select random **N** words from the **words** list 
excluding those words stored in **used_words** list.

##### select_n_words(words, used_words, N)

Firstly it is checked, that **N** is less or equals the amount of **words**,
otherwise **N** gets the value of the amount of **words**.
It is done in order to exclude repetitive checks of the same word
during one session.

A list **not_used_words** is created by excluding **used_words** from **words**
using the "set().difference" method.

Further on the following two variables are created and returned: 
a bool **exceeded** and a list **selected_words**.

In case when **N** equals or is less than amount of **not_used_words**,
variable **exceeded** gets value **False**,
the list **selected_words** is populated with a random sample of **N** words 
from **not_used_words** ("random.sample()" function is used).

In case when **N** is greater than the amount of **not_used_words**,
variable **exceeded** gets value **True**.
And as **N** - the number of words needed to be selected -
exceeds the amount of unused words, the list **selected_words** is 
populated by portions:
in the **first_portion** the shuffled **not_used_words** are stored,
in the **last_portion** the random sample of (**N** - len(**not_used_words**))
words selected from the **words** excluding the **first_portion** is stored.
(Function select_n_words() is used recursively here, because it does
exactly what is expected in this case).

### Getting wikimedia links (pronunciation)

To get a wikimedia link (http link to audio with pronunciation) for every word
in **selected_words**, class method GetLinks.get_links(selected_words) 
from [get_links.py](./get_links.py) is used.

##### Class GetLinks

A class to scrape and parse wiktionary.org in parallel threads
in order to get links to audio files with pronunciation 
of the given English words.

To get links to wikimedia resources for specific english words,
GetLinks utilizes the external library "wkt_scraper" (imported as "scraper"). 
To get links in parallel, GetLinks uses "threading" and 
"concurrent.futures" from the Python standard library.

GetLinks is not supposed to be instantiated anywhere, 
thus there is no `__init__` method.
GetLinks has attribute **thread_local** - an instance of the class 
"threading.local", which manages thread-local data of the executed threads.

Threads are started and links are accumulated in classmethod 
GetLinks.get_links(words), which utilizes
classmethod GetLinks.get_link(word) to get one link per word.

##### Classmethod GetLinks.get_link(word)

Method scrapes wiktionary.org to get a link to audio file 
with pronunciation of an English **word**. 

When called, method creates attribute "session" of **thread_local** - 
thread_local.session, and stores in it an instance of "scraper.Scraper()".

Method "scrape()" of "scraper.Scraper()" is used to receive the data
from wiktionary.org for the **word**. The data are stored as "response".

The "response" is parsed, looking for "value" with "type" 
'audio/wav', 'audio/ogg' or 'audio/mpeg' in "pronunciation" list.

The first found "value" (which is a **link** to wikimedia resources) 
is returned.

If link for the **word** not found (i.e. wiktionary.org responses 404 or alike,
'pronunciation' list is empty or does not contain corresponding values),
**FileNotFoundError** is raised.

##### Classmethod GetLinks.get_links(words)

This class method executes in parallel GetLinks.get_link() 
for every word in **words**, and accumulates results.
Method returns **words_links** dictionary with found links as values 
and corresponding words as keys,
and **notfound_words** list of words, for which links were not found.

ThreadPoolExecutor is created.
The execution of GetLinks.get_link() for every word of **words** is scheduled
(ThreadPoolExecutor.submit() is used for that).
In dictionary **future_to_url**	are stored:
- "Future" objects (representing the execution) as keys,
- corresponding words as values.
The results in **future_to_url** are yielded as executions complete.

Dictionary **words_links** is populated with:
- corresponding words as keys,
- results (links) as values.

If result for a word is a FileNotFoundError, word is appended
to the **notfound_words**.

The following articles were helpful:
[python-concurrency](https://realpython.com/python-concurrency/)
[ThreadPoolExecutor Example](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor-example)

### Checking spelling of a word
To check spelling of a word, the function 
is_spelling_correct(word, link, level, fglt) from [project.py](./project.py) is used.

##### is_spelling_correct(word, link, LEVEL, fglt)
Argument **fglt** is an instance of pyfiglet.Figlet(),
see [pyfiglet](https://pypi.org/project/pyfiglet/).
**fglt** is created once in the main() and is used in several places
all over the program.

Preparation:
- load pronunciation audio, save it as **word_sound**
  (pyglet.media.load(**link**, streaming=False) is used fo this,
  **word_sound** is a "Source" object of pyglet, which provides a "play()" method),
- calculate **attempts_amount** considering **LEVEL**
  (if length of **word** is 1, **attempts_amount** is 1,
  otherwise **attempts_amount** is length of **word** divided by **LEVEL**),
- set the first **attempt** to 1. 

Execution and logic:
1) while going through **attempts_amount**,
2) play **word_sound** (utilize "play()" method of the object),
3) ask user to input the pronounced word,
4) if correct spelling inputted, congratulate(), return **True**
   (see [congratulate()](#congratulate()) below),
5) if not correct spelling and not the first attempt, 
   give_hint(**word**, **attempt** - 1) for the **word**
   (see [give_hint(word, i)](#give-hint(word,-i)) below),
6) if **attempts_amount** reached, but no correct spelling inputted,
   print the correct spelling, 
   play **word_sound**,
   get_correct_input() for the **word**
   (get_correct_input() is a function, which in a loop stubbornly
   asks user to input the word correctly),
   print approval nicely using **fglt**,
   return **False**.

##### congratulate()
This function from [project.py](./project.py) does:
- select random **congrat** - a "congratulation" word from the hardcoded list
  (examples: 'excellent', 'brilliant' etc.)
- select a random **character** for "cowsay"
- if audio file with the name **congrat** exists in "./audio/congratulations/",
  load audio as **congrat_audio** (pyglet.media.load(path, streaming=False)), 
  and play **congrat_audio**
- print **congrat** using "cowsay.**character**()".

To put the value of variable **character** as name of "cowsay" method,
Python function "eval" from builtins is used. 

About getting audio for congratulations see [audio_getter.py](#audio-getter.py).

##### give_hint(word, i)
This function from [project.py](./project.py) 
returns a hint for a **word** - a string containing 
**i** letters of the word beginning with the first one,
and the stars "*" as placeholders for the remaining letters.

Examples:
```
>>> give_hint("owl", 1)
"o**"
>>> give_hint("tomato", 3)
"tom***"
>>> give_hint("a cat", 2)
"a ***"
```

### Running spelling test
To get a list of **correctly_spelled_words**,
executor(words_links, level, fglt) from [project.py](./project.py) is used.

##### executor(words_links, LEVEL, fglt)
This function executes is_spelling_correct() for every 
(word, link) pair from **words_links** dictionary,
and returns a list of **correctly_spelled_words**.

For every word in **words_links**:
- clear_screen() 
  (a simple function, which clears console screen platform independently)
- print welcome note nicely using **fglt**
- print words count (example: "Word: 2 of 10")
- if is_spelling_correct(**word**, link, **LEVEL**, fglt) return **True**,
  append **word** to the **correctly_spelled_words**
- ask user to press "Enter" to continue.

### Updating FILE_USED
After spelling of words checked and the **correctly_spelled_words** collected,
usage history of the **FILE** i.e. **FILE_USED** is updated using
update_used_words(correctly_spelled_words, FILE_USED, exceeded)
from [project.py](./project.py).
**FILE_USED** is a path created in main() according to the pattern:
"./words/used/_used_{basename of **FILE**}".

##### update_used_words(correctly_spelled_words, used_words_path, exceeded)
This function updates a file by **used_words_path** 
with the given **correctly_spelled_words**,
rewrites file if **exceeded** is True, 
appends to the file if **exceeded** is False.

### Printing results
These steps are part of main() in [project.py](./project.py):
- clear_screen()
- print score (example: 9/10)
- print the table of checked words with results "OK" or "Failed"
- if **notfound_words** present, print them.

## Audio congratulations (audio_getter.py)
audio_getter.py can be executed separately for downloading audio
for the hardcoded list of congratulations ('excellent', 'great job' etc.).
Class GetLinks is utilized for getting links from wiktionary.org.
Python standard library "requests" is used to download audio files.
Files are saved without extension as "./congratulations/{congratulation}".

## External Python libraries used:
[wkt_scraper](https://pypi.org/project/wkt-scraper/)
[pyfiglet](https://pypi.org/project/pyfiglet/)
[cowsay](https://pypi.org/project/cowsay/)
[pyglet](https://pypi.org/project/pyglet/)
[tabulate](https://pypi.org/project/tabulate/)

## Resources used when running English Spelling Test:
[Wiktionary](https://en.wiktionary.org/wiki/Wiktionary:Main_Page)
[Wikimedia Commons](https://commons.wikimedia.org/wiki/Main_Page)
