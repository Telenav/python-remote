#/usr/bin/python
#
#unit test module for remote.py
#
#Copyright (c) 2012, Telenav, Inc. All rights reserved. See accompanying LICESE
#
#
# Author: Andreww
# Version: 1.0.0

import remote
import unittest

class testRemote(unittest.TestCase):
    def setUp(self):
        self.con = remote.remote(host="localhost", user='', pswd='')
    
    def tearDown(self):
        self.con.logout()
    
    def testRemote1LoginSimple(self):
        msg = "Unable to login"
        self.assertTrue(self.con.login(), msg)
        
    def testRemote1LoginMultiPass(self):
        msg = "Unable to login with passwd array"
        self.assertTrue(self.con.login(pswd=['']), msg)
    
    def testRemote1LoginMultiTtl(self):
        msg = "Unable to login with timeout array"
        self.assertTrue(self.con.login(timeout=[15,10,5]), msg)
    
    def testRemote1LoginMultiPassTtl(self):
        msg = "Unable to login with passwd, timeout array"
        self.assertTrue(self.con.login(pswd=[''], timeout=[15,10,5]), msg)
    
    def testRemote1LoginHostDosntExist(self):
        msg = "Expected graceful failure of bad hostname"
        self.assertFalse(self.con.login(host="thishostdosntexist"), msg)
        
    def testRemote1LoginHostDosntExistMultiTtl(self):
        msg = "Expected graceful failure of bad hostname"
        self.assertFalse(self.con.login(host="thishostdosntexist", timeout=[5,4,3,2,1]), msg)
        
        
    def testRemote1LoginBadPassSimple(self):
        msg = "Expected graceful failure of bad password"
        pswd = "mamba"
        self.assertFalse(self.con.login(pswd=pswd), msg)
        
    def testRemote1LoginBadPassMulti(self):
        msg = "Expected graceful failure of bad password list"
        pswd = ["mamba", "tucow", "rose"]
        self.assertFalse(self.con.login(pswd=pswd), msg)

    def testRemote1LoginBadPassMultiTtl(self):
        msg = "Expected graceful failure of bas pswd with ttl array"
        pswd = ["mamba", "tucow", "rose"]
        self.assertFalse(self.con.login(pswd=pswd, timeout=[5,4,3,2,1]), msg)
                
    def testRemote5GetoutputPwd(self):
        cmd = "pwd"
        msg = "Unable to get pwd output"
        result = self.con.login()
        if (not result):
            raise Error, "Unable to login, test can't continue"
        self.assertTrue(self.con.getoutput(cmd), msg)
        
    def testRemote6Getrhel(self):
        msg = "Unable to stat /etc/redhat-release"
        result = self.con.login()
        if (not result):
            raise Error, "Unable to login, test can't continue"
        self.assertTrue(self.con.getrhel(), msg)
        
    def testRemote6Getuname(self):
        msg = "Unable to get output from uname -a"
        result = self.con.login()
        if (not result):
            raise Error, "Unable to login, test can't continue"
        self.assertTrue(self.con.getuname(), msg)
    
    def testRemote6run(self):
        msg = "Unable to get output and $?"
        cmd = "touch /tmp"
        result = self.con.login()
        if (not result):
            raise Error, "Unable to login, test can't continue"
        self.assertEqual(self.con.run(cmd), (self.con.getoutput(cmd),0), msg)
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testRemote))
    return suite

if __name__ == '__main__':
    
    #suiteFew = unittest.TestSuite()
    #suiteFew = suiteFew.addTest(testRemote("testRemoteLoginSimple"))
    #unittest.TextTestRunner(verbosity=2).run(suiteFew)
    results = unittest.TextTestRunner(verbosity=2).run(suite())