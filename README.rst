====
remote
====


License
====

Copyright (c) 2012 Telenav, Inc. All rights reserved.

This software is licensed under a BSD Style license, see accompanying LICENSE file. 



Synopsis
====

Remote provides a wrapper around pxssh from pexpect to increase the robustness 
and scripting power of the expect interface. remote is maintained to be able 
to programmatically and precisely work with remote systems over the ssh 
protocol. remote deals with this several ways. The login procedure has been 
beefed up allowing for graceful error handling, timeout, retry, as well as 
multiple KeyboardInteractive passwords or the use ssh-key's with or with-out 
pass-phrases. Additional code is written around the execution of commands or 
statements inside a cli. Most of the time you wont need to write expect clauses 
or deal with timeouts or the like, however if for whichever reason you want or 
need these interfaces they are still there as we carry a fully implemented
subclass of pxssh which in turn is a child of pexpect.   

Security Note
====

I'm not going to beat around the bush or lecture (too much) about credential 
security but there are some things we need to set expectations about.

1. **Password data is stored as-is, currently that's plain text.** Yes, that's 
   right, if you put your password in the object it does **NOTHING** to protect it.

2. Creating a centralized process that can go login to and random system in 
   your network / whatever is necessary when managing systems in mass. However
   you must take steps to protect said process from nosy and/or generally
   bad people. If you leave the keys lying around the will use them.

3. ssh-keys with out pass-phrases to every host on your network are effectively 
   as weak as writing your plain-text password in ~/passwords. Use passwords,
   pass-phrases and change your keys, passwords, pass-phrases frequently. It's 
   worth the effort.

Example Usage
----
Simple usage often looks like this::

    $ python -i

    >>> from remote import remote
    >>> con = remote("remote-host", "user", "password")
    >>> con.login()
    True
    >>> con.gethostname()
    'localhost.localdomain'
    >>>con.run("cat /some/file")
    ('cat: /some/file: No such file or directory\r\n', 1)

Advanced usage across a number of hosts::

    $ python -i
    
    >>> from remote import remote
    >>> from string import join
    >>> cons = []
    >>> for each in range(1,255) #Generate Host list and connections for each
    ...   hosts.append( remote(join(["192.168.0",each],'.'), "user", 
    ...     ['pass1', 'pass2', 'asdf', 'qwerty'], timeout=[15,5]))
    ...
    >>> for host in cons:  #Login each host
    ...   if not con.login():
    ...     cons.pop(cons.index(host)) #Remove nodes that failed to login
    ...
    >>> for host in cons:
    ...   host.gethostname()
    ...   con.close()
    ...
    host1
    host2
    host3
    [Truncated]
    host254
    >>>

Authentication
----

Authentication can be one of several methods 

1. Single string password::

    >>> con = remote("remote-host", "user", "password")

2. List of string passwords::

    >>> con = remote("remote-host", "user", ["password",'asdf', 'qwerty'])

3. ssh-key (with or with-out pass-phrase)::

    #If key is in your existing ssh environment settings
    >>> con = remote("remote-host", "user", None, Key=True)
    
    #Specify a key file 
    >>> con = remote("remote-host", "user", None, Key="~/.ssh/some_key")
    
    #Key has a pass-phrase
    >>> con = remote("remote-host", "user", "pass-phrase", Key="~/.ssh/some_key")

4. Actual KeyboardInteractive questions (using getpass)::
    
    >>> con = remote("remote-host", 'user', None, interact=True)
    >>> con.login()
    Bad passwd [0/3] enter new passwd for user:
    True
    
   
Timeouts
----

Sometimes timeout handling can be painful as such remote has two methods for 
handling this. 

During class init or the invocation of login, an array of 
timeouts can be passed. Then during the login process if a list of authentication 
methods are available, the login function will use the timeout values in the
order of the list. If an uneven number of credentials to timeout values are 
passed, then the last timeout value will be repeated for all remaining credentials.

During command run's the default timeout is 5 seconds, for commands that you 
expect to take longer, you can pass timeout=new_value  

Running commands
----

remote has a basic framework to capture command results. Because its scripting 
centric we also have default methods to capture return values. This is useful
when the shell response value is as important or even more so than the text result.

*Note: running one of the pre-packed commands or any other command that uses 
getoutput will call remote.login() if the instance isn't connected to a host.
It will raise an exception if it can't connect.*


There are some pre-packed commands

* rem_passwd(newpswd, username=None, oldpswd=None)
  run's passwd, if username or old passwd are none, then the params used during
  login will be used

* gethostname()
  returns the value of $HOSTNAME
  
* getrhel()
  returns the value of /etc/redhat-release
  
* getuname()
  returns the value of uname

Aswell as raw command helpers

* getoutput(command,timeout=5)
  This is part of the meat and gravy, getouput will run a command and try to 
  store the output from it. It is implemented by issuing the command with a 
  commented (#) random string afterwards, this helps us to seek the end of
  our start line and helps prevent buffer issues.
  
* run(command,timeout=5)
  A wrapper around getoupt, it runs both getoutput(cmd) and then also runs 
  getoutput('echo $?') to secure the return value of cmd. This has been very
  useful in scripted interaction.  
