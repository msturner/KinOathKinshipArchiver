#!/usr/bin/python
# Author: Peter Withers
# Date: 2014/02/26

import csv
from base64 import encodestring
import json
import sys
import time
import urllib
import urllib2

githubUsername = sys.argv[1]
githubProject = sys.argv[2]
githubRepository = sys.argv[3]
print 'GitHub username: ', githubUsername
print 'GitHub project:', githubProject
print 'GitHub repository: ', githubRepository
tracCsvUrl = 'https://trac.mpi.nl/query?component=KinOath-desktop&component=KinOath-web&max=1000&col=id&col=summary&col=component&col=owner&col=type&col=status&col=priority&col=milestone&col=version&col=resolution&col=time&col=changetime&col=reporter&col=keywords&col=cc&report=24&order=milestone&col=description&format=csv'
githubApiUrl = 'https://api.github.com'

milestoneUrl = githubApiUrl + '/repos/%s/%s/milestones' % (githubProject, githubRepository)
print(milestoneUrl)

githubToken = raw_input("GitHub Password:")
base64string = encodestring('%s:%s' % (githubUsername, githubToken)).replace('\n', '')

knownMilestones = []

def getMileStoneId(milestoneTitle):
    if len(milestoneTitle.strip()) eq 0:
        return ""
    if not milestoneTitle in knownMilestones:
        data=json.dumps({'title': milestoneTitle, 'state': 'open'})
        #data=json.dumps({'title': 'milestone', 'state': 'open', 'desription': '.', 'due_on': '2012-10-09T23:39:01Z'})
        print(data)
        datalength = len(data)
        request = urllib2.Request(milestoneUrl, data, {'Content-Type': 'application/json', 'Content-Length': datalength})
        #request = urllib2.Request(milestoneUrl, data)
        #, 'Content-Length': datalength}
        request.add_header('Authorization', 'Basic %s' % base64string)
        response = urllib2.urlopen(request)
        print(response)
        knownMilestones.append(milestoneTitle)
        time.sleep(1)
    return knownMilestones.index(milestoneTitle)

tracCSV = urllib.urlopen(tracCsvUrl)
tracTickets = csv.DictReader(tracCSV)
tickets = []
print(tracTickets)
for ticket in tracTickets:
    print (ticket)
    for column in ticket:
        print column,":",ticket[column]
    
    milestoneId = getMileStoneId(ticket['milestone'])
    print 'milestone: ', milestoneId
exit(0)
