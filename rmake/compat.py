#
# Copyright (c) 2006 rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/cpl.php.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#
"""
Tracks compatibility with versions of integrated software for backwards 
compatibility checks.
"""
from conary import constants

class ConaryVersion(object):
    def __init__(self):
        self.conaryVersion = [int(x) for x in constants.version.split('.')]
        self.majorVersion = self.conaryVersion[0:2]
        self.minorVersion = self.conaryVersion[2]
        self.isOneOne = self.majorVersion == (1,1)
    
    def supportsCloneCallback(self):
        # support added in 1.0.30 and 1.1.3
        return self.checkVersion(30, 3)

    def checkVersion(self, oneZeroVersion, oneOneVersion):
        if self.majorVersion == [1,0]:
            if oneZeroVersion is None:
                return False
            return self.minorVersion < oneZeroVersion
        elif self.majorVersion == [1,1]:
            if oneOneVersion is None:
                return False
            return self.minorVersion < oneOneVersion