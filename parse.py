#!/usr/bin/env python

from BeautifulSoup import BeautifulSoup
import urllib2
from urllib2 import urlparse
import re

FILE_TO_PARSE = "file:///home/n0ha/Desktop/dt.html"
BASE_URL = "http://iportalt2.eurotel.sk:9092/"

#FILE_TO_PARSE = "http://www.sme.sk/"
#BASE_URL = ""

PATTERN = re.compile('function \$');
DEBUG = False

# BASE_URL should be set
if not BASE_URL:
  BASE_URL = FILE_TO_PARSE

page = urllib2.urlopen(FILE_TO_PARSE)
soup = BeautifulSoup(page)

# holds all JS with reference to what file it is from
js_contents = {}

# holds all occurences of search string
found = {}

# counter for in-file scripts
in_file_scripts = 0

# grab all the scripts from the page
for script in soup.findAll("script"):

  # if there is a src attribute, download the script
  if 'src' in script._getAttrMap():
    
    # first, check if the url is absolute
    if urlparse.urlsplit(script['src']).netloc == '':
      js_url = BASE_URL + script['src']
    else:
      js_url = script['src']
    
    if DEBUG:
      print "Downloading included script from %s" % js_url
    js = urllib2.urlopen(js_url)
    js_contents[js_url] = js.readlines()
  else:
    
    # just get the contents of the in-file script
    index = "in_file_%s" % in_file_scripts
    if DEBUG:
      print "Indexing in-file script %s" % index
    
    js_contents[index] = script.contents
    
    # raise the index for future generations :)
    in_file_scripts = in_file_scripts + 1

# search all JS content
for source, content in js_contents.items():
  line_no = 1
  for line in content:
    for match in PATTERN.finditer(line):
      if source not in found:
        found[source] = {}
      found[source][line_no] = (line, match)
      line_no = line_no + 1
  
# print the results
if len(found) == 0:
  print "Searched %s scripts, no matches found" % len(js_contents)

for source, occurences in found.items():
  print "Found %s occurences in %s" % (len(occurences), source)
  for line_no, (line, match) in occurences.items():
    print " - [%s:%s] %s" % (line_no, match.start(), line.replace("\n", ""))


