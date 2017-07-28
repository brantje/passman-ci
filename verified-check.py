import requests
import json
import sys
import os

from pprint import pprint


pullRequestNumber = os.environ.get('DRONE_PULL_REQUEST')
repoOwner = os.environ.get('DRONE_REPO_OWNER')
repoName = os.environ.get('DRONE_REPO_NAME')
oauthToken = os.environ.get('OAUTH_TOKEN','')
droneEvent = os.environ.get('DRONE_BUILD_EVENT')


def getData(url):
    headers = {'content-type': 'application/json', 'Accept': 'application/vnd.github.cryptographer-preview'}
    if oauthToken:
        print("Got authorization token")
        headers['Authorization'] = 'token '+ oauthToken
    response = requests.get(url, headers=headers)
    return json.loads(response.text)

def checkCommit(commit, sha):
    if commit.get('verification'):
        if commit.get('verification').get('verified') == True:
            print("Commit "+  sha +" is valid!")
            return True
        else:
            print("Commit " + sha + " is NOT valid!")
            return False
    return False


if droneEvent == "push":
    commitData = getData("https://api.github.com/repos/"+ repoOwner + "/"+ repoName + "/git/commits/" + os.environ.get('DRONE_COMMIT_SHA'))
    print("Checking last commit: "+ os.environ.get('DRONE_COMMIT_SHA'))
    result = checkCommit(commitData, os.environ.get('DRONE_COMMIT_SHA'))
    if result:
        print("All PGP checks passed")
        sys.exit(0)
    else:
        print("PGP checks did not pass")
        sys.exit(1)

else:
    isPrValid = False
    commits = getData("https://api.github.com/repos/"+ repoOwner + "/"+ repoName + "/pulls/"+ str(pullRequestNumber) +"/commits")
    print("Checking PGP verification status of PR "+ str(pullRequestNumber))
    if len(commits) == 0:
        print("No commits found")
        sys.exit(1)

    for commit in commits:
        commitData = getData(commit['url'])
        if commitData.get('commit').get('verification'):
            isPrValid = checkCommit(commitData.get('commit'), commit.get('sha') )
        else:
            isPrValid = False
            break


    if isPrValid:
        print("All PGP checks passed")
        sys.exit(0)
    else:
        print("PGP checks did not pass")
        sys.exit(1)
