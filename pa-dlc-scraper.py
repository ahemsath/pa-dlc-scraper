#!//anaconda/bin/python3

from bs4 import BeautifulSoup
import requests
import re
import plistlib
import eyed3

class DlcEpisode:
    def __init__(self, url, title, date):
        self.url = url
        self.title = self.closing_quote_to_apostrophe(title)
        self.date = date
        (month,day,year) = self.date.split('/')
        self.local_filename = "{}-{}-{} {}.mp3".format(year,month,day, self.title)

    def show(self):
        print("url = {}, title = {}, date = {}".format(self.url, self.title, self.date))

    def closing_quote_to_apostrophe(self, title):
        return title.replace("’","'")
    
    def download(self):
        # NOTE the stream=True parameter
        r = requests.get(self.url, stream=True)
        with open(self.local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    def set_tags(self):
        song = eyed3.load(self.local_filename)
        song.initTag()
        song.tag.artist = "Mike Krahulik and Jerry Holkins"
        song.tag.album = "Downloadable Content, The Penny Arcade Podcast"
        song.tag.save()

class DlcSeason:
    def __init__(self, season_url):
        self.episodes = []
        self.request = requests.get(season_url)
        if self.request.ok:
            self.soup = BeautifulSoup(self.request.content)
            ep_list = self.soup.find('ul', class_='episodeList')
            for list_item in ep_list.find_all('li'):
                a = list_item.find('a')
                ep_url = a.get("href")
                ep_title = a.get("title")
                h = a.find('h2')
                s = h.find('strong')
                ep_date = s.contents[0]
                self.episodes.append(DlcEpisode(ep_url, ep_title, ep_date))
        else:
            print("Error getting PADC Season Page ({}): {}".format(season_url, self.request.reason))

    def show(self):
        for e in self.episodes:
            e.show()

    def get_episodes(self):
        return self.episodes

class DlcHomepage:
    def __init__(self):
        self.seasons = []
        self.request = requests.get("http://penny-arcade.com/podcasts/show/dlc")
        if self.request.ok:
            self.soup = BeautifulSoup(self.request.content)
            for link in self.soup.find_all('a'):
                link_title = link.get("title")
                if link_title and re.match("Season\ \d", link_title):
                    self.seasons.append(DlcSeason(link.get('href')))
        else:
            print("Error getting PADLC homepage: {}".format(self.request.reason))
            exit()

    def show(self):
        for s in self.seasons:
            s.show()

    def get_episodes(self):
        full_ep_list = []
        for s in self.seasons:
            full_ep_list += s.get_episodes()
        return full_ep_list


class ItunesLibrary:
    def __init__(self, library_xml_file):
        self.library = plistlib.load(open(library_xml_file, 'rb'))
        self.track_names = []
        for track_id in self.library['Tracks']:
            self.track_names.append(self.library['Tracks'][track_id]['Name'])

    def show(self):
        for n in self.track_names:
            print(n)

    def search_by_name(self, name):
        for track_name in self.track_names:
            #print("searching for {} in {}".format(name, track_name))
            if re.search(re.escape(name), track_name):
                return True
        return False

h = DlcHomepage()

#h.show()

iTunes_library_file = "/Users/riceowlguy/Music/iTunes/iTunes Music Library.xml"
l = ItunesLibrary(iTunes_library_file)

#l.show()

for e in h.get_episodes():
    if l.search_by_name(e.title):
        pass
        #print("Found episode {} in library".format(e.title))
    else:
        print("Need to download", e.title)
        local_filename = e.download()
        print("Downloaded to", e.local_filename)
        #e.set_tags()



# @TODOs
# 1. add to iTunes

