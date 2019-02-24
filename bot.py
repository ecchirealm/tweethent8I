import os, sys, threading, time, signal, twitter, csv
import random
from datetime import datetime

conKey = ""
conSec = ""
accTok = ""
accSec = ""
tweets = []
threads = []
timeInBetweenPosts = 0
timeBase = time.time()

def auth():
        # check for stored data

        fl = ""
        global conKey
        global conSec
        global accTok
        global accSec

        try:
                fl = open("config", "r+").read()
                if(input("\nPrevious settings found. Should use it? (y/n): ") == "n"):
                        fl = ""
        except:
                print("\nNo previous settings found")

        if(fl == ""):
                #ask for credentials
                conKey = input("Consumer Key: ")
                conSec = input("Consumer Secret: ")
                accTok = input("Access Token: ")
                accSec = input("Access Token Secret: ")
                fr = open("config", "w+")
                fr.write(conKey + ":" + conSec + ":" + accTok + ":" + accSec)
        else:
                conKey = fl.split(":")[0]
                conSec = fl.split(":")[1]
                accTok = fl.split(":")[2]
                accSec = fl.split(":")[3]

        #login
        twitter.auth(conKey, conSec, accTok, accSec)

def schedule():

        path = ""
        deli = ""
        global conKey
        global conSec
        global accTok
        global accSec

        try:
                cfg = open("config", "r").read()
                path = cfg.split(":")[4]
                deli = cfg.split(":")[5]

                if(input("\nPrevious CSV found (" + path + "). Should use it? (y/n): ") == "n"):
                        path = input("CSV file name (e.g sample.csv): ")
                        deli = input("Delimiter (default: ','): ")
        except:
                print("\nNo previous CSV found")
                path = input("CSV file name (e.g sample.csv): ")
                deli = input("Delimiter (default: ','): ")

        if(deli == ""):
                deli = ","

        open("config", "r+").write(conKey + ":" + conSec + ":" + accTok + ":" + accSec + ":" + path + ":" + deli)

        csvf = ""

        try:
                csfv = csv.reader(open(path, "r") , delimiter=",")
        except:
                print("\nCSV corrupted or not found. Try again.\n")
                schedule()
                return

        global tweets
        tweets = []
        
        for r in csfv:
            tweets.append(r)
            resourceUrl = r[2]
#            filePath = getResourceFromInternet(resourceUrl)
#            print('abbbbbb')
#            if(filePath != 0):
#                print('awefa')
#                r[2] = filePath
#                tweets.append(r)

        random.shuffle(tweets)

def start():

  global timeInBetweenPosts
  postInt = input("How many minutes between each tweet? ")
  if(postInt):
    timeInBetweenPosts = int(postInt) * 60

  print("")

  global tweets
  global threads
  cnt = 0
  for tw in tweets:

    if(timeInBetweenPosts == 0):
        print("Post interval not provided ! Post time scheduled in CSV will be used")
        time_str = tw[0]
        date = datetime.strptime(time_str, '%m/%d/%Y %I:%M:%S %p')

        tm = int((date - datetime.now()).total_seconds())

        if(tm < 1):
          print("It's too late to schedule: " + tw[1])
        else:
          t = threading.Timer(tm, work, [tw])
          t.start()
          threads.append(t)
          print("Post scheduled to " + tw[0])

        if(len(threads) > 0):
          print("\n--== Results ==--\n")
    else:
        tPost = (timeBase + timeInBetweenPosts + (timeInBetweenPosts * cnt)) - time.time()
        #tPost = (timeBase  + (timeInBetweenPosts * cnt)) - time.time()
        cnt += 2
        print(tPost)
        t = threading.Timer(tPost, work, [tw])
        t.start()
        threads.append(t)
        print("Post scheduled to " + str(int(tPost)) + " second(s) from now")

        if(len(threads) > 0):
          print("\n--== Results ==--\n")


def work(tw):
        print("[Tweet] Initializing...")
        twitter.start(conKey, conSec, accTok, accSec, tw[2], tw[1])


def signal_handler(sig, frame):
        sys.exit(0)

try:
        # set everything
        print("---=== TwitterBot - https://fiverr.com/lihilip ===---")
        auth()
        schedule()
        start()
        signal.signal(signal.SIGINT, signal_handler)
        try:
                signal.pause() # not work on Windows, batch pause
        except:
                pass

except:
        print("\nShutting down...")
        for t in threads:
                #t.cancel()
                print("Cancelling scheduled tweet...")
        print("Done.")
