import requests
import os
from bs4 import BeautifulSoup

#configuration
outputDir = "SomaFM"
source = "https://somafm.com/listen/"

#todo: die Config parameter in der Shell übergeben

#### Main
def main():
  stations = getStationsByFormat(source)
  print(str(len(stations['pls'])) + " *.pls Listen eingelesen")

  try:
    os.mkdir(outputDir)
  except OSError:
    print ("Creation of the directory %s failed" % outputDir)
  else:
    print ("Successfully created the directory %s " % outputDir)

  for station in stations['pls']:
    toFile(station, outputDir+'/somafm - '+station['name']+'.m3u')


'''
  getURLsByFormat

  @param: a url path of a page with links
  @return: a dict with name and url of a station
'''
def getStationsByFormat(source):
  PLS = []
  r = requests.get(source)
  soup = BeautifulSoup(r.text, 'html.parser')
  allLinks = soup.find_all('a')
  for link in allLinks:
    url = link.get('href')
    if ("130.pls" not in url):
      continue
    if ("nossl/" in url):
      continue
    name = link.parent.parent.parent.previous_sibling.previous_sibling.previous_sibling.previous_sibling.text
    PLS.append({"name": name, "url": "https://somafm.com" + url})
  return { 'pls' : PLS }

def scrapeUrl(line):
  start = line.find('<a href') +9
  end = line.find('"',start)
  return 'https://somafm.com'+line[start:end]

def toFile(station, filename):
  all = open(filename, 'w')
  all.write("#EXTM3U\n\n")
  all.write("#EXTINF:1,"+station['name']+"\n")
  all.write(station['url']+ "\n\n")
  all.close()
  print('write '+filename)

#start main function
main()
