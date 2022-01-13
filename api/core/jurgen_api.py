import json
import os
import sys

from api.moveshelf.api import MoveshelfApi
from api.moveshelf.api import Metadata

parentFolder = os.getcwd()
sys.path.append(parentFolder)

baseProject = 'support/API_assignment_jurgen'  # e.g. support/demoProject
baseSubject = 'JurgenSubject'  # subject name, e.g. Subject1
baseSession = '2022-1-1'  # session name, e.g. 2021-01-01
baseCondition = '3-min-run'  # condition name, e.g. 2-min walk
baseTrial = 'Trial-1'  # trial name, e.g. Trial-1


class JurgenApi(MoveshelfApi):
    def __init__(self):
        # Load the default configuration
        with open(os.path.join(parentFolder, 'mvshlf-config.spec.json'), 'r') as configFile:
            data = json.load(configFile)

        # And overwrite with personal configuration if available
        personalConfig = os.path.join(parentFolder, 'mvshlf-config.json')
        if os.path.isfile(personalConfig):
            with open(personalConfig, 'r') as configFile:
                data.update(json.load(configFile))

        MoveshelfApi.__init__(self, os.path.join(parentFolder, data['apiKeyFileName']), data['apiUrl'])

    def setProject(self, myProject=baseProject):
        projects = self.getUserProjects()
        projectNames = [p['name'] for p in projects]
        iMyProject = projectNames.index(myProject)
        return projects[iMyProject]['id']

    def setSubject(self, projectId, mySubject=baseSubject):
        subjects = self.getProjectSubjects(projectId)
        subjectNames = [s['name'] for s in subjects]

        if mySubject not in subjectNames:
            # create Subject
            subject = self.createSubject(projectId, mySubject)
            mySubjectId = subject['id']
        else:
            # get subject data
            iMySubject = subjectNames.index(mySubject)
            mySubjectId = subjects[iMySubject]['id']

        # Extract subject details
        return self.getSubjectDetails(mySubjectId)

    def setSession(self, subjectDetails, myProject, mySession=baseSession):
        sessions = subjectDetails['sessions']
        sessionExists = False
        for session in sessions:
            try:
                sessionName = session['projectPath'].split('/')[2]
            except:
                sessionName = ""
            if sessionName == mySession:
                sessionId = session['id']
                sessionExists = True
                print('Session found')
                break

        if not sessionExists:
            sessionPath = '/' + subjectDetails['name'] + '/' + mySession + '/'
            session = self.createSession(myProject, sessionPath, subjectDetails['id'])
            sessionId = session['id']
            print('Session created')

        return self.getSessionById(sessionId)

    def setConditions(self, session, myCondition=baseCondition):
        conditions = []
        conditions = getConditionsFromSession(session, conditions)

        condition = {}
        for c in conditions:
            if c['path'] == myCondition:
                condition = c
                break

        if not condition:
            condition['path'] = myCondition
            condition['clips'] = []

        return condition

    def setTrial(self, session, condition, myTrial=baseTrial):
        return addOrGetTrial(self, session, condition, myTrial)


def getConditionsFromSession(session, conditions=None):
    if conditions is None:
        conditions = []
    sessionPath = session['projectPath']
    clips = session['clips']
    for c in clips:
        clipPath = c['projectPath'].split(sessionPath)
        if len(clipPath) > 0 and len(clipPath[1]) > 0:
            conditionPath = clipPath[1]
            conditionFound = False
            for condition in conditions:
                if condition['path'] == conditionPath:
                    condition['clips'].append(c)
                    conditionFound = True
                    break

            if not conditionFound:
                condition = dict.fromkeys(['path', 'fullPath', 'norms', 'clips'])
                condition['path'] = conditionPath
                condition['fullPath'] = sessionPath + conditionPath
                condition['norms'] = []
                condition['clips'] = [c]
                conditions.append(condition)

    norms = session['norms']
    for n in norms:
        normPath = ''
        if n['projectPath']:
            normPath = n['projectPath'].split(sessionPath)
            if len(normPath) > 0:
                conditionPath = normPath[1]
                conditionFound = False
                for condition in conditions:
                    if condition['path'] == conditionPath:
                        condition['norms'].append(n)
                        conditionFound = True
                        break
                if not conditionFound:
                    condition = dict.fromkeys(['path', 'fullPath', 'norms', 'clips'])
                    condition['path'] = conditionPath
                    # condition['fullPath'] = sessionPath + conditionPath
                    condition['norms'] = [n]
                    condition['clips'] = []
                    conditions.append(condition)

    return conditions


def addOrGetTrial(api, session, condition, trialName=None):
    trialCount = len(condition['clips'])

    if trialName is None:
        trialNumbers = [clip['title'].split('-')[1] for clip in condition['clips'] if trialCount > 0]
        trialNumber = max(trialNumbers) if len(trialNumbers) > 0 else trialCount
        trialName = "Trial-" + str(trialNumber + 1)

    trialNames = [clip['title'] for clip in condition['clips'] if trialCount > 0]
    if trialName in trialNames:
        # return existing clip
        iClip = trialNames.index(trialName)
        clipId = condition['clips'][iClip]['id']
    else:
        # generate new clip
        metadata = Metadata()
        metadata['title'] = trialName
        metadata['projectPath'] = session['projectPath'] + condition['path']
        # metadata['allowDownload'] = False
        # metadata['allowUnlistedAccess'] = False
        clipId = api.createClip(session['project']['name'], metadata)

    return clipId
