# -*- python -*-

# LMTP protocol support for tmda
#
# Based on spamcheck.py, Copyright (C) 2002 James Henstridge
# Which was distributed with the following license"
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import sys, string
import re, getopt
import smtplib, socket

import Defaults
import Errors

# this class hacks smtplib's SMTP class into a shape where it will
# successfully pass a message off to Cyrus's LMTP daemon.
# Also adds support for connecting to a unix domain socket.
class LMTP(smtplib.SMTP):
    lhlo_resp = None
    def __init__(self, host=''):
        self.lmtp_features  = {}
        self.esmtp_features = self.lmtp_features

        if host:
            (code, msg) = self.connect(host)
            if code != 220:
                raise smtplib.SMTPConnectError(code, msg)

    def connect(self, host='localhost'):
        """Connect to a host on a given port.

        If the hostname starts with `unix:', the remainder of the string
        is assumed to be a unix domain socket.
        """

        if host[:5] == 'unix:':
            host = host[5:]
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            if self.debuglevel > 0: print 'connect:', host
            self.sock.connect(host)
        else:
            i = string.find(host, ':')
            if i >= 0:
                host, port = host[:i], host[i+1:]
                try: port = int(port)
                except string.atoi_error:
                    raise socket.error, "non numeric port"
            if not port: port = LMTP_PORT
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.debuglevel > 0: print 'connect:', (host, port)
            self.sock.connect((host, port))
        (code, msg) = self.getreply()
        if self.debuglevel > 0: print 'connect:', msg
        return (code, msg)

    def putcmd(self, cmd, args=""):
        """Send a command to the server."""
        if args:
            str = '%s %s%s' % (cmd, args, smtplib.CRLF)
        else:
            str = '%s%s' % (cmd, smtplib.CRLF)
        self.send(str)

    def lhlo(self, name='localhost'):
        """ LMTP 'lhlo' command.
        Hostname to send for this command defaults to localhost.
        """
        self.putcmd("lhlo",name)
        (code, msg) = self.getreply()
        if code == -1 and len(msg) == 0:
            raise smtplib.SMTPServerDisconnected("Server not connected")
        self.lhlo_resp = msg
        self.ehlo_resp = msg
        if code != 250:
            return (code, msg)
        self.does_esmtp = 1
        # parse the lhlo response
        resp = string.split(self.lhlo_resp, '\n')
        del resp[0]
        for each in resp:
            m = re.match(r'(?P<feature>[A-Za-z0-9][A-Za-z0-9\-]*)',each)
            if m:
                feature = string.lower(m.group("feature"))
                params = string.strip(m.string[m.end("feature"):])
                self.lmtp_features[feature] = params
        return (code, msg)

    # make sure bits of code that tries to EHLO actually LHLO instead
    ehlo = lhlo

    def mail(self, sender, options=[]):
        optionlist = ''
        if options and self.does_esmtp:
            optionlist = ' ' + string.join(options, ' ')
        self.putcmd('mail', 'FROM:%s%s' % (smtplib.quoteaddr(sender), optionlist))
        return self.getreply()
    def rcpt(self, recip, options=[]):
        optionlist = ''
        if options and self.does_esmtp:
            optionlist = ' ' + string.join(options, ' ')
        self.putcmd('rcpt', 'TO:%s%s' % (smtplib.quoteaddr(recip), optionlist))
        return self.getreply()

def sendlmtp(lmtp_host, sender, recipient, data):
    """Send mail on via lmtp for cyrus imapd"""
    try:
        lmtp = LMTP(lmtp_host)
        code, msg = lmtp.lhlo()
        if code != 250:
            raise Errors.DeliveryError, 'LMTP lhlo error'
        lmtp.sendmail(sender, recipient, data)
    except smtplib.SMTPRecipientsRefused:
        raise Errors.DeliveryError, 'LMTP User does not exist'

    except smtplib.SMTPDataError, errors:
        raise Errors.DeliveryError, 'LMTP Data error'
