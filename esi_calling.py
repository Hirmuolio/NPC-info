#Esi calling 1.2


import json
import time
import base64
import random
import sys
import webbrowser

from datetime import datetime
from datetime import timedelta

from requests_futures.sessions import FuturesSession

session = FuturesSession(max_workers=50)


scopes = ''
user_agent = 'ESI calling script by Hirmuolio'
config = { }


def load_config():
	global config
	try:
		config = json.load(open('esi_config.json'))
		client_id = config['client_id']
		client_secret = config['client_secret']
	except:
		print('no client ID or secret found. \nRegister at https://developers.eveonline.com/applications to get them')
		
		client_id = input("Give your client ID: ")
		client_secret = input("Give your client secret: ")
		config["client_id"] = client_id
		config["client_secret"] = client_secret
		config["authorizations"] = {}
		with open('esi_config.json', 'w') as outfile:
			json.dump(config, outfile, indent=2)

def get_authorized():
	return config[ "authorizations" ].keys()

def set_user_agent(new_user_agent):
	global user_agent
	user_agent = new_user_agent

	
def logging_in(scopes):
	global config
	
	client_id = config['client_id']
	client_secret = config['client_secret']
	
	login_url = 'https://login.eveonline.com/oauth/authorize?response_type=code&redirect_uri=http://localhost/oauth-callback&client_id='+client_id+'&scope='+scopes
	authentication_url = "https://login.eveonline.com/oauth/token"
	
	number_of_attempts = 1
	while True:
		webbrowser.open(login_url, new=0, autoraise=True)

		authentication_code = input("Give your authentication code: ")
		
		combo = base64.b64encode(bytes( client_id+':'+client_secret, 'utf-8')).decode("utf-8")
		
		headers = json.dumps({"Authorization":"Basic "+combo, "User-Agent":user_agent})
		data = json.dumps({"grant_type": "authorization_code", "code": authentication_code})
		
		esi_response = make_call(url = authentication_url, headers = headers, data = data, calltype='post', job = 'exchange authorization code for tokens')[1]
		
		if call_was_succesful(esi_response, 'refresh authorization tokens', number_of_attempts):
			tokens = {}
			
			tokens['refresh_token'] = esi_response.json()['refresh_token']
			tokens['access_token'] = esi_response.json()['access_token']
			tokens['expiry_time'] = str( datetime.utcnow() + timedelta( seconds = esi_response.json()['expires_in']) )
			
			token_info = get_token_info(tokens)
			
			tokens['character_name'] = token_info['character_name']
			tokens['character_id'] = str( token_info['character_id'] )
			tokens['scopes'] = token_info['scopes']
			
			config['authorizations'][tokens['character_id']] = tokens
			with open('esi_config.json', 'w') as outfile:
				json.dump(config, outfile, indent=2)
			print( '  Character "'+ token_info['character_name'] +'" succesfully logged in' )
			break
		else:
			number_of_attempts += 1
			check_server_status()
			print('  Retrying login process...')
	
def check_tokens(authorizer_id):
	#Check if access token still good
	#If access token too old or doesn't exist generate new access token
	
	#refresh_token = tokens['refresh_token']
	#access_token = tokens['access_token'] (optional)
	#expiry_time = tokens['expiry_time'] (optional. Should exist with access token)
	global config
	
	try:
		tokens = config['authorizations'][str(authorizer_id)]
	except:
		print('  Error:ID: "'+str(authorizer_id)+'" has no authorization. Something is very broken.')
		print( config )
	
	number_of_attempts = 1
	
	
	#Check if token is valid
	#Needs to be done like this since the expiry time may or may not exist
	if datetime.utcnow() < datetime.strptime(tokens['expiry_time'], '%Y-%m-%d %H:%M:%S.%f') - timedelta( seconds = 20 ):
		return
	
	# The tokens have expired (or are about to expire)
	print( "  Refreshing expired tokens" )
	client_id = config['client_id']
	client_secret = config['client_secret']
	
	refresh_url = 'https://login.eveonline.com/oauth/token'
	combo = base64.b64encode(bytes( client_id+':'+client_secret, 'utf-8')).decode("utf-8")
	
	headers = json.dumps({"Authorization":"Basic "+combo, "User-Agent":user_agent})
	data = json.dumps({"grant_type": "refresh_token", "refresh_token": tokens['refresh_token']})
	
	while True:
		esi_response = make_call(url = refresh_url, headers = headers, data = data, calltype='post', job = 'refresh authorization tokens')[1]
		
		if call_was_succesful(esi_response, 'refresh authorization tokens', number_of_attempts):
			config['authorizations'][str(authorizer_id)]['refresh_token']	= esi_response.json()['refresh_token']
			config['authorizations'][str(authorizer_id)]['access_token'] = esi_response.json()['access_token']
			config['authorizations'][str(authorizer_id)]['expiry_time'] = str( datetime.utcnow() + timedelta( seconds = esi_response.json()['expires_in']) )
			with open('esi_config.json', 'w') as outfile:
				json.dump(config, outfile, indent=2)
			break
		else:
			number_of_attempts += 1
			print('  Your login may have been invalidated. Retrying in 5 seconds.')
			time.sleep( 5 )
			check_server_status()
		

def get_token_info(tokens):
	#Uses the access token to get various info
	#character ID
	#character name
	#expiration time (not sure on format)
	#scopes
	#token type (char/corp)
	
	url = 'https://login.eveonline.com/oauth/verify'
	
	headers = json.dumps({"Authorization":"Bearer "+tokens['access_token'], "User-Agent":user_agent})
	number_of_attempts = 1
	token_info = {}
	
	while True:
		esi_response = make_call(url = url, headers = headers, job = 'get token info')[1]
		
		if call_was_succesful(esi_response, 'get token info', number_of_attempts):
			token_info['character_name'] = esi_response.json()['CharacterName']
			token_info['character_id'] = esi_response.json()['CharacterID']
			token_info['expiration'] = esi_response.json()['ExpiresOn']
			token_info['scopes'] = esi_response.json()['Scopes']
			token_info['token_type'] = esi_response.json()['TokenType']
			break
		else:
			check_server_status()
			if number_of_attempts < 10:
				print( "  Failed to get token info. Retrying...")
				number_of_attempts +=1
			else:
				print( "  Failed to get token info 10 times. Something is probably very broken.\nExiting in 60 seconds...")
				time.sleep( 60 )
				sys.exit(0)
		
	return token_info


def call_was_succesful(esi_response, job, attempts):
	#Error checking
	#Returns True if call was succesful
	#Returns false if call failed. Retry the call.
	#[200, 204, 304] = All OK
	#[404,  400] = not found or user error. Call was succesful, input was bad.
	#401 = unauthorized. Call was succesful, problem is somewhere else.
	#402 = invalid autorization. Call was succesful, problem is somewhere else.
	#403 = No permission. Call was succesful, problem is somewhere else.
	#420 = error limited. Wait the duration and retry.
	#[500, 503, 504] = Server problem. Just retry.
	# 520 = Not sure. Too early called after downtime?
	
	if "warning" in esi_response.headers:
		print( esi_response.headers["warning"] )
	
	if esi_response.status_code in [200, 204, 304, 400, 404]:
		return True
	else:
		#First part of error message
		print(' ', datetime.utcnow().strftime('%H:%M:%S'), 'Failed to ' + job +'. Error',esi_response.status_code, end="")
		
		#Second half of the error message. Some errors have no description so try to print it
		try:
			print(' -', esi_response.json()['error'])
		except:
			print(' - no error message')
		
		if esi_response.status_code in [500, 502, 503, 504]:
			time_to_wait = round( min( (2 ** attempts) + (random.randint(0, 1000) / 1000), 300) )
			print('  Retrying in', time_to_wait, 'second...')
			time.sleep(time_to_wait)
		elif code in [520]:
				time_to_wait = 60
		elif esi_response.status_code in [401, 402]:
			#TODO: Refresh autorization
			print('Restart the script to get fresh authorization. If problem continues your character has no access to thir resource.\nExiting in 60 seconds...')
			time.sleep( 60 )
			sys.exit(0)
		elif esi_response.status_code == 403:
			#TODO: Refresh autorization
			print('You do not have access to this thing.\nExiting in 60 seconds...')
			time.sleep( 60 )
			sys.exit(0)
		elif esi_response.status_code == 420:
			time.sleep(esi_response.headers['x-esi-error-limit-reset']+1)
		else:
			#Some other error
			print('  Unknown error. Retrying')
	return False

def many_calls_error_check(response_array, job, attempts):
	#Error checking
	#Returns True if call was succesful
	#Returns false if call failed. Retry the call.
	#[200, 204, 304] = All OK
	#[404,  400] = not found or user error. Call was succesful, input was bad.
	#401 = unauthorized. Call was succesful, problem is somewhere else.
	#402 = invalid autorization. Call was succesful, problem is somewhere else.
	#403 = No permission. Call was succesful, problem is somewhere else.
	#420 = error limited. Wait the duration and retry.
	#[500, 503, 504] = Server problem. Just retry.
	# 520 = Too soon after downtime. Wait a minute and retry.
	
	number_of_responses = len( response_array )
	refetch_indexs = []
	time_to_wait = 0
	error_time_to_wait = 0
	
	for index  in range(number_of_responses):
	
		if "warning" in response_array[index].headers:
			print( response_array[index].headers["warning"] )
		try:
			code = response_array[index].status_code
		except:
			#The call failed completely
			code = 0

		if code in [200, 204, 304, 400, 404]:
			# Everything OK
			continue
		else:
			print(' ', datetime.utcnow().strftime('%H:%M:%S'), 'Failed to ' + job +'. Error',response_array[index].status_code, end="")
			#Second half of the error message. Some errors have no description so try to print it
			try:
				print(' -', response_array[index].json()['error'])
			except:
				print(' - no error message')
			
			if code in [500, 502, 503, 504]:
				refetch_indexs.append(index)
				time_to_wait = round( max( min( (2 ** attempts) + (random.randint(0, 1000) / 1000), 300), time_to_wait) )
			elif code in [520]:
				refetch_indexs.append(index)
				time_to_wait = max( 60, time_to_wait)
			elif code in [401, 402]:
				#TODO: Refresh autorization
				print('  Restart the script to get fresh authorization. If problem continues your character has no access to thir resource.\nExiting in 60 seconds...')
				time.sleep( 60 )
				sys.exit(0)
			elif code == 403:
				#TODO: Refresh autorization
				print('  You do not have access to this thing.\nExiting in 60 seconds...')
				time.sleep( 60 )
				sys.exit(0)
			elif code == 420:
				refetch_indexs.append(index)
				time_to_wait = max( response_array[index].headers['x-esi-error-limit-reset']+1, time_to_wait )
			elif code == 0:
				print('  Error - failed call.')
				refetch_indexs.append(index)
			else:
				#Some other error
				print('  Unknown error.')
		
	
	if time_to_wait > 0:
		print( "  retrying in", time_to_wait, "seconds" )
		time.sleep( time_to_wait )
	return refetch_indexs
	

def check_server_status():
	url = 'https://esi.evetech.net/v1/status/?datasource=tranquility'
	headers = {"User-Agent":user_agent}
	while True:
		future = session.get(url, headers = headers)
		esi_response = future.result()
		
		if "warning" in esi_response.headers:
			print( esi_response.headers["warning"] )
			
		if esi_response.status_code != 200:
			print( "  Server not OK. Waiting 1 minute" )
			time.sleep( 60 )
		else:
			break
	
def make_many_calls(urls, headers = {}, calltype='get', job = 'make ESI call'):
	#Use this to call many different URLs at once
	#Returns the responses and the used urls
	
	#Show what is sent to CCP	
	
	futures = [] 
	responses = []
	for url in urls:
		futures.append(session.get(url, headers = headers))

	for future in futures:
		responses.append(future.result())
	
	error_check_rounds = 0
	
	number_of_responses = len(responses)
	
	while True:
		sleep_time = 0
		refetch_urls = []
		refetch_indexs = []
		
		refetch_indexs = many_calls_error_check(responses, job, error_check_rounds)
		
		if len( refetch_indexs ) == 0:
			# Everything is good.
			break
		else:
			error_check_rounds = error_check_rounds + 1
			check_server_status()
			print('  Refetching ', len(refetch_indexs), ' urls...')
			
			for index in refetch_indexs:
				future = session.get(urls[index], headers = headers)
				esi_response = future.result()
				
				responses[refetch_indexs[index]] = esi_response
					
	return_array = []
	for index in range( len(urls) ):
		return_array.append( [urls[index], responses[index] ] )
	
	return return_array

def call_many_pages(url, headers = {}, pages = None, calltype='get', job = 'make ESI call'):
	#Use this get many pages off of same url
	#Returns array with rest of the pages
	
	futures = [] 
	responses = []
	for page in range(2, pages + 1):
		futures.append(session.get(url, headers = headers, params={'page': page}))

	for future in futures:
		responses.append(future.result())
	
	error_check_rounds = 0
	
	number_of_responses = len(responses)
	
	while True:
		sleep_time = 0
		refetch_pages = []
		
		refetch_indexes = many_calls_error_check(responses, job, error_check_rounds)
		
		if len( refetch_indexes ) == 0:
			# Everything OK
			break
		else:
			check_server_status()
			# The page is index + 2
			refetch_pages = [x+2 for x in refetch_indexes]
			print('  Refetching ', len(refetch_pages), ' pages...')
			for page in refetch_pages:
				future = session.get(url, headers = headers, params={'page': page})
				esi_response = future.result()
				
				responses[page-2] = esi_response
	
			error_check_rounds = error_check_rounds + 1
			
	return responses

def make_call(url, headers = '', data = '', page = None, calltype='get', job = 'make ESI call'):
	#Makes single call to ESI and returns the used url and the response.
	#The dictionaries comes in as a string to avoid certain dictionary fuckery
	
	#headers = user agent and authorization token things
	#data = Login things
	
	#Gives up after 10 failures
	
	try:
		headers = json.loads(headers)
	except:
		headers = {}
	
	#Data is only used for logging in
	try:
		data = json.loads(data)
	except:
		data = {}
	
	if page != None:
		params={'page': page}
	else:
		params={}
	
	attempts = 0
	
	while attempts < 10:
		attempts +=  1
		
		#grequests.get(url, headers = headers).send().response
		try:
			if calltype == 'get':
				future = session.get(url, headers = headers, data = data, params = params)
			elif calltype == 'post':
				future = session.post(url, headers = headers, data = data, params = params)
			elif calltype == 'delete':
				future = session.delete(url, headers = headers, data = data, params = params)
			esi_response = future.result()
		except:
			# Maybe set up for a retry, or continue in a retry loop
			print('Exception on ', url, ' page', page, '. Ignoring...')
		
		if call_was_succesful(esi_response=esi_response, job=job, attempts=attempts):
			return [url, esi_response]
		
	#The following will run only if the call fails too many times.
	print('Unable to make ESI call after', attempts, 'attempts')
	print('Shit is broken')
	input("Press enter to continue (something is very broken)")
	return [url, esi_response]

def call_esi(scope, url_parameters = [], etag = None, authorizer_id = None, datasource = 'tranquility', calltype='get', job = ''):
	#scope = url part. Mark the spot of parameter with {par}
	#url_parameter = parameter that goes into the url. Can be array to make many calls
	#etag = TODO
	#authorizer_id = ID of the char whose authorization will be used
	
	#datasource. Default TQ
	#calltype = get, post or delete. Default get
	#job = string telling what is being done. Is displayed on error message.
	
	# Returns array of arrays of resonses.
	# [ [response for url 1], [response for url 2], ...]
	# [ [page 1, page 2, ...], [page 1, page 2, ...] ]
	# For single call the response is responses[0][0]
	
	#un-authorized / authorized
	if authorizer_id == None:
		headers = {"User-Agent":user_agent}
	else:
		check_tokens(authorizer_id)
		access_code = config['authorizations'][str(authorizer_id)]['access_token']
		headers =  {"Authorization":"Bearer "+access_code, "User-Agent":user_agent}
	
	urls = []
	
	#Build the urls to call to
	#Also replace // with / to make things easier
	#url = 'https://' + ('esi.evetech.net'+scope+'/?datasource='+datasource).replace('{par}', str(url_parameter)).replace('//', '/')
	if len(url_parameters) == 0:
		url = 'https://' + ('esi.evetech.net'+scope+'/?datasource='+datasource).replace('//', '/')
		urls.append(url)
	else:
		for parameter in url_parameters:
			url = 'https://' + ('esi.evetech.net'+scope+'/?datasource='+datasource).replace('{par}', str(parameter)).replace('//', '/')
			urls.append(url)
			
	responses = make_many_calls(urls, headers = headers, calltype=calltype, job = job)			
	
	#Responses is an array of arrays.
	#Each array contains the call url and responses that correspond to the url.
	#If the response is only one page then the array contains only one response.
	#If multipage response then the array contains all the pages (done in next step).
	#Example:
	#[ ['url', page1], ['url', page1, page2, page3], ['url', page1] ]
	
	
	#Check if multipages.
	for index in range(len(responses)):
		#url = responses[index][0]
		#esi_response = responses[index][1]
		if 'X-Pages' in responses[index][1].headers:
			#Multipage thing. Get all the pages
			total_pages = int(responses[index][1].headers['X-Pages'])
			if total_pages > 1:
				print('  Multipage response. Fetching ', total_pages, ' pages' )
				
				multipages = call_many_pages(responses[index][0], headers = headers, pages = total_pages, calltype=calltype, job = job)
				
				responses[index].extend( multipages )
			
	

	#Remove url from the responses
	for index in range( len(responses)):
		del responses[index][0]
		
	return responses
	
	
	
	
	
