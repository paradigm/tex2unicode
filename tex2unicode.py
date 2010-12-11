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
# 2010-12-10, Daniel Thau
#   version 0.3: implemeneted goosemo's recommendations to clean up the code
# 2010-12-09, Daniel Thau
#   version 0.2: added support for {} blocks
# 2010-12-08, Daniel Thau
#   version 0.1: initial release
#

#
# This script converts TeX-style input from weechat into unicode/weechat
#


import weechat,string

SCRIPT_NAME    = "tex2unicode"
SCRIPT_AUTHOR  = "Daniel Thau"
SCRIPT_VERSION = "0.3"
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

def find_bracket_end(bracket_start,weechatbuffer):
"""Find the matching } in a {} block."""
    bracket_end = 0 # will be matching }
    nested_count = 0 # number of nested {'s - don't match a nested }
    for index in range(bracket_start,len(weechatbuffer)):
        if weechatbuffer[index]=='}' and nested_count==0: # found matching }
            return index
        if weechatbuffer[index]=='{': # found nested {
            nested_count=nested_count+1
        if weechatbuffer[index]=='}' and nested_count>0: # found nested }
            nested_count=nested_count-1
    return index


def command_run_input(data, buffer, command):
    """
    When applicable, substitute TeX-style sections of weechat buffer with unicode or weechat equivilents.
    """
    # if return is pressed, get input from weechat and check to ensure that we want to do something
    if command == "/input return": # enter was pressed
        # get buffer to parse/replace
        weechatbuffer = unicode(weechat.buffer_get_string(buffer, 'input'))
        # don't interfere with any commands other than /me
        if weechatbuffer.startswith('/') and not weechatbuffer.startswith('/me'):
            return weechat.WEECHAT_RC_OK
        # disable tex2unicode by starting with a space
        if weechatbuffer.startswith(' '):
            return weechat.WEECHAT_RC_OK
        # next few sections deal with the various ways TeX sees bolding
        while '\\textbf{' in weechatbuffer:
            bracket_start = weechatbuffer.find('\\textbf{')+8 # start of {} block
            bracket_end = find_bracket_end(bracket_start,weechatbuffer) # end of {} block
            weechatbuffer=weechatbuffer[:bracket_start-8]+weechat.color('bold')+weechatbuffer[bracket_start:bracket_end]+weechat.color('-bold')+weechatbuffer[bracket_end+1:]
        while '\\mathbf{' in weechatbuffer:
            bracket_start = weechatbuffer.find('\\mathbf{')+8 # start of {} block
            bracket_end = find_bracket_end(bracket_start,weechatbuffer) # end of {} block
            weechatbuffer=weechatbuffer[:bracket_start-8]+weechat.color('bold')+weechatbuffer[bracket_start:bracket_end]+weechat.color('-bold')+weechatbuffer[bracket_end+1:]
        while '\\bf{' in weechatbuffer:
            bracket_start = weechatbuffer.find('\\bf{')+4 # start of {} block
            bracket_end = find_bracket_end(bracket_start,weechatbuffer) # end of {} block
            weechatbuffer=weechatbuffer[:bracket_start-4]+weechat.color('bold')+weechatbuffer[bracket_start:bracket_end]+weechat.color('-bold')+weechatbuffer[bracket_end+1:]
        # expand _{} and ^{} blocks, distributing the _'s and ^'s
        # prepend viable chars with _ in _{} block
        while weechatbuffer.find('_{')!=-1:
            bracket_start = weechatbuffer.find('_{')+2 # start of {} block
            bracket_end = find_bracket_end(bracket_start,weechatbuffer) # end of {} block
            new_inside_bracket=''
            for char in weechatbuffer[bracket_start:bracket_end]:
                if (string.letters + string.digits + '()+-=').find(char)!=-1:
                    new_inside_bracket=new_inside_bracket+'_'
                new_inside_bracket=new_inside_bracket+char
            weechatbuffer=weechatbuffer[:bracket_start-2]+new_inside_bracket+weechatbuffer[bracket_end+1:]

        # prepend viable chars with ^ in ^{} block
        while weechatbuffer.find('^{')!=-1:
            bracket_start = weechatbuffer.find('^{')+2 # start of {} block
            bracket_end = find_bracket_end(bracket_start,weechatbuffer) # end of {} block
            new_inside_bracket=''
            for char in weechatbuffer[bracket_start:bracket_end]:
                if (string.letters + string.digits + '()+-=').find(char)!=-1:
                    new_inside_bracket=new_inside_bracket+'^'
                new_inside_bracket=new_inside_bracket+char
            weechatbuffer=weechatbuffer[:bracket_start-2]+new_inside_bracket+weechatbuffer[bracket_end+1:]

        # replace each TeX-style input with comparable unicode
        weechatbuffer=unicode(weechatbuffer.replace(u'``',u'\u201C'))
        weechatbuffer=unicode(weechatbuffer.replace('\'\'',u'\u201D'))
        weechatbuffer=unicode(weechatbuffer.replace('\\alpha',u'\u03B1'))
        weechatbuffer=unicode(weechatbuffer.replace('\\beta',u'\u03B2'))
        weechatbuffer=unicode(weechatbuffer.replace('\\gamma',u'\u03B3'))
        weechatbuffer=unicode(weechatbuffer.replace('\\delta',u'\u03B4'))
        weechatbuffer=unicode(weechatbuffer.replace('\\epsilon',u'\u03B5'))
        weechatbuffer=unicode(weechatbuffer.replace('\\zeta',u'\u03B6'))
        weechatbuffer=unicode(weechatbuffer.replace('\\eta',u'\u03B7'))
        weechatbuffer=unicode(weechatbuffer.replace('\\theta',u'\u03B8'))
        weechatbuffer=unicode(weechatbuffer.replace('\\iota',u'\u03B9'))
        weechatbuffer=unicode(weechatbuffer.replace('\\kappa',u'\u03BA'))
        weechatbuffer=unicode(weechatbuffer.replace('\\lambda',u'\u03BB'))
        weechatbuffer=unicode(weechatbuffer.replace('\\mu',u'\u03BC'))
        weechatbuffer=unicode(weechatbuffer.replace('\\nu',u'\u03BD'))
        weechatbuffer=unicode(weechatbuffer.replace('\\xi',u'\u03BE'))
        weechatbuffer=unicode(weechatbuffer.replace('\\omicron',u'\u03BF'))
        weechatbuffer=unicode(weechatbuffer.replace('\\pi',u'\u03C0'))
        weechatbuffer=unicode(weechatbuffer.replace('\\rho',u'\u03C1'))
        # final sigma?
        weechatbuffer=unicode(weechatbuffer.replace('\\sigma',u'\u03C3'))
        weechatbuffer=unicode(weechatbuffer.replace('\\tau',u'\u03C4'))
        weechatbuffer=unicode(weechatbuffer.replace('\\upsilon',u'\u03C5'))
        weechatbuffer=unicode(weechatbuffer.replace('\\phi',u'\u03C6'))
        weechatbuffer=unicode(weechatbuffer.replace('\\chi',u'\u03C7'))
        weechatbuffer=unicode(weechatbuffer.replace('\\psi',u'\u03C8'))
        weechatbuffer=unicode(weechatbuffer.replace('\\omega',u'\u03C9'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Alpha',u'\u0391'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Beta',u'\u0392'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Gamma',u'\u0393'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Delta',u'\u0394'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Epsilon',u'\u0395'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Zeta',u'\u0396'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Eta',u'\u0397'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Theta',u'\u0398'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Iota',u'\u0399'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Kappa',u'\u039A'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Lambda',u'\u039B'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Mu',u'\u039C'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Nu',u'\u039D'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Xi',u'\u039E'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Omicron',u'\u039F'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Pi',u'\u03A0'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Rho',u'\u03A1'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Sigma',u'\u03A3'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Tau',u'\u03A4'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Upsilon',u'\u03A5'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Phi',u'\u03A6'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Chi',u'\u03A7'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Psi',u'\u03CA'))
        weechatbuffer=unicode(weechatbuffer.replace('\\Omega',u'\u03A9'))
        weechatbuffer=unicode(weechatbuffer.replace('\\int',u'\u222B'))
        weechatbuffer=unicode(weechatbuffer.replace('\\iint',u'\u222C'))
        weechatbuffer=unicode(weechatbuffer.replace('\\iiint',u'\u222D'))
        weechatbuffer=unicode(weechatbuffer.replace('\\sum',u'\u2211'))
        weechatbuffer=unicode(weechatbuffer.replace('\\infty',u'\u221E'))
        weechatbuffer=unicode(weechatbuffer.replace('\\sqrt',u'\u221A'))
        weechatbuffer=unicode(weechatbuffer.replace('\\times',u'\u00D7'))
        weechatbuffer=unicode(weechatbuffer.replace('\\pm',u'\u00B1'))
        weechatbuffer=unicode(weechatbuffer.replace('\\mp',u'\u2213'))
        weechatbuffer=unicode(weechatbuffer.replace('\\therefore',u'\u2234'))
        weechatbuffer=unicode(weechatbuffer.replace('\\approx',u'\u2248'))
        weechatbuffer=unicode(weechatbuffer.replace('\\equiv',u'\u2261'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{1}{2}',u'\u00BD'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{1}{4}',u'\u00BC'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{3}{4}',u'\u00BE'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{1}{3}',u'\u2153'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{2}{3}',u'\u2154'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{1}{5}',u'\u2155'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{2}{5}',u'\u2156'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{3}{5}',u'\u2157'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{4}{5}',u'\u2158'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{1}{6}',u'\u2159'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{5}{6}',u'\u215A'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{1}{8}',u'\u215B'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{3}{8}',u'\u215C'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{5}{8}',u'\u215D'))
        weechatbuffer=unicode(weechatbuffer.replace('\\frac{7}{8}',u'\u215E'))
        weechatbuffer=unicode(weechatbuffer.replace('^0',u'\u2070'))
        weechatbuffer=unicode(weechatbuffer.replace('^1',u'\u00B9'))
        weechatbuffer=unicode(weechatbuffer.replace('^2',u'\u00B2'))
        weechatbuffer=unicode(weechatbuffer.replace('^3',u'\u00B3'))
        weechatbuffer=unicode(weechatbuffer.replace('^4',u'\u2074'))
        weechatbuffer=unicode(weechatbuffer.replace('^5',u'\u2075'))
        weechatbuffer=unicode(weechatbuffer.replace('^6',u'\u2076'))
        weechatbuffer=unicode(weechatbuffer.replace('^7',u'\u2077'))
        weechatbuffer=unicode(weechatbuffer.replace('^8',u'\u2078'))
        weechatbuffer=unicode(weechatbuffer.replace('^9',u'\u2079'))
        weechatbuffer=unicode(weechatbuffer.replace('^+',u'\u207A'))
        weechatbuffer=unicode(weechatbuffer.replace('^-',u'\u207B'))
        weechatbuffer=unicode(weechatbuffer.replace('^=',u'\u207C'))
        weechatbuffer=unicode(weechatbuffer.replace('^(',u'\u207D'))
        weechatbuffer=unicode(weechatbuffer.replace('^)',u'\u207E'))
        weechatbuffer=unicode(weechatbuffer.replace('^i',u'\u2071'))
        weechatbuffer=unicode(weechatbuffer.replace('^n',u'\u207F'))
        weechatbuffer=unicode(weechatbuffer.replace('_0',u'\u2080'))
        weechatbuffer=unicode(weechatbuffer.replace('_1',u'\u2081'))
        weechatbuffer=unicode(weechatbuffer.replace('_2',u'\u2082'))
        weechatbuffer=unicode(weechatbuffer.replace('_2',u'\u2082'))
        weechatbuffer=unicode(weechatbuffer.replace('_3',u'\u2083'))
        weechatbuffer=unicode(weechatbuffer.replace('_4',u'\u2084'))
        weechatbuffer=unicode(weechatbuffer.replace('_5',u'\u2085'))
        weechatbuffer=unicode(weechatbuffer.replace('_6',u'\u2086'))
        weechatbuffer=unicode(weechatbuffer.replace('_7',u'\u2087'))
        weechatbuffer=unicode(weechatbuffer.replace('_8',u'\u2088'))
        weechatbuffer=unicode(weechatbuffer.replace('_9',u'\u2089'))
        weechatbuffer=unicode(weechatbuffer.replace('_+',u'\u208A'))
        weechatbuffer=unicode(weechatbuffer.replace('_-',u'\u208B'))
        weechatbuffer=unicode(weechatbuffer.replace('_=',u'\u208C'))
        weechatbuffer=unicode(weechatbuffer.replace('_(',u'\u208D'))
        weechatbuffer=unicode(weechatbuffer.replace('_)',u'\u208E'))
        weechatbuffer=unicode(weechatbuffer.replace('\\square',u'\u2610'))
        weechatbuffer=unicode(weechatbuffer.replace('\\checkedbox',u'\u2611'))
        weechatbuffer=unicode(weechatbuffer.replace('\\checkmarkbold',u'\u2714'))
        weechatbuffer=unicode(weechatbuffer.replace('\\checkmark',u'\u2713'))
        # give weechat the new buffer
        weechat.buffer_set(buffer, 'input', weechatbuffer.encode('utf-8'))
    return weechat.WEECHAT_RC_OK
