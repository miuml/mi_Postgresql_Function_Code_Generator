#! /usr/bin/env python

"""
Template Domain - Bridge Functions

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
from datetime import date

# Local
from mi_Error import *
from mi_Tag import * # fill and expanding_tag globals
from mi_Template_Set import template_sets

# Diagnostic
import pdb

# RUNTIME BRIDGES

# Here we encapsulate the template domain so that any client domain can use
# its services without knowing anything about how the template domain is designed
# or being aware of any particular internal vocabulary/mechanisms

# Maps model data from model domain to fill values in template domain

def flatten( text ):
    """
    Remove spaces and push down to lower case for legal postgres variable names

    """
    return text.lower().replace(' ', '_')


def client_gen_setters( subsys_name, subsys_alias, p_class, attrs, ui_types ):
    """
    Generate the UI_ and method_ templates required for an attribute's setter

    """
    # Flatten the ui_types for use as DB variable names
    ui_types = { flatten(k) : flatten(v) for (k, v) in ui_types.items() }

    # These fills will be constant throughout all templates
    fill['year'] = str( date.today().year )
    fill['schema'] = 'mi'+subsys_alias.lower()
    fill['class'] = flatten(p_class) # p_ for param since 'class' is a keyword
    fill['Class'] = flatten(p_class).title() # For documentation, use title case

    # These fills will change as a template is filled out
    for purpose in attrs: # purpose is focus or modify
        expanding_tag.update( {purpose+'_attr':[], purpose+'_type':[], purpose+'_default':[]} )
        for a in attrs[purpose]:
            expanding_tag[purpose+'_attr'].append(flatten(a))
            expanding_tag[purpose+'_type'].append( flatten( attrs[purpose][a]['type'] ) )
            expanding_tag[purpose+'_default'].append( attrs[purpose][a]['default'] )

    # Each modify attr type has a raw ui type prior to validation
    expanding_tag['modify_ui_type'] = [ ui_types[t] for t in expanding_tag['modify_type'] ]

    # So now, for each focus attr, we have the attr name and type values
    # and for each modify attr, we have the attr name, type and raw ui type values
    # loaded into expanding tags for later template population

    # Fill out all Templates in the 'Setters' Template Set
    template_sets['Setters'].generate( subsys_dir = subsys_name + ' Subsystem' )

# End Bridge functions (from here on in, Template domain vocabulary only)
if __name__ == '__main__':
    print( "Cannot be run from the command line." )
