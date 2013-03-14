from BeautifulSoup import BeautifulSoup
import urllib2
import sys
import os

base = "http://www.imdb.com/title/"
#dir_path = "best_music/" #change to each directory every time
#dir_path = "best_actress/"
#dir_path = "best_actor/"
#dir_path = "best_director/"
dir_path = "best_picture/"

movie_file = open(dir_path + "movies.txt", "rb")

lines = movie_file.readlines()
for line in lines:
	index = 0
	movie_id = line.split()[0]
	movie_url = base + movie_id + "/"
	os.mkdir(dir_path + movie_id)
	for i in range(0, 100, 10):
		url = movie_url + "reviews?start=" + str(i)
		page=urllib2.urlopen(url)
		soup = BeautifulSoup(page.read())
		tmp=soup.findAll('div',{'class':'yn'})
		for dt in tmp:
			file_name = str(index)+".txt"
			review = dt.findPreviousSibling('p').contents[0]
			out = open(dir_path + movie_id + "/" + file_name, 'wb')
			out.write(str(review))
			out.close()
			index = index + 1