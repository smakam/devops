# Import the onePK Libraries  
from onep.element.NetworkElement import NetworkElement  
from onep.element.SessionConfig import SessionConfig
from onep.core.util import tlspinning  
from onep.interfaces import InterfaceFilter

import optparse
import sys
  
# This program connects to Cisco ONEPK device using TLS pinning option and displays information 
# about the Network element. Reference from https://communities.cisco.com/thread/44820

# TLS Connection (This is the TLS Pinning Handler)  
class PinningHandler(tlspinning.TLSUnverifiedElementHandler):  
    def __init__(self, pinning_file):  
        self.pinning_file = pinning_file  
    def handle_verify(self, host, hashtype, finger_print, changed):  
        return tlspinning.DecisionType.ACCEPT_ONCE  

if __name__ == '__main__':  
    hostname = None
    username = None
    password = None
    
    parser = optparse.OptionParser()
    parser.add_option('-i', '--ip',dest="ip",
                          help="[Mandatory] IP Address")
    parser.add_option('-u', '--username',dest="userName",
                          help="[Mandatory] Account Username for Login")
    parser.add_option('-p', '--password',dest="password",
                          help="[Mandatory] Account Password for Login")

    (options, args) = parser.parse_args()

    if not options.ip:
        parser.print_help()
        parser.error("Provide IP Address")
    if not options.userName:
        parser.print_help()
        parser.error("Provide UserName")
    if not options.password:
        options.password=getpassword("Password:")

        
    # Setup a connection config with TLS pinning handler
    config = SessionConfig(None)  
    config.set_tls_pinning('', PinningHandler(''))  
    config.transportMode = SessionConfig.SessionTransportMode.TLS  
     
    # Connection to my onePK enabled Network Element  
    ne = NetworkElement(options.ip, 'App_Name')  
    ne.connect(options.userName, options.password, config)  
     
    # Print the information of the Network Element  
    print ne
     
    # Finally have the application disconnect from the Network Element  
    ne.disconnect()
