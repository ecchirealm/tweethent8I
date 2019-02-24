import os
import sys
import time
import urllib
import json
import requests , string, random
from requests_oauthlib import OAuth1


MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'
POST_TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''

VIDEO_FILENAME = ''

oauth = ""
networkAttemps = 0

class VideoTweet(object):

  def __init__(self, file_name):
    '''
    Defines video tweet properties
    '''
    self.video_filename = file_name
    #self.total_bytes = os.path.getsize(self.video_filename)
    self.media_id = None
    self.processing_info = None

    global oauth
    oauth = OAuth1(CONSUMER_KEY,
      client_secret=CONSUMER_SECRET,
      resource_owner_key=ACCESS_TOKEN,
      resource_owner_secret=ACCESS_TOKEN_SECRET)


  def upload_init(self):
    '''
    Initializes Upload
    '''

    try:
        self.total_bytes = os.path.getsize(self.video_filename)
    except:
        print('[Upload] Error: File not found')
        return 0

    request_data = ""

    ext = self.video_filename.split(".")

    if ext[len(ext) - 1] == "mp4":

        request_data = {
          'command': 'INIT',
          'media_type': 'video/mp4',
          'total_bytes': self.total_bytes,
          'media_category': 'tweet_video'
        }

    else:

        request_data = {
          'command': 'INIT',
          'media_type': 'image/jpeg',
          'total_bytes': self.total_bytes
        }

    req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=oauth)
    media_id = ""

    try:
        media_id = req.json()['media_id']
    except:
        print("Can't login on Twitter. Reason: " + req.json()["errors"][0]["message"])
        return 0

    self.media_id = media_id


  def upload_append(self):
    '''
    Uploads media in chunks and appends to chunks uploaded
    '''
    segment_id = 0
    bytes_sent = 0
    file = ""

    try:
        file = open(self.video_filename, 'rb')
    except:
        print('[Upload] Error: File not found')
        return 0

    print('[Upload] Starting')

    while bytes_sent < self.total_bytes:
      chunk = file.read(4*1024*1024)

      request_data = {
        'command': 'APPEND',
        'media_id': self.media_id,
        'segment_index': segment_id
      }

      files = {
        'media':chunk
      }

      req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, files=files, auth=oauth)

      if req.status_code < 200 or req.status_code > 299:
        print("Can't upload to Twitter. Reason: " + req.json()["error"])
        return 0

      segment_id = segment_id + 1
      bytes_sent = file.tell()

      print('[Upload] %s of %s MB uploaded' % (str((bytes_sent/1024)/1024), str((self.total_bytes/1024)/1024)))

    print('[Upload] Complete.')


  def upload_finalize(self):
    '''
    Finalizes uploads and starts video processing
    '''

    request_data = {
      'command': 'FINALIZE',
      'media_id': self.media_id
    }

    req = requests.post(url=MEDIA_ENDPOINT_URL, data=request_data, auth=oauth)

    print("[Upload] Processing...")
    self.processing_info = req.json().get('processing_info', None)
    return self.check_status()


  def check_status(self):
    '''
    Checks video processing status
    '''
    if self.processing_info is None:
      return

    state = self.processing_info['state']

    if state == u'succeeded':
      return

    if state == u'failed':
      print("[Upload] Twitter error: " + self.processing_info['error']['message'])
      return 0

    check_after_secs = self.processing_info['check_after_secs']
    
    time.sleep(check_after_secs)

    request_params = {
      'command': 'STATUS',
      'media_id': self.media_id
    }

    req = requests.get(url=MEDIA_ENDPOINT_URL, params=request_params, auth=oauth)
    self.processing_info = req.json().get('processing_info', None)
    return self.check_status()

  def tweet(self, tw):
    '''
    Publishes Tweet with attached video
    '''
    print("[Tweet] Posting: " + tw)
    request_data = {
      'status': tw.encode('latin-1'),
      'media_ids': self.media_id,
      #'media_ids': media
    }

    req = requests.post(url=POST_TWEET_URL, data=request_data, auth=oauth)

    url = ""

    try:
        url = req.json()['entities']['urls'][-1]['expanded_url']
    except:
        try:
            print("[Tweet] Error: " + req.json()['errors'][0]['message'])
            print("[Tweet] Aborted")
            print("")
            print("Started deleting local image...")
            if(os.path.isfile(VIDEO_FILENAME)):
               os.remove(VIDEO_FILENAME)
               print("Finished deleting local image.")
            else:
               print("Error while deleting : " + VIDEO_FILENAME+ " File Not Found")

            return 1
        except:
            print("[Tweet] Aborted due a network error")
            return 1

    print("[Tweet] URL: " + url + "\n")
    print("")
    print("Started deleting local image...")
    if(os.path.isfile(VIDEO_FILENAME)):
        os.remove(VIDEO_FILENAME)
        print("Finished deleting local image.")
    else:
        print("Error while deleting : " + VIDEO_FILENAME+ " File Not Found")
    print("")
    
    
  def auth(self):

    print("Logging to Twitter")

    req = requests.get(url="https://api.twitter.com/1.1/account/verify_credentials.json", auth=oauth)

    try:
        print("Logged as @" + req.json()["screen_name"])
    except:
        print("Can't login on Twitter. Reason: " + req.json()["errors"][0]["message"])
        print("Try again.")
        return 0

def getResourceFromInternet(resourceUrl):
    try:
        print("")
        print("Retrieving Resource at : " + resourceUrl)
        fileName = random_string(10) + ".mp4"
        urllib.request.urlretrieve(resourceUrl, os.getcwd()+"/images/"+fileName)
        print("Retrieving Resource Successfull")
        print("")
        return os.getcwd()+"/images/"+fileName
    except urllib.request.URLError as e:
        print(e)
        print("Failed Retrieving Resource : " + resourceUrl)
        return 0
      
def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for m in range(length))
    
def tweet(ckey, csecret, tk, tks, fl, tw, media):

	global MEDIA_ENDPOINT_URL
	global POST_TWEET_URL

	global CONSUMER_KEY
	global CONSUMER_SECRET
	global ACCESS_TOKEN
	global ACCESS_TOKEN_SECRET

	global VIDEO_FILENAME
	global STATUS_TO_POST
	global networkAttemps

	MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'
	POST_TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'

	CONSUMER_KEY = ckey
	CONSUMER_SECRET = csecret
	ACCESS_TOKEN = tk
	ACCESS_TOKEN_SECRET = tks

	VIDEO_FILENAME = getResourceFromInternet(fl)

	try:  
		videoTweet = VideoTweet(VIDEO_FILENAME)
		videoTweet.tweet(tw, media)

		networkAttemps = 0
	except Exception as e:
		print(e)
		if networkAttemps < 3:
			print("\nCan't connect to Twitter due a network error. Trying again...")
			networkAttemps = networkAttemps + 1
			return start(ckey, csecret, tk, tks, fl, tw)
		else:
			print("\nUnable to connect to Twitter after 4 attemps.")
			print("Check your conection and try again")
			return 0
    

def auth(ckey, csecret, tk, tks):

    global MEDIA_ENDPOINT_URL
    global POST_TWEET_URL

    global CONSUMER_KEY
    global CONSUMER_SECRET
    global ACCESS_TOKEN
    global ACCESS_TOKEN_SECRET

    global VIDEO_FILENAME
    global STATUS_TO_POST
    global networkAttemps

    MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'
    POST_TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'

    CONSUMER_KEY = ckey
    CONSUMER_SECRET = csecret
    ACCESS_TOKEN = tk
    ACCESS_TOKEN_SECRET = tks

    try:       
        videoTweet = VideoTweet("..")
        videoTweet.auth()
        networkAttemps = 0
    except Exception as e:
        print(e)
        if networkAttemps < 3:
            print("\nCan't connect to Twitter due a network error. Trying again...")
            networkAttemps = networkAttemps + 1
            return auth(ckey, csecret, tk, tks)
            
        else:
            print("\nUnable to connect to Twitter after 4 attemps.")
            print("Check your conection and try again")
            return 0

def start(ckey, csecret, tk, tks, fl, tw):

	global MEDIA_ENDPOINT_URL
	global POST_TWEET_URL

	global CONSUMER_KEY
	global CONSUMER_SECRET
	global ACCESS_TOKEN
	global ACCESS_TOKEN_SECRET

	global VIDEO_FILENAME
	global STATUS_TO_POST
	global networkAttemps

	MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'
	POST_TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'

	CONSUMER_KEY = ckey
	CONSUMER_SECRET = csecret
	ACCESS_TOKEN = tk
	ACCESS_TOKEN_SECRET = tks

	VIDEO_FILENAME = getResourceFromInternet(fl)

	try:  
		videoTweet = VideoTweet(VIDEO_FILENAME)
		if videoTweet.upload_init() != 0:
			if videoTweet.upload_append() != 0:
				if videoTweet.upload_finalize() != 0:
					videoTweet.tweet(tw)
					#return videoTweet.media_id
				else:
					return 0
			else:
				return 0
		else:
			return 0

		networkAttemps = 0
	except Exception as e:
		print(e)
		if networkAttemps < 3:
			print("\nCan't connect to Twitter due a network error. Trying again...")
			networkAttemps = networkAttemps + 1
			return start(ckey, csecret, tk, tks, fl, tw)
		else:
			print("\nUnable to connect to Twitter after 4 attemps.")
			print("Check your conection and try again")
			return 0

if __name__ == '__main__':
  videoTweet = VideoTweet(VIDEO_FILENAME)
  videoTweet.upload_init()
  videoTweet.upload_append()
  videoTweet.upload_finalize()
  videoTweet.tweet()
