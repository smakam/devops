import paramiko
import optparse
import time
import re
import xml.etree.cElementTree as ET
from StringIO import StringIO


def disable_paging(remote_conn):
    '''Disable paging on a Cisco router'''

    remote_conn.send("terminal length 0\n")
    time.sleep(1)

    # Clear the buffer on the screen
    output = remote_conn.recv(1000)

    return output


if __name__ == '__main__':

    parser = optparse.OptionParser()
    parser.add_option('-i', '--ip',dest="ip",
                          help="[Mandatory] NXOS IP Address")
    parser.add_option('-u', '--username',dest="userName",
                          help="[Mandatory] Account Username for NXOS Login")
    parser.add_option('-p', '--password',dest="password",
                          help="[Mandatory] Account Password for NXOS Login")

    (options, args) = parser.parse_args()
    
    if not options.ip:
        parser.print_help()
        parser.error("Provide NXOS IP Address")
    if not options.userName:
        parser.print_help()
        parser.error("Provide NXOS UserName")
    if not options.password:
        options.password=getpassword("NXOS Password:")
        
    # Create instance of SSHClient object
    remote_conn_pre = paramiko.SSHClient()

    # Automatically add untrusted hosts (make sure okay for security policy in your environment)
    remote_conn_pre.set_missing_host_key_policy(
         paramiko.AutoAddPolicy())

    # initiate SSH connection
    remote_conn_pre.connect(options.ip, username=options.userName, password=options.password)
    print "--- SSH connection established to %s ---" % options.ip

    # Use invoke_shell to establish an 'interactive session'
    remote_conn = remote_conn_pre.invoke_shell()
    print "Interactive SSH session established"

    # Strip the initial router prompt
    output = remote_conn.recv(1000)

    # See what we have
    #print output

    # Turn off paging
    disable_paging(remote_conn)

    # Now let's try to send the router a command
    remote_conn.send("\n")

    # Get output in xml format
    remote_conn.send("show int brief | xml \n")

    # Wait for the command to complete
    time.sleep(2)
    
    output = remote_conn.recv(50000)

    # See what we have
    #print output

    # Parse the output to get only relevant XML section
    output1 = re.findall("\<\?xml.*reply\>", output, re.DOTALL)

    # Strip namespaces
    it = ET.iterparse(StringIO(output1[0]))
    for _, el in it:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
    root = it.root

    # See what we have
##    for elem in root.iter():
##      print elem.tag, elem.text

    # Find interfaces in up state
    print "--- INTERFACES that are UP --- "
    for elem in root.iter('ROW_interface'):
        intf_name = elem.find('interface').text
        intf_state = elem.find('state').text
        if (intf_state == "up"):
            print intf_name


