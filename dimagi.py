#!/usr/bin/env python

# ========= [ Imports ]
from optparse import OptionParser
from os import path
from time import sleep
from re import compile as recompile
from sys import argv
import paramiko
import logging
import warnings
warnings.filterwarnings("ignore")


# ========= [ Customs ]

#Paramiko logs
paramiko.util.log_to_file("filename.log")

# ========= [ Statics ]

# deeeeeeee BUG
debug = True


# Regex pattern for IP addresses (simple pattern)
ipRe = recompile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")


class tunnel():
    """
    SSH tunnel object. Instantiated object is passed to a command module, and
    the command module operates on that specific tunnel. (Facilitates quicker
    command handling as well as the possibility of multithreading.)
    """

    def __init__ (self, mgmtip, name=False, user="devops", password="devops", inputPort=22):
        self.mgmt = mgmtip
        self.port = inputPort
        self.user = user
        self.password = password

        # Logging
        logging.raiseExceptions = True

        # Naming
        if name:
            self.name = name
        else:
            self.name = mgmtip
        if debug:
            print "DEBUG> Tunnel is created => " + self.name 

        # Establish the SSH tunnel as part of initialization
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
        self.ssh.connect(
            mgmtip,
            username=self.user,
            password=self.password,
            port = self.port
        )


    def ssh_command(self, run_command , livestream=True):
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(run_command)   
        return [ssh_stdout.readlines() , ssh_stderr.readlines()]


    def teardown(self):
        self.ssh.close()


    def git_deploy (self):
        """
        GIT to update the application source
        """

        if not opts.branch:
            BRANCH = 'master'
        else:
            BRANCH = opts.branch

        # check if the directory exists
        dir_present = link.ssh_command('test -d /home/devops/todo ; echo $?')
        if '0' not in dir_present[0][0].encode('ascii', 'ignore'):
            print "/home/devops/todo does not exist"
            exit(0)

        # Push current build value in a install.log file
        print "-> Push current build value in a install.log"
        cur_build = link.ssh_command('cd /home/devops/todo ; git rev-parse --verify --short HEAD >> /home/devops/install.log')       

        # Get in the directory and git pull.
        print "-> Git Fetch"
        fetch = link.ssh_command('cd /home/devops/todo ; git fetch ')
        if debug:
            print "DEBUG> :" 
            print fetch
    
        # Checkout Branch
        print "-> Git Checkout"
        checkout_call = "cd /home/devops/todo ; git checkout {0}".format(BRANCH)
        checkout = link.ssh_command(checkout_call)
        if debug:
            print "DEBUG> :" 
            print checkout

        #Pull
        print "-> Git Pull"
        pull = link.ssh_command("cd /home/devops/todo ; git pull")
        if debug:
            print "DEBUG> :" 
            print pull
    

    def git_rollback (self):
        """
        GIT rollback to a previously working version
        """

 



    def setup(self):
        """
        Setup virtual ENV and install requirements
        """
        # Activate the python virtualenv
        print "-> Activate the python virtualenv"
        env = link.ssh_command('cd /home/devops/todo ; source env/bin/activate')
        if debug:
            print "DEBUG> :" 
            print env

        sleep(2)
        # Update python virtual environment
        print "-> Update python virtual environment"
        update = link.ssh_command('cd /home/devops/todo ; pip install -U -r requirements.txt')
        if debug:
            print "DEBUG> :" 
            print update
 
        sleep(2)
        # database migration
        print "-> database migration"
        db_migration = link.ssh_command('cd /home/devops/todo ; source ~/.bash_profile ; flask db upgrade')
        if debug:
            print "DEBUG> :" 
            print db_migration

        sleep(2)
        # Stop the application process
        print "-> Stop the application process"
        kill = link.ssh_command('cd /home/devops/todo ; source ~/.bash_profile ; pkill -u devops flask')
        if debug:
            print "DEBUG> :" 
            print kill

        sleep(2)
        # Start the application process
        print "-> Start the application process"
        start = link.ssh_command('cd /home/devops/todo ; source ~/.bash_profile ; nohup flask run -h 0.0.0.0 >/dev/null 2>&1 &')
        if debug:
            print "DEBUG> :" 
            print start


def cli ():
    """
    Parse CLI options.
    """

    cli = OptionParser(usage="Usage: %prog [options]")
    cli.add_option("--ip", dest="ip", help="Target MGMT IP")
    cli.add_option("--branch", dest="branch", help="Target Branch")

    # Harvest
    (opts, args) = cli.parse_args()

    # Filter required variables
    if len(argv) < 2:
        cli.print_help()
        exit()

    return (opts, args)



if __name__ == "__main__":
    # Grab that CLI
    (opts, args) = cli()
    IP = opts.ip

    # Make sure we got an IP address and not a ukulele or something
    if not ipRe.match(IP):
        print "Fatal: IP lookup returned non-IP value '" + IP + "'"
        exit(1)


    link = tunnel(IP)

    # Test the link
    linktest = link.ssh_command("uname -a")
    if "Ubuntu" not in linktest[0][0]:
        print "Fatal: Error during SSH connection validation (`uname -a`) to " + IP + "."
        exit(1)

    link.git_deploy()

    link.setup()
    # Close the ssh session
    link.teardown()
