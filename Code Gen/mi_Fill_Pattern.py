#! /usr/bin/env python

"""
Fill Pattern - Replaces any <tag> in a string with corresponding fill['tag'] value.

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

# System
import re

# Local
from mi_Error import *
from mi_Tag import * # fill and expanding_tag globals

# Diagnostic
import pdb
from pprint import pprint as pp

# Patterns for tag and command detection
tag = re.compile( r'<\w+>' ) # Recognizes a tag such as: <focus_attr>

class Fill_Pattern:
    """ Text with embedded tags each of which may be replaced by a fill value
    """
    def __init__( self, pattern ):
        """ Immediately fills itself out using existing fills """
        self.filled_out_text = pattern # Start with the supplied pattern
        # Replace each tag embedded in pattern (blank) with that tag's fill value
        for blank in re.findall( tag, self.filled_out_text ):
            self.filled_out_text = self.filled_out_text.replace( blank, fill[blank.strip('<>')] )
        # The pattern is now completely filled out
        # and available as the filled_out_text attribute

if __name__ == '__main__':
    print( "Cannot be run from the command line." )
