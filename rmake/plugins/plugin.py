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
Definition of plugins available for rmake plugins.

Plugin writers should derive from one of these classes.

The plugin will be called with the hooks described here, if the
correct program is being run.  For example, when running rmake-server,
the server hooks will be run.
"""
from rmake.lib.pluginlib import Plugin

TYPE_CLIENT = 0
TYPE_SERVER = 1
TYPE_LIBRARY = 3

class ClientPlugin(Plugin):

    types = [TYPE_CLIENT]

    def client_preInit(self, main, argv):
        """
            Called right after plugins have been loaded.
        """
        pass

    def client_preCommand(self, main, thisCommand, (buildConfig, conaryConfig),
                         argSet, args):
        pass

    def client_preCommand2(self, main, client, command):
        """
            Called after the command-line client has instantiated, 
            but before the command has been executed.
        """
        pass

class ServerPlugin(Plugin):

    types = [TYPE_SERVER]

    def server_preConfig(self, main):
        """
            Called before the configuration file has been read in.
        """
        pass

    def server_preInit(self, main, argv):
        """
            Called before the server has been instantiated.
        """
        pass

    def server_postInit(self, server):
        """
            Called after the server has been instantiated but before
            serving is done.
        """
        pass

    def server_pidDied(self, server, pid, status):
        """
            Called when the server collects a child process that has died.
        """
        pass

    def server_loop(self, server):
        """
            Called once per server loop, between requests.
        """
        pass

    def server_builderInit(self, server, builder):
        """
            Called when the server instantiates a builder for a job.
        """
        pass

    def server_shutDown(self, server):
        """
            Called when the server is halting.
        """
        pass


class LibraryPlugin(Plugin):

    types = [TYPE_LIBRARY]
    protocol = None

    def library_init(self):
        """
            Called when using rmake as a library.
        """
