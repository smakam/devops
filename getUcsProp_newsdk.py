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
# Usage: getFaults.py [options]
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
from UcsSdk.MoMeta.EquipmentChassis import EquipmentChassis

def loadAllMo(): 
	import os 
	import UcsSdk 
	exports = [] 
	globals_, locals_ = globals(), locals() 
	package_path = os.path.dirname(UcsSdk.__file__) 
	package_name = os.path.basename(package_path) 
	mometa_path = os.path.join(package_path,'MoMeta') 
	for filename in os.listdir(mometa_path): 
		modulename, ext = os.path.splitext(filename) 
		if not modulename.endswith('Meta') and ext in ('.py') and modulename != '__init__': 
			subpackage = '{}.{}'.format(package_name+".MoMeta", modulename) 
			module = __import__(subpackage, globals_, locals_, [modulename]) 
			modict = module.__dict__ 
			names = [name for name in modict if name[0] != '_'] 
			exports.extend(names) 
			globals_.update((name, modict[name]) for name in names)

def getpassword(prompt):
    if platform.system() == "Linux":
        return getpass.unix_getpass(prompt=prompt)
    elif platform.system() == "Windows" or platform.system() == "Microsoft":
        return getpass.win_getpass(prompt=prompt)
    else:
        return getpass.getpass(prompt=prompt)

# Get Ethernet mode
def getEthernetMode(handle):
    molist = handle.GetManagedObject(None, None, {OrgOrg.DN:"fabric/lan"})
    if (molist != None):
          for mo in molist:
               for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                    if(str(prop) == "Mode"):
                        ethmode =  mo.getattr(prop)
    return ethmode
    
# Get software version
def getSwVersion(handle):
    molist = handle.GetManagedObject(None, None, {OrgOrg.DN:"sys/mgmt/fw-system"})
    if (molist != None):
        for mo in molist:
            for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                if(str(prop) == "Version"):
                    version =  mo.getattr(prop)
    return version

# Get HA mode
def getHaMode(handle):
    molist = handle.GetManagedObject(None, None, {OrgOrg.DN:"sys"})
    if (molist != None):
        for mo in molist:
            for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                if(str(prop) == "Mode"):
                    hamode =  mo.getattr(prop)
    return hamode

# Get FI model(for cluster 2 models will be returned)
def getFiModel(handle):
    fi_model = {}
    molist = handle.GetManagedObject(None, None, {OrgOrg.DN:"sys/switch-A"})
    if (molist != None):
        for mo in molist:
            for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                if(str(prop) == "Model"):
                    fi_model[0] =  mo.getattr(prop)
    
    # Get FI Model for B if its cluster
    if (hamode == 'cluster'):
        molist = handle.GetManagedObject(None, None, {OrgOrg.DN:"sys/switch-B"})
        if (molist != None):
            for mo in molist:
                for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                    if(str(prop) == "Model"):
                        fi_model[1] =  mo.getattr(prop)
                        
    return fi_model

# Get Blade chassis model details
def getBladeDetail(handle):
    chassis_model = []
    server_model = []
    
    molist = handle.GetManagedObject(None, EquipmentChassis.ClassId())
    chassis_cnt = 0
    if (molist != None):
        for mo in molist:
            chassis_cnt = chassis_cnt + 1
            for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                if(str(prop) == "Model"):
                    chassis_model.append(mo.getattr(prop))
            
            molist1 = handle.GetManagedObject(None, ComputeBlade.ClassId())
            server_cnt = 0
            if (molist1 != None):
                for mo1 in molist1:
                    server_cnt = server_cnt + 1
                    for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo1.propMoMeta.name):
                        if(str(prop) == "Model"):
                            server_model.append(mo1.getattr(prop))
                            
    return chassis_model, server_model

# Get Rack server model details
def getRackDetail(handle):
    rack_model = []
    
    molist = handle.GetManagedObject(None, ComputeRackUnit.ClassId())
    rack_cnt = 0
    if (molist != None):
        for mo in molist:
            rack_cnt = rack_cnt + 1
            for prop in UcsUtils.GetUcsPropertyMetaAttributeList(mo.propMoMeta.name):
                if(str(prop) == "Model"):
                    rack_model.append(mo.getattr(prop))

    return rack_model

if __name__ == "__main__":
    loadAllMo()
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
        ethmode = getEthernetMode(handle)
        
        # Get software version
        version = getSwVersion(handle)

        # Get cluster/standalone
        hamode = getHaMode(handle)
        
        # Get FI model for A
        model = getFiModel(handle)

        # Get chassis and servers
        chassismodel, servermodel = getBladeDetail(handle)
                                
        # Get rack servers
        rackmodel = getRackDetail(handle)
        
        print 'hamode', hamode, 'ethmode', ethmode, 'version', version

        print 'fia-model', model[0]
        
        if (hamode == 'cluster'):
            print 'fib-model', model[1]
        
        print "Blade chassis:"
        i = 0
        while (i < len(chassismodel)):
            print chassismodel[i]
            i = i + 1
            
        print "Blade servers:"
        i = 0
        while (i < len(servermodel)):
            print servermodel[i]
            i = i + 1
        
        print "Rack servers:"
        i = 0
        while (i < len(rackmodel)):
            print rackmodel[i]
            i = i + 1
        
        handle.Logout()

    except Exception, err:
        handle.Logout()
        print "Exception:", str(err)
        import traceback, sys
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60

