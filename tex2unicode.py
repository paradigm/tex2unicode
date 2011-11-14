# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 by Daniel Thau
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#
# (this script requires WeeChat 0.3.0 or newer)
#
# History:
# 2010-02-26, Daniel Thau
#   version 0.4: major reworking, attempt to processing more TeX-like and deal.
#   with things like scoping sanely
# 2010-12-10, Daniel Thau
#   version 0.3: implemeneted goosemo's recommendations to clean up the code
# 2010-12-09, Daniel Thau
#   version 0.2: added support for {} blocks
# 2010-12-08, Daniel Thau
#   version 0.1: initial release
#

#
# TODO:
# - commands with arguments, like \frac, \color
# - unicode input
#

#
# This script converts TeX-style input from weechat into unicode/weechat
#


import weechat,string

SCRIPT_NAME    = "tex2unicode"
SCRIPT_AUTHOR  = "Daniel Thau"
SCRIPT_VERSION = "0.4"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "converts TeX-style input to unicode/weechat"

"""Set up weechat hooks."""
if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE,
                    SCRIPT_DESC, "", ""):
    hook_command_run = {
        "input" : ("/input return",  "command_run_input"),
    }
    for hook, value in hook_command_run.iteritems():
        weechat.hook_command_run(value[0], value[1], "")

def command_lookup_table(command,states):
    """Return output for command given the state"""
    # output from command
    out=""
    # attribute changes from command
    new_attributes=[]
    # formatting
    if command=="textbf":
        new_attributes.append("bold")
    if command=="mathbf":
        new_attributes.append("bold")
    if command=="bfseries":
        new_attributes.append("scopebold")

    charset1 = ["\\", " ", "^", "{", "}"]
    # escaped special/active
    for char in charset1:
        if char == command:
            out = char

    charset2 = {
            "textbackslash" : u"\\",
            "backslash" : u"\\",
            "alpha" : u"\u03B1",
            "beta" : u"\u03B2",
            "delta" : u"\u03B4",
            "epsilon" : u"\u03B5",
            "zeta" : u"\u03B6",
            "eta" : u"\u03B7",
            "theta" : u"\u03B8",
            "iota" : u"\u03B9",
            "kappa" : u"\u03BA",
            "lambda" : u"\u03BB",
            "mu" : u"\u03BC",
            "nu" : u"\u03BD",
            "xi" : u"\u03BE",
            "omicron" : u"\u03BF",
            "pi" : u"\u03C0",
            "rho" : u"\u03C1",
            "sigma" : u"\u03C3",
            "tau" : u"\u03C4",
            "upsilon" : u"\u03C5",
            "phi" : u"\u03C6",
            "chi" : u"\u03C7",
            "psi" : u"\u03C8",
            "omega" : u"\u03C9",
            "Alpha" : u"\u0391",
            "Beta" : u"\u0392",
            "Gamma" : u"\u0393",
            "Delta" : u"\u0394",
            "Epsilon" : u"\u0395",
            "Zeta" : u"\u0396",
            "Eta" : u"\u0397",
            "Theta" : u"\u0398",
            "Iota" : u"\u0399",
            "Kappa", "\u039A",
            "Lambda" : u"\u039B",
            "Mu" : u"\u039C",
            "Nu" : u"\u039D",
            "Xi" : u"\u039E",
            "Omicron" : u"\u039F",
            "Pi" : u"\u03A0",
            "Rho" : u"\u03A1",
            "Sigma" : u"\u03A3",
            "Tau" : u"\u03A4",
            "Upsilon" : u"\u03A5",
            "Phi" : u"\u03A6",
            "Chi" : u"\u03A7",
            "Psi" : u"\u03CA",
            "Omega" : u"\u03A9",
            "int" : u"\u222B",
            "iint" : u"\u222C",
            "iiint" : u"\u222D",
            "sum" : u"\u2211",
            "infty" : u"\u221E",
            "sqrt" : u"\u221A",
            "times" : u"\u00D7",
            "pm" : u"\u00B1",
            "mp" : u"\u2213",
            "therefore" : u"\u2234",
            "approx" : u"\u2248",
            "equiv" : u"\u2261",
            "onehalf" : u"\u00BD",
            "onequarter" : u"\u00BC",
            "threequarters" : u"\u00BE",
            "onethird" : u"\u2153",
            "twothirds" : u"\u2154",
            "onefifth" : u"\u2155",
            "twofifths" : u"\u2156",
            "threefifths" : u"\u2157",
            "fourfifths" : u"\u2158",
            "onesixth" : u"\u2159",
            "fivesixths" : u"\u215A",
            "oneeight" : u"\u215B",
            "threeeights" : u"\u215C",
            "fiveeights" : u"\u215D",
            "seveneights" : u"\u215E",
            "square" : u"\u2610",
            "checkedbox" : u"\u2611",
            "checkmarkbold" : u"\u2714",
            "checkmark" : u"\u2713",
            "dots" : u"\u2026",
            "ldots" : u"\u2026",
            "telephone" : u"\u260F",
            "heart" : u"\u2764",
            "TeX" : u"T\u1D07X",
            "LaTeX" : u"L\u1D2CT\u1D07X",
        }

    for char in charset2:
        if char == command:
            out = charset2[char]

    if len(out)+len(new_attributes)==0:
        out= '\\'+command
    return out, new_attributes

def attr(groups,current_attributes):
    """return flat list of current attributes"""
    attributes=current_attributes
    for group in groups:
        for attribute in group:
            attributes.append(attribute)
    return attributes

def command_run_input(data, buffer, command):
    """When applicable, substitute TeX-style sections of weechat buffer with unicode or weechat equivilents."""

    """Check if we actually want to do processing, and return otherwise"""
    # we only care about processing once enter is pressed
    if command != "/input return":
        return weechat.WEECHAT_RC_OK
    # get buffer to parse/replace
    inbuffer = unicode(weechat.buffer_get_string(buffer, 'input'))
    # don't interfere with any weechat commands other than /me
    if inbuffer.startswith('/') and not inbuffer.startswith('/me'):
        return weechat.WEECHAT_RC_OK
    # disable tex2unicode by starting with a space
    if inbuffer.startswith(' '):
        # remove that first space
        weechat.buffer_set(buffer, 'input', inbuffer[1:].encode('utf-8'))
        return weechat.WEECHAT_RC_OK
    """run through the inbuffer, building the outbuff as we go"""
    # the soon-to-be output buffer
    outbuffer=unicode("")
    # attributes for next character - out of scope quickly without grouping
    current_attributes=[]
    # an array, where each item is a list of the attributes at that scope depth
    groups=[[]]
    # if state==N, we're processing normal text - just output
    # if state==S, we've processed this char specially, return to N next char
    # if state==C, we're looking for the end of a command - don't print
    state="N"
    # will store commands as we build them char-by-char
    command=""
    for char in inbuffer:
        """commands and active characters"""
        # one-character commands
        if state=="C" and string.ascii_letters.find(char)==-1 and command=="\\":
            command+=char
            commandoutput, new_attributes = command_lookup_table(command[1:],"")
            outbuffer+=commandoutput
            for attribute in new_attributes:
                current_attributes.append(attribute)
            state="S"
        # multi-character commands
        if state=="C" and string.ascii_letters.find(char)==-1:
            commandoutput, new_attributes = command_lookup_table(command[1:],"")
            outbuffer+=commandoutput
            for attribute in new_attributes:
                current_attributes.append(attribute)
            if char==" ": # eat first space after multi-char command
                state="S"
            else:         # char may mean end of command, but still need to process
                state="N"
        # moving scope attributes to scope
        if current_attributes.count("scopebold")>0:
            groups[-1].append("bold")
            current_attributes.remove("scopebold")
        # active characters
        if state=="N" and char=="^": # superscripts
            current_attributes.append("superscript")
            state="S"
        if state=="N" and char=="_": # subscripts
            current_attributes.append("subscript")
            state="S"
        if len(outbuffer)>0:
            if state=="N" and char=="`" and outbuffer[-1]=="`": # opening quotes
                outbuffer = outbuffer[:-1]+u'\u201C'
                state="S"
            if state=="N" and char=="'" and outbuffer[-1]=="'": # closing quotes
                outbuffer = outbuffer[:-1]+u'\u201D'
                state="S"
        # found beginning of new command
        if state=="N" and char=="\\":
            state="C"
            # clear command buffer
            command=""
        """grouping commands"""
        if state=="N" and char=="{":
            if current_attributes.count("bold")>0:
                outbuffer+=weechat.color("bold")
            groups.append(current_attributes)
            current_attributes=[]
            state="S"
        if state=="N" and char=="}" and len(groups)>0:
            old_groups=groups.pop()
            if old_groups.count("bold")>0:
                outbuffer+=weechat.color("-bold")
            state="S"
        """state N processing"""
        # normal state -- check attributes, print
        if state=="N":
            # open bold
            if attr(groups,current_attributes).count("bold")>0:
                outbuffer+=weechat.color("bold")
            # superscripts
            if attr(groups,current_attributes).count("superscript")>0:
                if char=="0":
                    outbuffer+=u'\u2070'
                elif char=="1":
                    outbuffer+=u'\u00B9'
                elif char=="2":
                    outbuffer+=u'\u00B2'
                elif char=="3":
                    outbuffer+=u'\u00B3'
                elif char=="4":
                    outbuffer+=u'\u2074'
                elif char=="5":
                    outbuffer+=u'\u2075'
                elif char=="6":
                    outbuffer+=u'\u2076'
                elif char=="7":
                    outbuffer+=u'\u2077'
                elif char=="8":
                    outbuffer+=u'\u2078'
                elif char=="9":
                    outbuffer+=u'\u2079'
                elif char=="+":
                    outbuffer+=u'\u207A'
                elif char=="-":
                    outbuffer+=u'\u207B'
                elif char=="=":
                    outbuffer+=u'\u207C'
                elif char=="(":
                    outbuffer+=u'\u207D'
                elif char==")":
                    outbuffer+=u'\u207E'
                elif char=="i":
                    outbuffer+=u'\u2071'
                elif char=="n":
                    outbuffer+=u'\u207F'
                else:
                    outbuffer+=char
            # subscripts
            elif attr(groups,current_attributes).count("subscript")>0:
                if char=="0":
                    outbuffer+=u'\u2080'
                elif char=="1":
                    outbuffer+=u'\u2081'
                elif char=="2":
                    outbuffer+=u'\u2082'
                elif char=="3":
                    outbuffer+=u'\u2083'
                elif char=="4":
                    outbuffer+=u'\u2084'
                elif char=="5":
                    outbuffer+=u'\u2085'
                elif char=="6":
                    outbuffer+=u'\u2086'
                elif char=="7":
                    outbuffer+=u'\u2087'
                elif char=="8":
                    outbuffer+=u'\u2088'
                elif char=="9":
                    outbuffer+=u'\u2089'
                elif char=="+":
                    outbuffer+=u'\u208A'
                elif char=="-":
                    outbuffer+=u'\u208B'
                elif char=="=":
                    outbuffer+=u'\u208C'
                elif char=="(":
                    outbuffer+=u'\u208D'
                elif char==")":
                    outbuffer+=u'\u208E'
                else:
                    outbuffer+=char
            else: # no special attribute work
                outbuffer+=char
            # close bold
            if attr(groups,current_attributes).count("bold")>0:
                outbuffer+=weechat.color("-bold")
        """other processing preperation"""
        if state=="N" and char!=" ":
            current_attributes=[] # non-grouped attributes are now out of scope
        if state=="C":
            command+=char
        # S states only last one character, return to N
        if state=="S":
            state="N"
    # may not have finished last command yet
    if state=="C" and command!="":
        commandoutput, new_attributes = command_lookup_table(command[1:],"")
        outbuffer+=commandoutput
    # give weechat the new buffer
    weechat.buffer_set(buffer, 'input', outbuffer.encode('utf-8'))
    return weechat.WEECHAT_RC_OK
