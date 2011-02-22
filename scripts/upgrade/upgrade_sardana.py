#!/usr/bin/env python

import sys, time
import PyTango

from upgrade_utils import *

if __name__ == "__main__":
    try:
        import PyQt4
        import upgradeGUI
        upgradeGUI.main()
    except Exception, e:
        import upgradeCLI
        upgradeCLI.main()

