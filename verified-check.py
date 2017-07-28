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

print(os.environ.get('TEST',''))

isPrValid = False
def getData(url):
    headers = {'content-type': 'application/json', 'Accept': 'application/vnd.github.cryptographer-preview'}
    if oauthToken:
        headers['Authorization'] = 'token '+ oauthToken
    response = requests.get(url, headers=headers)
    return json.loads(response.text)


if droneEvent == "push":
    print("Push event - no verification check required")
    sys.exit(0)

commits = getData("https://api.github.com/repos/"+ repoOwner + "/"+ repoName + "/pulls/"+ str(pullRequestNumber) +"/commits")
print("Checking PGP verification status of PR "+ str(pullRequestNumber))
if len(commits) == 0:
    print("No commits found")
    sys.exit(1)

for commit in commits:
    commitData = getData(commit['url'])
    pprint(commitData)
    if commitData.get('commit').get('verification'):
        if commitData.get('commit').get('verification').get('verified') == True:
            print("Commit "+  commitData.get('sha') +" is valid!")
            isPrValid = True
        else:
            print("Commit " + commitData.get('sha') + " is NOT valid!")
            isPrValid = False
    else:
        isPrValid = False


if isPrValid:
    print("All PGP checks passed")
    sys.exit(0)
else:
    print("PGP checks did not pass")
    sys.exit(1)
