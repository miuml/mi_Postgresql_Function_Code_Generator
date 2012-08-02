#! /usr/bin/env python

"""
Target - Code generated from template is saved here before writing out
to a file.

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
from os import path, getenv

# Local
from mi_Error import *

# Diagnostic
import pdb

# Constant
_PROJECT_HOME_DIR_ENV_VAR = "miumlhome"

class Target:
    """
    Target file

    """
    def __init__( self, subsys_dir, file_name ):
        project_dir = getenv( _PROJECT_HOME_DIR_ENV_VAR, False )
        if not project_dir:
            raise mi_Error("{} env var not set".format( _PROJECT_HOME_DIR_ENV_VAR ) )
        self.name = path.join( project_dir, subsys_dir, file_name )
        self.lines = []

    def write( self ):
        """
        Write out the entire target to its file.

        """
        try:
            self.file = open( self.name, 'w' )
        except IOError:
            raise mi_File_Error( "Cannot open for write.", self.name )

        for l in self.lines:
            self.file.write( l )

if __name__ == '__main__':
    print( "Cannot be run from the command line." )
