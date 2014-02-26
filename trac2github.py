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
tracCsvUrl = 'https://trac.mpi.nl/query?component=KinOath-desktop&component=KinOath-web&max=10000&col=id&col=summary&col=component&col=owner&col=type&col=status&col=priority&col=milestone&col=version&col=resolution&col=time&col=changetime&col=reporter&col=keywords&col=cc&report=24&order=milestone&col=description&format=csv'
githubApiUrl = 'https://api.github.com'

milestoneUrl = githubApiUrl + '/repos/%s/%s/milestones' % (githubProject, githubRepository)
issuesUrl = githubApiUrl + '/repos/%s/%s/issues' % (githubProject, githubRepository)
print(milestoneUrl)

knownMilestones = []

def getAllMileStones():
    response = urllib.urlopen(milestoneUrl)
    content = response.read()
    #print(content)
    milestones = json.loads(content)
    #print(milestones)
    del knownMilestones[:]
    for entry in milestones:
        print entry['number'], ' : ', entry['title']
        knownMilestones.insert(entry['number'], entry['title'])

def getMileStoneId(milestoneTitle):
    if len(milestoneTitle.strip()) == 0:
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

def makeIssueRequest(data):
    print(data)
    datalength = len(data)
    request = urllib2.Request(issuesUrl, data, {'Content-Type': 'application/json', 'Content-Length': datalength})
    request.add_header('Authorization', 'Basic %s' % base64string)
    response = urllib2.urlopen(request)
    print(response)
    time.sleep(1)

getAllMileStones()

githubToken = raw_input("GitHub Password:")
base64string = encodestring('%s:%s' % (githubUsername, githubToken)).replace('\n', '')

tracCSV = urllib.urlopen(tracCsvUrl)
tracTickets = csv.DictReader(tracCSV)
tickets = []
# print(tracTickets)
# create any missing milestones
print 'adding milestones'
for ticket in tracTickets:
    milestoneId = getMileStoneId(ticket['milestone'])
# make sure the milestone list is up to date
getAllMileStones()
print 'adding tickets'
# insert the tickets as issues
tracCSV = urllib.urlopen(tracCsvUrl)
tracTickets = csv.DictReader(tracCSV)
for ticket in tracTickets:
    #print (ticket)
    milestoneId = getMileStoneId(ticket['milestone'])
    print 'milestone: ', milestoneId
    data=json.dumps({'title': ticket['summary'], 'body': ticket['description'], 'milestone': milestoneId,
    'labels': [ticket['component'], ticket['type'], ticket['priority'], ticket['resolution']]})
    # so far unused fields: col=id& &col=time &col=changetime &col=reporter &col=keywords &col=cc 'assignee': ticket['owner'], , ticket['version']
    makeIssueRequest(data)
    #if ticket['status'] == 'closed':
    #    data=json.dumps({'title': ticket['summary'], "state": "closed"})
    #    makeIssueRequest(data)

exit(0)
