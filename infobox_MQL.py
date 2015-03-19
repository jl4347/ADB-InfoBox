import json
import urllib

import sys

# For regular expression
import re

# function to do Search API call
def searchQuery(query):

	api_key = open("api_key.txt").read()
	# print api_key
	# query = 'blue bottle'
	service_url = 'https://www.googleapis.com/freebase/v1/search'
	params = {
	        'query': query,
	        'key': api_key
	}
	url = service_url + '?' + urllib.urlencode(params)
	response = json.loads(urllib.urlopen(url).read())
	return response

# function to do Topic API call
def topicQuery(topic_id):

	api_key = open("api_key.txt").read()
	service_url = 'https://www.googleapis.com/freebase/v1/topic'
	topic_id = '/m/016z2j' # id of actor
	params = {
	  'key': api_key,
	  'filter': 'suggest'
	}
	url = service_url + topic_id + '?' + urllib.urlencode(params)
	topic = json.loads(urllib.urlopen(url).read())
	return topic

# Pass the topicResult['property']['/type/object/type']['values'](array) 
# into this function
def matchEntity(entities):
	entityDict = {}
	matchAny = False

	# Build a dictionary of the entities we are interested in
	with open("entity.txt","r") as text:
		entityDict = dict((line.strip(), {'found': False, 'entityType': ''}) for line in text)

	for entity in entities:
		if entity['id'] in entityDict:
			entityDict[entity['id']]['found'] = True
			entityDict[entity['id']]['entityType'] = entity['text']
			matchAny = True

	return entityDict, matchAny

def personInfo(topicResult):
	
	propertyDict = {}
	infoBox = {}

	# Build a dictionary of the entities we are interested in
	with open("person_property.txt","r") as text:
		for line in text:
			prop = line.strip().split('-')
			# first is the key, last is the name of the property
			propertyDict[prop[0]] = prop[1:]

	# Extract properties from the Topic API response
	for prop in propertyDict:
		if prop in topicResult['property']:
			temp = topicResult['property'][prop]
			matchObj = re.match(r'.+_s', prop, 0)
			if matchObj:
				# array of "values"
				for entry in temp['values']:
					temp2 = entry['property']
					# multiple property needs to be extracted
					for subprop in propertyDict[prop][:-1]:
						if subprop in temp2:
							infoBox[propertyDict[prop][-1]] = temp2[subprop]['values']['text']
			else:
				infoBox[propertyDict[prop][-1]] = temp['values'][0]['text']
			
	print propertyDict
	print infoBox
	
# Write JSON response to file
def jsonWrite(data, fileName):
	with open(fileName, 'w') as outfile:
		json.dump(data, outfile, sort_keys = True, indent = 4)
	

def main():
	# Taking query from command line
	query = sys.argv[1]
	searchResult = searchQuery(query)
	jsonWrite(searchResult, 'search_response.txt')

	# To keep track of all the existing entities that we are interested in
	entityDict = {}
	# To store the information extracted from Topic API response
	infoBox = {}

	# iteration = 0

 	for result in searchResult['result']:
 		topicResult = topicQuery(result['mid'])
		entityDict, match = matchEntity(topicResult['property']['/type/object/type']['values'])

		if match == True:
			break
		# iteration += 1

	personInfo(topicResult)

	jsonWrite(topicResult, 'topic_response.txt')

if __name__ == '__main__':
	main()