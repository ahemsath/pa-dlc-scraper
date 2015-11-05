#!//anaconda/bin/python3

from bs4 import BeautifulSoup
import requests
import re
import plistlib

class DlcEpisode:
    def __init__(self, url, title, date):
        self.url = url
        self.title = title
        self.date = date

    def show(self):
        print("url = {}, title = {}, date = {}".format(self.url, self.title, self.date))

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
                ep_date = s.contents
                self.episodes.append(DlcEpisode(ep_url, ep_title, ep_date))
        else:
            print("Error getting PADC Season Page ({}): {}".format(season_url, self.request.reason))

    def show(self):
        for e in self.episodes:
            e.show()

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
        return name in self.track_names

h = DlcHomepage()

h.show()

iTunes_library_file = "/Users/riceowlguy/Music/iTunes/iTunes Music Library.xml"
l = ItunesLibrary(iTunes_library_file)

l.show()


# @TODOs
# 1. check to see if any episodes exist that I haven't already downloaded/imported
# 2. download new episodes and rename/edit mp3 tags

