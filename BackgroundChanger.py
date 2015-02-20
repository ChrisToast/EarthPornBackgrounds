'''
Created on Nov 24, 2014

Updated on Feb 18, 2015 to support multiple monitors dynamically and
pathing to arbitrary Mac Users.

@author: Chris Bernt
'''

import praw
import requests
import shutil
import os
import datetime
import subprocess
import re

homePath = os.path.dirname(os.path.realpath(__file__))
pathAddition = "/desktop-backgrounds/background" + str(datetime.date.today())

user_agent = "EarthPorn desktop backgrounds by /u/ChrisToast"
r = praw.Reddit(user_agent=user_agent) 


def main():
    print "IN PYTHON FILE"
    getTopResults("EarthPorn")

def getTopResults(subreddit):
    submissions = r.get_subreddit(subreddit).get_top(limit=10)
    getBestResults(submissions, [], 1, int(getNumberOfDesktops()))
    
    
def getBestResults(submissions, toIgnore, desktopNumber, numDesktops):
    if desktopNumber > numDesktops:
        return

    for a in submissions:
        if goodToUse(a, toIgnore):
            path = homePath + pathAddition + "(" + str(desktopNumber) + ").jpg"
            readImageToFile(path, a.url)
            makeBackground(path, desktopNumber)
            toIgnore.append(a.url)
            break
    
    getBestResults(submissions, toIgnore, desktopNumber+1, numDesktops)


def goodToUse(submission, toIgnore):
    p = re.compile("\[(\d+)(.*?)\]")
    try:
        res = "".join([i for i in p.findall(submission.title)[0]]).split("x")
        width = float(res[0].strip())
        height = float(res[1].strip())
        return width/height > 1.2 and submission.url not in toIgnore
    except: #just in case anything goes wrong (improper submission format, non unicode characters)
        return False


def readImageToFile(path, url):
    response = requests.get(url, stream=True)
    with open(path, 'wb+') as out_file:
        shutil.copyfileobj(response.raw, out_file)
        del response 
        
def getNumberOfDesktops():
    ascript = '''
    tell application "System Events"
        return count of desktops
    end tell
    '''
    return asrun(ascript)
    
def makeBackground(imagePath, desktopNumber):

    ascript = '''
    tell application "System Events"
        tell desktop %d
            set picture to "%s"
        end tell
    end tell
    ''' % (desktopNumber, imagePath)
    
    asrun(ascript)    
    
    
def asrun(ascript):
    "Run the given AppleScript and return the standard output and error."

    osa = subprocess.Popen(['osascript', '-'],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    return osa.communicate(ascript)[0]

def asquote(astr):
    "Return the AppleScript equivalent of the given string."
  
    astr = astr.replace('"', '" & quote & "')
    return '"{}"'.format(astr)    
    
main()