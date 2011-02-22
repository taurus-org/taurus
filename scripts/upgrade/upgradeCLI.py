#!/usr/bin/env python

import sys, time
import PyTango

from upgrade_utils import *

def upgrade(serv, old_vers, new_vers):
    u_kcls = get_suitable_upgrade(old_vers, new_vers)
    u_obj = u_kcls()
    db = PyTango.Database()
    print
    for msg, perc in u_obj.upgrade(db, serv, old_vers, new_vers):
        msg = "\033[1F\033[2K%-70s" % msg
        msg = "%s [ %03d%s ]" % (msg, perc, '%')
        print msg
        time.sleep(0.1)
    
def main():
    
    serv = ""
    vers = "0.0.0"

    if len(sys.argv) > 1: serv = sys.argv[1]
    if len(sys.argv) > 2: vers = sys.argv[2]

    pool_serv_list = get_server_list()
    
    while not serv in pool_serv_list:
        print_list(pool_serv_list)
        serv = raw_input("Which instance you want to upgrade? ")
    
    old_vers = get_pool_server_version(serv)

    print "Current version of %s is %s" % (serv, old_vers)
    
    possible_upgrades = get_possible_upgrades(serv)
    
    if not possible_upgrades:
        print "Could not find a suitable upgrade plugin for version %s.\nUpgrade FAILED" % old_vers
        return

    while not get_suitable_upgrade(old_vers, vers):
        print_list(possible_upgrades)
        vers = raw_input("To which version you want to upgrade %s (bigger than %s)? " % (serv, old_vers))
    
    upgrade(serv, old_vers, vers)
    
if __name__ == "__main__":
    main()