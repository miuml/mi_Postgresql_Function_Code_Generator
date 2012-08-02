#! /usr/bin/env python

"""
List Region - Consecutive lines in Template where each line except the last must
terminate with a delimiter string such as a comma.  This is only used within
an Expansion Block since, otherwise, we could pre-specify each delimitier in the
Template.

"""
# --
# Copyright 2012, Model Integration, LLC
# Developer: Leon Starr / leon_starr@modelint.com

# This file is part of the miUML metamodel library.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.  The license text should be viewable at
# http://www.gnu.org/licenses/
# --
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

# Local
from mi_Error import *

# Diagnostic
import pdb
from pprint import pprint as pp

class List_Region:
    """Delimited List Region
    """
    def __init__( self, template, delimiter ):
        self.template = template
        self.delimiter = delimiter
        # Assume one empty set of lines before the first expansion block
        self.assembly = []

    def interstitial( self, filled_out_line ):
        """Buffer a filled out line before the next expansion block
        """
        self.assembly.append( { 'iline' : filled_out_line } )

    def add_block( self, eblock ):
        """Add newly created expansion block to be flushed and/or trimmed later.
        """
        self.assembly.append( {'eblock' : eblock } )

    def terminate( self ):
        """Trim the last block and then flush them all to the target, if any
        """
        # Find the last block, and if found, trim its final delimiter
        for b in reversed( self.assembly ):
            if 'eblock' in b:
                b['eblock'].trim( self.delimiter )
                break
        for b in self.assembly:
            if 'eblock' in b:
                b['eblock'].flush()
            else:
                self.template.target.lines.append( b['iline'] )
        # Delete self
        self.template.list_region = None

if __name__ == '__main__':
    print( "Cannot be run from the command line." )
