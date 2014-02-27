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
print(issuesUrl)

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

def createRequiredEmptyTickets(tracTicketCount):
    print 'total ticket count: ', tracTicketCount
    response = urllib.urlopen(issuesUrl)
    content = response.read()
    tickets = json.loads(content)
    #print(tickets)
    currentIssueCount = tickets[0]['number']
    while tracTicketCount > currentIssueCount:
        currentIssueCount = currentIssueCount + 1
        makeEmptyIssueRequest()

def makeEmptyIssueRequest():
    data=json.dumps({'title': 'dummy ticket to allow imports with the correct ticket id'})
    datalength = len(data)
    request = urllib2.Request(issuesUrl, data, {'Content-Type': 'application/json', 'Content-Length': datalength})
    request.add_header('Authorization', 'Basic %s' % base64string)
    response = urllib2.urlopen(request)
    print(response)
    time.sleep(1)

def makeIssueRequest(ticketId, data):
    print (ticketId)
    print(data)
    datalength = len(data)
    request = urllib2.Request(issuesUrl + '/' + ticketId, data, {'Content-Type': 'application/json', 'Content-Length': datalength})
    request.add_header('Authorization', 'Basic %s' % base64string)
    response = urllib2.urlopen(request)
    print(response)
    time.sleep(1)

getAllMileStones()

githubToken = raw_input("GitHub Password:")
base64string = encodestring('%s:%s' % (githubUsername, githubToken)).replace('\n', '')

tracCSV = urllib.urlopen(tracCsvUrl)
tracTickets = csv.DictReader(tracCSV)

# print(tracTickets)
# create any missing milestones
print 'adding milestones'
tracTicketCount = 0
for ticket in tracTickets:
    tracTicketCount = tracTicketCount + 1
    milestoneId = getMileStoneId(ticket['milestone'])
# make sure the milestone list is up to date
getAllMileStones()
print 'adding tickets'
createRequiredEmptyTickets(tracTicketCount)
# insert the tickets as issues
tracCSV = urllib.urlopen(tracCsvUrl)
tracTickets = csv.DictReader(tracCSV)
currentTicket = 0
for ticket in tracTickets:
    #print (ticket)    
    currentTicket = currentTicket + 1
    milestoneId = getMileStoneId(ticket['milestone'])
    #print 'milestone: ', milestoneId
    if ticket['status'] == 'closed':
        status = 'closed'
    else:
        status = 'open'
    if milestoneId == 0:
        # if there is no milestone then we must not pass it as a parameter
        data=json.dumps({'title': ticket['summary'], 'body': ticket['description'].strip(), "state": status, 'labels': [ticket['component'], ticket['type'], ticket['priority'], ticket['resolution']]})
    else:
        data=json.dumps({'title': ticket['summary'], 'body': ticket['description'].strip(), 'milestone': milestoneId, "state": status, 'labels': [ticket['component'], ticket['type'], ticket['priority'], ticket['resolution']]})
    # so far unused fields: col=id& &col=time &col=changetime &col=reporter &col=keywords &col=cc 'assignee': ticket['owner'], , ticket['version']
    #if currentTicket > 223: # ticket 224 has issues that are as yet un identified, ticket 147 is the fist one to not have a milestone
    makeIssueRequest(str(currentTicket), data) # ticket['id']
exit(0)
