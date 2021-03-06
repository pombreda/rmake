#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""
    Failure reasons for rMake jobs.

    Freezable failure reasons with arbitrary data.

    NOTE: to make a new failure reason available it must be added to the 
    list at the bottom of this page.
"""
from conary.conaryclient import cmdline
from conary import versions
from conary.deps.deps import ThawFlavor

from rmake.lib import apiutils


FAILURE_REASON_FAILED         = 0
FAILURE_REASON_BUILD_FAILED   = 1
FAILURE_REASON_BUILDREQ       = 2
FAILURE_REASON_DEP            = 3
FAILURE_REASON_CHROOT         = 4 # installation error
FAILURE_REASON_LOAD           = 5 # loadrecipe error
FAILURE_REASON_INTERNAL       = 6 # error in rmake proper
FAILURE_REASON_STOPPED    = 7 # stop request
FAILURE_REASON_COMMAND_FAILED = 8

# FIXME: this should use streamSets for the data.

class FailureReason(object):
    tag = FAILURE_REASON_FAILED
    def __init__(self, data=''):
        self.data = data

    def getData(self):
        return self.data

    def getShortError(self):
        return str(self)

    def getReason(self):
        return self.tag

    def hasTraceback(self):
        return False

    def __eq__(self, other):
        if other is None:
            return False
        return (self.tag == other.tag) and (self.data == other.data)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.data)

    def __str__(self):
        return str(self.data)

    def __freeze__(self):
        return (self.tag, self._freezeData())

    def _freezeData(self):
        return self.data

    @classmethod
    def _thawData(class_, data):
        return data

class FailureWithException(FailureReason):

    def __init__(self, error='', traceback=''):
        if isinstance(error, (list, tuple)):
            assert(isinstance(error[0], str))
            FailureReason.__init__(self, list(error))
        else:
            assert(isinstance(error, str))
            FailureReason.__init__(self, [error, traceback])

    def getShortError(self):
        return self.data[0]

    def getErrorMessage(self):
        return self.data[0]

    def hasTraceback(self):
        return bool(self.data[1])

    def getTraceback(self):
        return self.data[1]

    def _freezeData(self):
        return '\0'.join(self.data)

    @classmethod
    def _thawData(class_, data):
        return data.split('\0')

    def __str__(self):
        return 'Error: %s' % self.data[0]


class BuildFailed(FailureWithException):
    tag = FAILURE_REASON_BUILD_FAILED

    def __str__(self):
        return 'Failed while building: %s' % self.data[0]

class CommandFailed(FailureWithException):
    tag = FAILURE_REASON_COMMAND_FAILED

    def __init__(self, commandId, error='', exception=''):
        if isinstance(commandId, (list, tuple)):
            FailureWithException.__init__(self, commandId)
        else:
            FailureWithException.__init__(self, [error, exception, commandId])

    def __str__(self):
        return 'Failed while executing command %s: %s' % (self.data[2], self.data[0])

class ChrootFailed(FailureWithException):
    tag = FAILURE_REASON_CHROOT

    def __str__(self):
        return 'Failed while creating chroot: %s' % self.data[0]

    def getShortError(self):
        return str(self)

class LoadFailed(FailureWithException):
    tag = FAILURE_REASON_LOAD

    def getShortError(self):
        return 'Failed while loading recipe'

    def __str__(self):
        return 'Failed while loading recipe: %s' % self.data[0]

class InternalError(FailureWithException):
    tag = FAILURE_REASON_INTERNAL

    def getShortError(self):
        return 'Internal rMake Error'

    def __str__(self):
        # print out the whole traceback for internal errors
        return 'Internal rMake Error : %s\n%s' % tuple(self.data)

class MissingBuildreqs(FailureReason):
    tag = FAILURE_REASON_BUILDREQ

    # data format:
    # [(n,vS,fS), (n,vS,fS)]

    def __init__(self, buildReqs):
        # remove Nones to make formatting easier
        newData = []
        for item in buildReqs:
            if isinstance(item[1], tuple):
                isCross, (n,v,f) = item
            else:
                (n,v,f) = item
            if v is None:
                v = ''
            if f is None:
                f = ''
            newData.append((n,v,f))
        self.data = newData

    def __str__(self):
        data = ', '.join("%s=%s[%s]" % x for x in self.data)
        return 'Could not satisfy build requirements: %s' % data

    def _freezeData(self):
        return '\000'.join("%s=%s[%s]" % x for x in self.data)

    @classmethod
    def _thawData(class_, data):
        return [cmdline.parseTroveSpec(x) for x in data.split('\000')]

class MissingDependencies(FailureReason):
    tag = FAILURE_REASON_DEP

    # data format:
    # [((n,v,f), depSet), ((n,v,f), depSet)]

    def __init__(self, depSet):
        self.data = depSet

    def __str__(self):
        s = ['    %s=%s[%s] requires:\n\t%s' % (x[0] + ('\n\t'.join(str(x[1]).split('\n')),)) for x in self.data ]
        return 'Could not satisfy dependencies:\n%s' % '\n'.join(s)

    def _freezeData(self):
        return '\000'.join('%s=%s[%s]\001%s' % (x[0] + (x[1].freeze(),)) for x in self.data)

    @classmethod
    def _thawData(class_, data):
        parsedData = []
        lines = data.split('\000')
        for line in lines:
            troveSpec, flavor = line.split('\001')
            troveSpec = cmdline.parseTroveSpec(troveSpec)
            troveTup = troveSpec[0], versions.VersionFromString(troveSpec[1]), troveSpec[2]
            dep = ThawFlavor(flavor)
            parsedData.append((troveTup, dep))
        return parsedData


class Stopped(FailureReason):
    tag = FAILURE_REASON_STOPPED

    def __str__(self):
        return 'Stopped: %s' % self.data

# ----------------------------------------------------
# NOTE: Must add new failure types to this list
# ---------------------------------------------------

classByTag = {}
for class_ in (FailureReason,
               BuildFailed,
               CommandFailed,
               ChrootFailed,
               MissingBuildreqs,
               MissingDependencies,
               LoadFailed,
               InternalError,
               Stopped):
    classByTag[class_.tag] = class_

def freezeFailureMethod(failure):
    if failure is None:
        return ('', '')
    return failure.__freeze__()

def thawFailureMethod(frz):
    if frz[0] == '' or frz[0] is None:
        return None
    tag = int(frz[0])
    class_ = classByTag[tag]
    return class_(class_._thawData(frz[1]))

apiutils.registerMethods('FailureReason',
                         freezeFailureMethod, thawFailureMethod)
