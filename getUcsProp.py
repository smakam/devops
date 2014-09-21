#!/usr/bin/python

# Copyright 2013 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script retrieve all the UCS Manager Faults.
# Usage: getUcsInfo.py [options]
#
# Options:
# -h, --help            show this help message and exit
# -i IP, --ip=IP        [Mandatory] UCSM IP Address
# -u USERNAME, --username=USERNAME
#                       [Mandatory] Account Username for UCSM Login
# -p PASSWORD, --password=PASSWORD
#                       [Mandatory] Account Password for UCSM Login
#

import getpass
import optparse
from UcsSdk import *

def getpassword(prompt):
    if platform.system() == "Linux":
        return getpass.unix_getpass(prompt=prompt)
    elif platform.system() == "Windows" or platform.system() == "Microsoft":
        return getpass.win_getpass(prompt=prompt)
    else:
        return getpass.getpass(prompt=prompt)

if __name__ == "__main__":
    handle = UcsHandle()
    try:
        parser = optparse.OptionParser()
        parser.add_option('-i', '--ip',dest="ip",
                          help="[Mandatory] UCSM IP Address")
        parser.add_option('-u', '--username',dest="userName",
                          help="[Mandatory] Account Username for UCSM Login")
        parser.add_option('-p', '--password',dest="password",
                          help="[Mandatory] Account Password for UCSM Login")

        (options, args) = parser.parse_args()
        
        if not options.ip:
            parser.print_help()
            parser.error("Provide UCSM IP Address")
        if not options.userName:
            parser.print_help()
            parser.error("Provide UCSM UserName")
        if not options.password:
            options.password=getpassword("UCSM Password:")

        handle.Login(options.ip,options.userName,options.password)
        # Get Ethernet Mode
        molist = handle.GetManagedObject(None, None, {OrgOrg.DN:"fabric/lan"})
        if (molist != None):
            for mo in molist:
                for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                    if(str(prop) == "Mode"):
                        ethmode =  mo.getattr(prop)
        
        # Get software version
        molist = handle.GetManagedObject(None, None, {OrgOrg.DN:"sys/mgmt/fw-system"})
        if (molist != None):
            for mo in molist:
                for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                    if(str(prop) == "Version"):
                        version =  mo.getattr(prop)
        
        # Get cluster/standalone
        molist = handle.GetManagedObject(None, None, {OrgOrg.DN:"sys"})
        if (molist != None):
            for mo in molist:
                for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                    if(str(prop) == "Mode"):
                        hamode =  mo.getattr(prop)
        
        # Get FI model for A
        molist = handle.GetManagedObject(None, None, {OrgOrg.DN:"sys/switch-A"})
        if (molist != None):
            for mo in molist:
                for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                    if(str(prop) == "Model"):
                        fia_model =  mo.getattr(prop)
        
        # Get FI Model for B if its cluster
        if (hamode == 'cluster'):
            molist = handle.GetManagedObject(None, None, {OrgOrg.DN:"sys/switch-B"})
            if (molist != None):
                for mo in molist:
                    for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                        if(str(prop) == "Model"):
                            fib_model =  mo.getattr(prop)
                                                                            
        print 'hamode', hamode, 'ethmode', ethmode, 'version', version
        print 'fia-model', fia_model
        
        if (hamode == 'cluster'):
            print 'fib-model', fib_model

        # Get chassis and servers
        molist = handle.GetManagedObject(None, EquipmentChassis.ClassId())
        chassis_cnt = 0
        if (molist != None):
            for mo in molist:
                chassis_cnt = chassis_cnt + 1
                for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                    if(str(prop) == "Model"):
                        print 'chassis', chassis_cnt, 'model', mo.getattr(prop)
                
                molist1 = handle.GetManagedObject(None, ComputeBlade.ClassId())
                server_cnt = 0
                if (molist1 != None):
                    for mo1 in molist1:
                        server_cnt = server_cnt + 1
                        for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo1.propMoMeta.name):
                            if(str(prop) == "Model"):
                                print 'server', server_cnt, 'model', mo1.getattr(prop)   
                                
        # Get rack servers
        molist = handle.GetManagedObject(None, ComputeRackUnit.ClassId())
        rack_cnt = 0
        if (molist != None):
            for mo in molist:
                rack_cnt = rack_cnt + 1
                for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                    if(str(prop) == "Model"):
                        print 'rack', rack_cnt, 'model', mo.getattr(prop)
                        
        handle.Logout()

    except Exception, err:
        handle.Logout()
        print "Exception:", str(err)
        import traceback, sys
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60

