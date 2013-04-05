#/usr/bin/python
#
#remote automation module using pexpect(pxssh)
#
#Copyright (c) 2012, Telenav, Inc. All rights reserved. See accompanying LICESE
#
# Author: Andreww
# Date: 01-JAN-2013
#
# @ v2.0.4 removed pw_used after a sucessfull login and instead set pswd to 
#    shorten re-login and free some memory.
# @ v2.0.3 added __repr__ amd blocked __str__ from pxepect
# @ v2.0.2 added introspection hooks to make objects pretty 
# @ v2.0.1 fixed bug with having a private key configured in users shell, 
#    but not configured in remote causing failed password logins 
# @ v2.0.0 improved support to run stacks of commands, including instance of Cmd 
# @ v1.1.1 added timeout to run() and getoutput()
# @ v1.1.1 improved error prevention in run() 


__version__ = '2.0.4'

import pexpect, re, random
from getpass import getpass
from pxssh import *

INFO = 1
VERBOSE = 2
DB_CALL = 3

class remote(pxssh):
    def __init__(self, host, user, pswd, key=None, timeout=5, interact=False, 
                 debug=False, maxread=2000, searchwindowsize=None, 
                 logfile=None, cwd=None, env=None):

        self.host = host
        self.user = user
        pxssh.__init__(self, timeout=30, maxread=maxread, 
                       searchwindowsize=searchwindowsize, logfile=logfile, 
                       cwd=cwd, env=env)
        self.__data = {'host': host,
                       'user': user,
                       'pswd': pswd,
                       'timeout': timeout,
                       'interact': interact,
                       #These are for pxssh.__init__
                       'maxread': maxread, 
                       'searchwindowsize': searchwindowsize, 
                       'logfile': logfile, 
                       'cwd': cwd, 
                       'env': env,
                       'key': key,
                       }
        self.__output = {}
        self.DEBUG = debug
    def __repr__(self):
        return u"<%s@%s [A:%s]>" %(self.user, self.host, self.isalive())
    #pStr = __str__
    __str__ = __repr__
    __unicode__ = __repr__
    
    def __eprint(self, st, level=1):
        # 0 = OFF
        # 1 = INFO
        # 2 = VERBOSE
        # 3 = DB_CALL
        if (self.DEBUG >= level): print st
        return
    
    def __raiseNotAlive(self):
        if (not self.isalive()):
            self.login()
            if (not self.isalive()):
                raise Exception, "Not connected / alive / unable to connect"
        
    def rem_passwd(self, newpswd, username=None, oldpswd=None):
        self.__raiseNotAlive()
        user = username or self.__data['user']
        pw  = newpswd
        oldpw = oldpswd or self.__data['pswd']
        pw_re = re.compile("(.*)assword:")
        try:
            self.__eprint("sh_passwd:: changing passwd for %s" % (user))
            self.sendline("passwd %s" %(user))
            self.expect(pw_re)
            self.sendline(pw)
            self.expect(pw_re)
            self.sendline(pw)
            self.prompt()
            return True
        except (pexpect.TIMEOUT, pexpect.EOF), e:
            self.__eprint("sh_passwd::(TIMEOUT,EOF) %s" %(e))
        return False
        
    def gethostname(self):
        cmd = "echo $HOSTNAME"
        out = self.run(cmd)[0].strip()
        self.__eprint("sh_getHostName:: %s" %(out), VERBOSE)
        return out

    def getrhel(self):
        cmd = "cat /etc/redhat-release"
        out = self.run(cmd)[0].strip()
        self.__eprint("sh_getrhel:: %s" %(out),VERBOSE)
        return out
    
    def getuname(self):
        cmd = "uname -a"
        out = self.run(cmd)[0].strip()
        self.__eprint("sh_getuname:: %s" %(out),VERBOSE)
        return out
    
    def getoutput(self, cmd, timeout=5):
        self.__raiseNotAlive()
        rand = random.random()
        try:
            #ses.sendline('\r')
            #ses.prompt()
            self.sendline(cmd + " #%s" %(rand))
            self.expect("%s\r\n" %(rand))
            self.prompt(timeout=timeout)
            return self.before
        except (pexpect.TIMEOUT, pexpect.EOF), e:
            return None
    
    #New in 2.0, under development
    def do(self, cmds, timeout=5):
        for cmd in cmds:
            pass
    
    def run(self,cmd,timeout=5):
        output = self.getoutput(cmd,timeout)
        if (not output):
            ret = None
        else:
            try:
                ret = int(self.getoutput("echo $?", timeout).strip())
            except ValueError:
                ret = None
        return output,ret
    
    def logout(self):
        if (self.isalive()):
            return pxssh.logout(self)
        else: 
            return False
    
    #close = logout
    
    def remote_login(self, host=None, user=None, pswd=None, timeout=None, 
                    interact=None, key=None):
        host = host or self.__data['host']
        user = user or self.__data['user']
        passwd = pswd or self.__data['pswd']
        timeout = timeout or self.__data['timeout']
        intr = interact or self.__data['interact']
        key = key or self.__data['key']
        if not key:
            self.SSH_OPTS=""
        errstr=''
        times=0
        max_times = 3 #how may attempts (Other than passwd failed)
        
        if (type(passwd) == list):
            pw_array = True
            passwd = list(passwd) # list(...) makes a shallow copy
            if (pw_array and len(passwd)):
                    pw = passwd.pop(0)
        else:
            pw_array = False
            pw = str(passwd)  # shallow copy again
            pw_times = 0
    
        if (type(timeout) == list):
            ttl_array = True
            timeout = list(timeout) # shallow copy again
            if (ttl_array and len(timeout)):
                ttl = timeout.pop(0)
        else:
            ttl = timeout
            ttl_array = False
                    
        while (times < max_times):
            #We need to re-init before/after each attempt or we will 
            #get a "pid member should be None" error
            pxssh.__init__(self, maxread=self.__data['maxread'], 
                       searchwindowsize=self.__data['searchwindowsize'], 
                       logfile=self.__data['logfile'], 
                       cwd=self.__data['cwd'], env=self.__data['env'])
            if not key:
                self.force_password=True
            self.__eprint("pxssh_login:: attempt %i/%i" %(times,max_times),1)
            try:
                if (pxssh.login(self, host, user, pw, login_timeout=ttl)):
                    #store sucessfull password, also if we have to login again,
                    # we don't dont have to go through most of this code again.
                    self.__data['pswd'] = pw
                    #success dont need to do anything else
                    return True 
            except ExceptionPxssh, err:
                if (str(err) == "password refused"):
                    if (pw_array and len(passwd)):
                        pw = passwd.pop(0)
                        self.__eprint("remote_login:: using next passwd (%i) remaining" %(len(passwd)),INFO)
                        continue
                    elif (pw_array and not(len(passwd))):
                        #we dont want to be stuck here
                        errstr += "remote_login:: no valid passwd remains +"
                        break
                    elif (intr and pw_times < max_times):
                        pw = getpass("Bad passwd [%i/%i] enter new passwd for %s: " %(pw_times,max_times,user))
                        pw_times += 1
                        continue
                    else:
                        errstr += "remote_login:: No valid passwd +"
                        break
                elif str(err) >= "could not set shell prompt":
                    #This is an error from pxssh (pexcept) due to false positive 
                    # in pxssh.sync_original_prompt()
                    errstr += "remote_login:: trap false positive ((could not set shell prompt))"
                    break
                else:
                    print "Un-processed error condition '%s' please report" %(str(err))
                    errstr += "remote_login::%s" %(str(err))
    
            except pexpect.TIMEOUT, err:
                self.__eprint("Unexpected TIMEOUT connecting",INFO)
                errstr += "pxssh_login::TIMEOUT +"
                
            except pexpect.EOF, err:
                self.__eprint("Unexpected EOF connecting",INFO)
                errstr += "pxss_login::Cant conenct to host / EOF +"
    
            #we don't want to be here forever
            times += 1 
    
    
            if (ttl_array and len(timeout)):
                ttl = timeout.pop(0)
        if (errstr):
            if (self.__output.has_key('exit_status')):
                self.__output['exit_status'] += errstr
            else:
                self.__output['exit_status'] = errstr
            return False
    
        return False

    login = remote_login

    def interact(self):
        print "\n!!                                                               !!"
        print "!!                       !!  NOTICE  !!                          !!"
        print "!!                                                               !!"
        print "!!            About to attempt to interact with spawn            !!"
        print "!! You may need to pass a couple of line feeds to get the prompt !!"
        print "!! When you are done pass ^] to close the interact. Other methods!!"
        print "!! will cause pre-mature termination of the spawned process.     !!"
        print "!!                                                               !!"
        print "!!                                                               !!"
        try:
            pxssh.interact(self)
            return True
        except (ExceptionPxssh, OSError), e:
            self.__eprint("failure closing interact: %s" % (e))
            return False            
            

if __name__ == '__main__':
    pass
