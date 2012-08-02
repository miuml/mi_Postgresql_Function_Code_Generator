#! /usr/bin/env python

"""
Generate UI_ and method_ attribute setting plpgsql scripts

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
from mi_Template import Template

# Diagnostic
import pdb

# Template Sets
template_sets = {} 

# Template set is dictionary of template names and correspondng files
# example entry: "UI":"Resources/template_UI_set.sql"
class Template_Set:
    """ Group of Templates to be filled out at the same time
    """
    def __init__( self, name, templates ):
        self.name = name # ex: "Setters: a UI_ and method_ template"
        self.templates = [ Template( name, file_name, target_name_pattern )
                    for name, file_name, target_name_pattern in templates ]

    def generate( self, subsys_dir ):
        """Fill out each Template in this Template Set
        """
        for t in self.templates:
            t.fill_out( subsys_dir )


# Specify all template sets here.  We'll read these from a file instead, eventually.
# { Template set name : ( ( Template name, template fname, target fname ), ... ) }
tsets = { 'Setters': (
                ( 'UI', 'template_UI_set.sql', 'UI_set_<class>.sql' ),
                ( 'Method', 'template_method_set.sql', 'method_<class>_set.sql' )
            )
        }

for name, templates in tsets.items():
    template_sets[name] = Template_Set( name, templates )



if __name__ == '__main__':
    print( "Cannot be run from the command line." )
