''' Created by Jeremy Reynolds for UALR COSMOS Team
	Uses BeautifulSoup to parse webpages and get
	language attribute from <html> tag if present.
	Also uses TextBlob to detect page language.

	Expects .csv with hostnames in first column.
	Outputs .csv with columns:
		header_lang, TextBlob_lang, guess1_lang, guess2_lang, error_T/F, site
	'guess1_lang' uses 'header_lang' if exists, else 'TextBlob_lang'.
	'guess2_lang' uses 'TextBlob_lang' if exists, else 'header_lang'.
'''

from bs4 import BeautifulSoup
from textblob import TextBlob
from urllib.request import urlopen, Request
import urllib.request, http.client, time, csv, os

inputFile = 'sitelist.csv'			# CSV input file that contains hostname list
outputFile = 'output.csv'			# CSV output file
hostnames = []						# Array to store hostnames from 'inputFile'
counter = 0

file = open(inputFile)				# Opens 'inputFile' and appends entries to hostname[] array
reader = csv.reader(file)
for item in reader:
	hostnames.append(item[0])
file.close()

if not os.path.exists(outputFile):	# Creates outputFile if it does not exist and writes column headers
	with open(outputFile, 'a', newline='') as file:
		writer = csv.writer(file)
		writer.writerow(['header_lang','TextBlob_lang','guess1_lang','guess2_lang','error_T/F','site'])

for site in hostnames:				# Loops through hostnames, detects language and updates outputFile.csv
	start_time = time.time()
	error = False
	counter += 1

	if not site[0:4] == 'http':		# Appends 'http://' if not present on hostname
		site = 'http://' + site

	try:							# Tries to open site and reads page with BeautifulSoup
		page = urlopen(Request(site, headers={'User-Agent': 'Mozilla/5.0'}))
		soup = BeautifulSoup(page.read(), 'lxml')
	except (urllib.error.URLError, urllib.error.HTTPError, http.client.HTTPException) as err:
		print('ERROR: ', err)
		error = True				# If error, print 'err' and set 'error' to True

	try:							# Tries to find body and paragraph tags
		body = soup.find('body').findAll(['div','p'])
	except AttributeError as err:
		if not error:				# If 'error' is False, print 'err' and set 'error' to True
			print('ERROR: ', err)	# Will prevent printing both errors if not necessary
		error = True

	headerLang = 'null'				# Sets 'headerLang' to null and finds <html> tag attributes
	htmlTag = [tag.attrs for tag in soup.findAll('html') if tag]
	if htmlTag:						# Exctracts language attribute if present
		for item in htmlTag[0].items():
			if item[0] == 'lang' and not error:
				headerLang = item[1]

	langList = []
	for item in body:				# Strips tags and extra spacing from BeautifulSoup body
		item = ''.join(item.findAll(text=True)).strip()
		if len(item) > 2:			# Uses TextBlob to detect language for each word in BeautifulSoup body
			langList.append(TextBlob(item).detect_language())
	if langList and not error:		# Finds most common detected language
		mostCommonLang = max(set(langList), key=langList.count)
	else:
		mostCommonLang = 'null'

	if headerLang != 'null':		# Uses language from headerLang unless null, then use TextBlob language
		guess1_lang = headerLang
	else:
		guess1_lang = mostCommonLang
		
	if mostCommonLang != 'null':	# Uses language from TextBlob unless null, then use headerLang language
		guess2_lang = mostCommonLang
	else:
		guess2_lang = headerLang

	if not error and headerLang == 'null' and mostCommonLang == 'null':
		print('ERROR:  <html lang> and <body> tags are empty')
		error = 'True'				# Indicates no header language and nothing for TextBlob to parse

	print(counter, str(round(time.time()-start_time))+'s', 'header:', headerLang.ljust(5), 'blob:', mostCommonLang.ljust(5), site)
	with open(outputFile, 'a', newline='') as file:
		writer = csv.writer(file)	# Appends data to new row in 'outputFile.csv'
		writer.writerow([headerLang, mostCommonLang, guess1_lang, guess2_lang, error, site])
