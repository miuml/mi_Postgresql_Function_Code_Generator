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

# System
import re
import os

# Local
from mi_Structured_File import Structured_File
from mi_Error import *
from mi_Tag import * # fill and expanding_tag globals
from mi_Expansion_Block import Expansion_Block
from mi_Fill_Pattern import Fill_Pattern
from mi_List_Region import List_Region
from mi_Target import Target

# Diagnostic
import pdb

# Class
class Template:
    """
    Reference file with tags and commands referenced to generate target output such
    as code

    """
    commands = None # Initialized after class definitions

    def __init__( self, name, file_name, target_name_pattern ):
        self.name = name
        self.lines = []
        self.file_name = os.path.join( "Resources", file_name )
        codegen_path = os.getenv( "micodegen", False )
        if not codegen_path:
            raise mi_Error( "micodegen env variable not set." )
        self.target_name_pattern = target_name_pattern
        self.target = None
        self.list_region = None
        self.expansion_block = None

    def process( self, line ):
        for f, p in Template.commands:
            r = p.match( line )
            if r:
                f( self, r, line )
                return
        raise mi_Error( 'No case matched' )

    # Functions below correspond to an RE which recognizes a certain type
    # of line encountered in a template.  When the RE is recognized during
    # template processing, the function is invoked and passed the line and
    # RE match object

    def non_command( self, r, line ):
        """
        Process a non-command line.

        """
        if self.expansion_block:
            # Add it to the current expansion block
            self.expansion_block.append( line ) # Append is defined specially
            return

        # Fill out the line
        filled_out_line = Fill_Pattern( line ).filled_out_text

        if self.list_region:
            # Intersitial text to be flushed between blocks
            self.list_region.interstitial( filled_out_line )
            return

        # No expansion block or list region active, just flush to target
        self.target.lines.append( filled_out_line )

    def begin_list( self, r, line ):
        """
        Process begin list command.

        """
        if self.list_region:
            raise mi_Error( "List already open." )
        if self.expansion_block:
            raise mi_Error( "List begins during open expansion block." )
        # Create a new list region with the specified delimiter
        self.list_region = List_Region( template=self, delimiter=r.groupdict()['delimiter'] )

    def begin_cond( self, r, line ):
        """
        Create a new conditional segment in the active expansion block

        """
        if not self.expansion_block:
            raise mi_Error("Conditional segment specified outside of any expansion block!")

        self.expansion_block.set_condition( r.groups('condition')[0] )

    def end_cond( self, r, line ):
        """
        Tell expansion block to stop accepting conditional lines

        """
        if not self.expansion_block:
            raise mi_Error("Conditional segment closed outside of any expansion block!")

        self.expansion_block.close_condition();

    def begin_expand( self, r, line ):
        """
        Start a new expansion block

        """
        if self.expansion_block:
            raise mi_Error( "Expansion block already open!" )
        try:
            etag_fill = re.findall( '\w+', line.split(':')[1] )
        except IndexError:
            raise mi_Error( "Missing colon in begin expansion." )
        if not etag_fill:
            raise mi_Error( "Expansion block has no fill values." )
        self.expansion_block = Expansion_Block( self, etag_fill )

    def end_expand( self, r, line ):
        """
        End the current expansion block

        """
        if not self.expansion_block:
            raise mi_Error( "Unbalanced expansion block ending." )
        self.expansion_block.expand()
        self.expansion_block = None

    def end_list( self, r, line ):
        """
        End the current list

        """
        if not self.list_region:
            raise mi_Error( "Unbalanced list end." )
        if self.expansion_block:
            raise mi_Error( "List closed while expansion block open." )
        self.list_region.terminate()

    def fill_out( self, subsys_dir ):
        """
        Generate target output using template data and supplied tag values

        """
        print( "Filling out template: {} for schema: {} using: {}".format(
                self.name, fill['schema'], self.file_name ) )

        # Create the target
        self.target = Target(
            subsys_dir, Fill_Pattern( self.target_name_pattern ).filled_out_text
        )

        # Read each line of the template and generate target line or lines
        self.file = open( self.file_name )
        for line in self.file:
            self.process( line )
        self.file.close()
        try:
            self.target.write()
        except mi_File_Error:
            exit()

# Population

# RE's to recognize each template line ordered with the least restrictive
# at the end.  All but the last are commands, so named 'commands'.
# When the RE is matched, the corresponding Template.<function> is invoked.
Template.commands = (
    ( Template.begin_expand, re.compile( r'^\s*\*\s*expand' ) ),
    ( Template.begin_cond, re.compile( r'^\s*\*\s*conditional:(?P<condition>.*)$' ) ),
    ( Template.begin_list, re.compile( r'^\s*\*\s*list\s*(?P<delimiter>\S+)$' ) ),
    ( Template.end_expand, re.compile( r'^\s*\*{2}\s*expand' ) ),
    ( Template.end_cond, re.compile( r'^\s*\*{2}\s*conditional' ) ),
    ( Template.end_list, re.compile( r'^\s*\*{2}\s*list' ) ),
    ( Template.non_command, re.compile( r'^.*$' ) )
)

if __name__ == '__main__':
    print( "Cannot be run from the command line." )
