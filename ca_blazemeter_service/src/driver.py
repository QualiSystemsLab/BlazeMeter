from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.context import ResourceCommandContext, InitCommandContext
from cloudshell.api.cloudshell_api import CloudShellAPISession
import requests
import json
from time import sleep


class CaBlazemeterServiceDriver (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self.key = ''
        self.secret = ''
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        self._get_key_and_secrect(context)

    def _get_key_and_secrect(self, context):
        try:
            self.key = context.resource.attributes["BlazeMeterKey"]
            self.secret = context.resource.attributes["BlazeMeterSecret"]
            if self.key == '' or self.secret == '':
                raise Exception('key/secret values cannot be empty')
        except:
            raise Exception('Failed to get key/secret values')

    def start_tests(self, context, test_name):
        """
        A simple example function
        :param ResourceCommandContext context: the context the command runs on
        :param str test_name: A test name to execute (or empty)
        """

        self._get_key_and_secrect(context)
        csapi = self._get_api_session(context)
        resid = context.reservation.reservation_id

        res = csapi.GetReservationDetails(resid).ReservationDescription
        resource = context.resource

        a2b = {}
        for conn in res.Connectors:
            if conn.Source not in a2b:
                a2b[conn.Source] = []
            a2b[conn.Source].append(conn.Target)
            if conn.Target not in a2b:
                a2b[conn.Target] = []
            a2b[conn.Target].append(conn.Source)

        targetname2url = {}
        for conn in res.Connectors:
            target = ''
            if resource.name == conn.Source:
                target = conn.Target
            if resource.name == conn.Target:
                target = conn.Source
            if target:
                targetname2url[target] = \
                    [a.Value for a in csapi.GetResourceDetails(target).ResourceAttributes if
                     a.Name == 'Web Interface'][0]

        # get the list of tests from bm
        jtests = requests.get('https://a.blazemeter.com/api/latest/tests', auth=(self.key, self.secret)).text
        dtests = json.loads(jtests)

        sessionid2targetname = {}

        executed = 0
        csapi.WriteMessageToReservationOutput(resid, 'Looking for matching tests')
        for dtest in dtests['result']:
            for targetname in targetname2url:
                if ((test_name != '' and test_name == dtest['name']) or
                        ((test_name == '' or test_name is None) and (targetname in dtest['name'] or dtest['name'] in targetname))):

                    testid = dtest['id']

                    csapi.WriteMessageToReservationOutput(resid,
                                                          'Located test %s matching resource %s; getting test details...' % (
                                                          testid, targetname))
                    jtest = requests.get('https://a.blazemeter.com/api/latest/tests/%s' % testid,
                                         auth=(self.key, self.secret)).text

                    # csapi.WriteMessageToReservationOutput(resid, 'Details: %s' % jtest)

                    dtest = json.loads(jtest)
                    dtest['result']['configuration']['plugins']['http']['pages'][0]['url'] = targetname2url[targetname]
                    dtest2 = {
                        'name': dtest['result']['name'],
                        'configuration': dtest['result']['configuration'],
                    }
                    #csapi.SetResourceLiveStatus(targetname, 'Error', 'Server overloaded')

                    csapi.WriteMessageToReservationOutput(resid, 'Target: %s' % targetname)

                    # for b in a2b[targetname]:
                    #     if b != resource.name and not b.endswith('/' + resource.name):
                    #         csapi.SetResourceLiveStatus(b, 'Error', 'Server overloaded')

                    csapi.WriteMessageToReservationOutput(resid, 'Writing URL %s to test %s' % (
                    targetname2url[targetname], testid))
                    rp = requests.put('https://a.blazemeter.com/api/latest/tests/%s' % testid,
                                      auth=(self.key, self.secret),
                                      headers={'Content-Type': 'application/json'},
                                      data=json.dumps(dtest2))

                    jlaunch = requests.post('https://a.blazemeter.com/api/latest/tests/%s/start' % testid,
                                            auth=(self.key, self.secret)).text
                    dlaunch = json.loads(jlaunch)
                    sessionid = dlaunch['result']['sessionsId'][0]
                    sessionid2targetname[sessionid] = targetname

                    jstat = requests.get('https://a.blazemeter.com/api/latest/sessions/%s' % sessionid,
                                         auth=(self.key, self.secret)).text
                    dstat = json.loads(jstat)
                    csapi.WriteMessageToReservationOutput(resid, 'BlazeMeter session %s status 2: %s' % (
                    sessionid, dstat['result']['status']))

                    projectid = dstat['result']['projectId']
                    masterid = dstat['result']['masterId']
                    juser = requests.get('https://a.blazemeter.com/api/latest/user', auth=(self.key, self.secret)).text
                    duser = json.loads(juser)
                    accountid = duser['defaultProject']['accountId']
                    workspaceid = duser['defaultProject']['workspaceId']

                    jtoken = requests.post('https://a.blazemeter.com/api/v4/masters/%s/public-token' % masterid,
                                           auth=(self.key, self.secret)).text
                    dtoken = json.loads(jtoken)
                    publictoken = dtoken['result']['publicToken']

                    reporturl = 'https://a.blazemeter.com/app/?public-token=%s#/accounts/%s/workspaces/%s/projects/%s/masters/%s/summary' % (
                    publictoken, accountid, workspaceid, projectid, masterid)
                    csapi.WriteMessageToReservationOutput(resid, 'Report: %s' % reporturl)
                    csapi.WriteMessageToReservationOutput(resid,
                                                          'SessionId: %s, TargetName: %s' % (sessionid, targetname))
                    executed += 1

        csapi.WriteMessageToReservationOutput(resid, 'Executed %d tests' % executed)
        pass

    def wait_for_test(self, context, session_id, target_name):
        """
        An example function that accepts two user parameters
        :param ResourceCommandContext context: the context the command runs on
        :param str session_id: the test session id to wait for
        :param str target_name: the target app/resource name
        """
        self._get_key_and_secrect(context)
        csapi = self._get_api_session(context)
        resid = context.reservation.reservation_id

        reporturl = ''
        for _ in range(60):
            jstat = requests.get('https://a.blazemeter.com/api/latest/sessions/%s' % session_id, auth=(self.key, self.secret)).text
            dstat = json.loads(jstat)
            csapi.WriteMessageToReservationOutput(resid, 'BlazeMeter session %s status: %s' % (
            session_id, dstat['result']['status']))
            if dstat['result']['status'] in ['ENDED']:
                projectid = dstat['result']['projectId']
                masterid = dstat['result']['masterId']
                juser = requests.get('https://a.blazemeter.com/api/latest/user', auth=(self.key, self.secret)).text
                duser = json.loads(juser)
                accountid = duser['defaultProject']['accountId']
                workspaceid = duser['defaultProject']['workspaceId']

                jtoken = requests.post('https://a.blazemeter.com/api/v4/masters/%s/public-token' % masterid,
                                       auth=(self.key, self.secret)).text
                dtoken = json.loads(jtoken)
                publictoken = dtoken['result']['publicToken']

                csapi.SetResourceLiveStatus(target_name, 'Online', '')

                break
            sleep(5)

        pass
        
    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    def _get_api_session(self, context):
        return CloudShellAPISession(host=context.connectivity.server_address,
                                    token_id=context.connectivity.admin_auth_token,
                                    domain=context.reservation.domain)
