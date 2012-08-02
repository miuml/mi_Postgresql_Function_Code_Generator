#! /usr/bin/env python

"""
This is a very small chunk of the miUML metamodel.  There's just enough here
to generate settings UI_ and method_set files.

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
import os
import sys

# Local
_MODULE_DIR = os.path.abspath("../Modules")
if _MODULE_DIR not in sys.path:
    sys.path.append(_MODULE_DIR)
from mi_Error import *
from mi_Parse import parse
import mi_Template_Domain
from mi_Structured_File import Structured_File

# Diagnostic
import pdb

# Constants
PCODE = { 'f':'focus', 'm':'modify' } # Purpose code
MODELFILE = "model.mi"
RESOURCE_DIR = "Resources"
IN = 'in' # Model elments inside
OUT = 'out' # Model elements outside
TOP = -1 # Top of the stack

# mtax - Model entity taxonomy
mtax = { 'model':{ OUT:None, IN:{'domain', 'bridge'} },
        'domain':{ OUT:'model', IN:{'subsystem', 'spanning element'} },
            'spanning element':{ OUT:'domain', IN:{'cloop', 'lineage', 'type'} },
                'cloop':{ OUT:'spanning element', IN:{} },
                'lineage':{ OUT:'spanning element', IN:{} },
                'type':{ OUT:'spanning element', IN:{} },
            'subsystem':{ OUT:'domain', IN:{'class', 'relationship'} },
                'class':{ OUT:'subsystem', IN:{'attribute', 'lifecycle'} },
                    'attribute':{ OUT:'class', IN:{} },
                    'lifecycle':{ OUT:'class', IN:{'state', 'transition'} },
                        'state':{ OUT:'lifecycle', IN:{} },
                        'state':{ OUT:'transition', IN:{} },
                'relationship':{ OUT:'subsys', IN:{} }
    }

# Unabbreviated model element names
names = { # Indented to show containment hierarchy
    'model',
        'domain',
            'subsystem',
                'class',
                    'attribute',
                    'lifecycle',
                        'state',
                        'transition',
                'relationship',
            'spanning element',
                'cloop',
                'lineage',
                'type',
        'bridge'
    }

# To resolve common abbreviations
alias = {
    'a':'attribute',
    'attr':'attribute',
    'br':'bridge',
    'c':'class',
    'd':'domain',
    'dom':'domain',
    'lcycle':'lifecycle',
    'life':'lifecycle',
    'loop':'cloop',
    'rel':'relationship',
    's':'state',
    'subsys':'subsystem',
    'tr':'transition',
    'trans':'transition'
}

# Class
class Model:
    def __init__( self ):
        """
        Init the model by loading all data and generating the attribute setter code.

        """
        self.app_ui_type_map = {} # app -> raw ui data types
        self.data = { 'domain': {} } # all model data will go here

        # maintain depth of stack while parsing model file
        # level is the current model element depth
        # view is the sub-dictionary within self.data where
        # data is currently being inserted

        # For convenience, the top of the stack is held in the
        # context view.  So data is always inserted in the current
        # context.
        self.context = { 'level':'model', 'view':self.data }
        self.stack = [ ]

        # Map of each application type to a raw ui type
        # nominal : integer and short_name : text, for example.
        # This separation makes it possible to accept raw user input
        # so that it may be validated by the application, which can
        # generate helpful user error messages.
        #
        # Thus the ui may accept an integer, but the app will convert it to
        # an mi.nominal type

        
        # For each class, we designate certain focus and modify attributes.
        # A focus attribute helps address or select a class instance whereas
        # a modify attribute defines a characterstic that may be changed.
        # For example, the Subsystem class is uniquely identified by
        # Subsytem.Name + Subsystem.Domain.  So name, domain are the two focus
        # attributes.  The name and alias may be set to new values, so the
        # modify attributes are name and alias.  To avoid a name collision,
        # the generated code may prefix all modify attributes with 'new_'.

        # The data is organized as a hierarchichal dictionary from schema ->
        # class -> focus and modify attr specs with the app data type specified
        # for each attribute

        # Read metamodel data, but don't parse it yet
        self.import_lines = Structured_File( os.path.join( RESOURCE_DIR, MODELFILE ) )

        # Parse out the app / ui type data
        self.unpack_type_lines()

        # Parse out the attribute data
        self.unpack_model_lines()

        # Generate the attribute setter code
        self.gen_setter_code()

    def unpack_type_lines( self ):
        """
        Populate the app_ui_type_map

        """
        # Creates dictionary entries from colon delmited pairs
        # (each line has the same format so processing is easy)
        for line in self.import_lines.sections['Types']:
            app_type, base_type = line.strip().split(':')
            self.app_ui_type_map[app_type.strip()] = base_type.strip()

    def unpack_model_lines( self ):
        """
        Populate the model data dictionary

        """
        for n, line in enumerate(self.import_lines.sections['Model']):
            me_type, me_key, mdict = parse( n, line, MODELFILE )
            # model element type, key, and parsed data

            if me_type == 'properties':
                # This is just a set of properties
                self.context['view'][me_type].update( mdict )
                continue

            if me_type not in names:
                # It may be an alias, convert to full name
                try:
                    me_type = alias[me_type]
                except:
                    # No alias found
                    raise mi_Error( "Unknown model element: " + me_type )

            # Promote context if necessary
            while True:
                if me_type in mtax[ self.context['level'] ][IN]:
                    self.stack.append( self.context ) # Dropping down a level
                    break
                if not self.stack:
                    # At top of stack, and model element not recognized
                    raise mi_Error( 'Stack top: Model element not recognized' )
                # Change context to next higher on stack
                self.context = None
                self.context = self.stack.pop()


            # Insert data into current view
            self.context['view'][me_type].update( mdict )

            # Update current context and push it on the stack
            self.context = None # Break reference to stack
            self.context = { 'level':me_type, 'view':self.stack[TOP]['view'][me_type][me_key] }

            # Add empty subfields for next level down
            for ch in mtax[me_type][IN]:
                self.context['view'][ch] = {}
            continue

    def gen_setter_code( self ):
        """
        Generate the attribute setters for each schema

        """
        subsystems = self.data['domain']['miUML Metamodel']['subsystem']
        for s in subsystems:
            subsys_alias = subsystems[s]['properties']['alias']
            for c in subsystems[s]['class']:
                # Make attributes
                attrs = dict( modify={}, focus={} )

                attr_data = subsystems[s]['class'][c]['attribute']
                for a in attr_data:
                    a_props = attr_data[a]['properties']

                    # Now we categorize the attribute as focus, modify or both
                    # A focus attribute selects the object to update
                    # A modify attribute may be set to some value

                    if not ('ref' in a_props) and not ('id' in a_props and 'default' in a_props):
                        # All non-referential attributes that do not specify
                        # a default (singleton focus) may be modified
                        # so include in the modify category.  (You can change the
                        # name of a subystem, for example, but not a singleton)

                        # Set its default property as specified or a db "null"
                        attrs['modify'].update({a:{'type':a_props['type'], 'default':"null"}})

                    if 'id' in a_props and '1' in a_props['id']:
                        # By convention, each primary identifier attribute will be
                        # used to select, so it will be in the focus category

                        # There is never a default for a non-singleton focus
                        # attr, since it is necessary to select a particular instance.
                        # However, where there is a singleton, the focus attr will specify
                        # a default name because a setter requires at least one
                        # focus attribute to perform a select in the generated code
                        d = "" if 'default' not in a_props else \
                            " default '{}'".format( a_props['default'] )
                        # The space before 'default' is included here since we only need
                        # it in this rare case.  Otherwise, the template would specify a
                        # trailing space with no following default all the time.
                        attrs['focus'].update({a:{'type':a_props['type'], 'default':d}})

                mi_Template_Domain.client_gen_setters(
                        s, subsys_alias, c, attrs,
                        self.app_ui_type_map
                    )


if __name__ == '__main__':
    m = Model()

    # By creating a model we load the metamodel data and then
    # generate any related code
    # For now, the both code and metamodel data is quite limited
