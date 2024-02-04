#import re
import requests
import os
import sys
from time import sleep

# getting name of the current directory
current_dir = os.path.dirname(os.path.realpath(__file__))
#getting name of the parent directory
parent_dir = os.path.dirname(current_dir)
# adding parent directory to the sys.path
sys.path.append(parent_dir)

from get_links import GetLinks


def downloader(links: dict, directory):
	if not os.path.isdir(directory):
		os.mkdir(directory)
	for word, link in links.items():
		# Getting the extension of the downloaded file
		#match = re.match(r"^http.*/([^/]+)$", link)
		#web_name = match.groups()[0]
		#_, ext = os.path.splitext(web_name)
		file_name = f"./{directory}/{word}" # add {ext}, if extension needed
		headers = {"User-Agent": "EnglishSpellingTest/0.1 (Educational project) audio_getter/0.1"}
		r = requests.get(link, headers=headers, allow_redirects=True, stream=True)
		with open(file_name, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024):
				if chunk:
					f.write(chunk)
		r.close()
		sleep(1) # to not overload wikimedia
		print(f"HTTP: {r.status_code} || '{word}' saved to: {file_name}")


def main():
	congrats = ["great", "nice", "brilliant", "magnificent",
		"excellent", "amazing", "cool", "well done",
		"great job", "awesome", "wonderful", "fantastic",
	       	"terrific", "marvellous", "gorgeous", "splendid",
		"fabulous", "glorious", "impressive", "sublime",
		"clever", "clever", "smart", "fine", "wow", 
		"perfect", "accurate", "superb"]

	links, notfound_words = GetLinks.get_links(congrats)
	downloader(links, "congratulations")
        
        
if __name__ == "__main__":
	main()
	
