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

# Local
from mi_Error import *
from mi_Tag import *
from mi_Fill_Pattern import Fill_Pattern

# Diagnostic
import pdb

# Regex
trailing_comment = re.compile( r'\s*--.*$' ) # Specific to plpgsql (should be configurable)

# Constants
MIN_SPACE = 2
COL_DELIM = '|t|' # Column delimiter (for evenly spaced columns)

# Class
class Expansion_Block:
    """
    Expansion block

    """
    def __init__( self, template, etags ):
        self.template = template
        self.etags = etags # Expansion tags filled in for this block

        # While template lines are added to this expansion block
        # conditional processing is noted by the following attributes
        self.active_condition = None # Apply to each added template line
        self.conditions = {} # All conditions defined for this block

        # Skip this block if no expanding tag values were supplied
        # for this block's etags.  Any template lines within the block will
        # be skipped and no expansing/flush will occur.
        self.skip = set(self.etags).isdisjoint( set(expanding_tag) )

        self.template_lines = []
        self.filled_lines = []
        self.col_widths = []

    def set_condition( self, condition ):
        """
        New condition will apply to subsequent lines read in from template.

        """
        # Remember to associate with each subsequent line
        self.active_condition = condition

        # Save for evaluation and comparison during expansion
        self.conditions[self.active_condition] = None # Not yet evaluated

    def close_condition( self ):
        """
        The active condition no longer applies to subsequent lines.

        """
        self.active_condition = None # But still saved in conditions set

    def expand( self ):
        """
        Substitute tags and repeat for each etag member

        """
        if self.skip:
            return

        # Index through first etag (any would do)
        for i, value in enumerate( expanding_tag[self.etags[0]] ):

            # So now we have the i'th value in some etag
            # Set a fill for the i'th value in all of the etags used in this block
            for e in self.etags:
                fill[e] = expanding_tag[e][i]

            # Now expand all template lines in the block using the fills
            # for this i'th value of the etags

            # Evaluate any conditions for this i'th fill
            # All of this block's conditions are assumed to use only
            # fills for our etags (otherwise, poorly formed template)
            for c in self.conditions.keys():
                self.conditions[c] = False # Clears prior evaluation to default False
                bound_cond = Fill_Pattern( c ).filled_out_text # replace variable with value
                if eval(bound_cond):
                    self.conditions[c] = True # Evaluation is valid throughout i'th value

            # Fill in blanks for all lines in block using current fill values
            first_line = True
            for this_line in self.template_lines:

                if this_line[1]['condition']: # There is a condition
                    if not self.conditions[this_line[1]['condition']]:
                        continue

                # Fill out the tags values and append to this block
                filled_line = Fill_Pattern( this_line[0] ).filled_out_text
                self.filled_lines.append( filled_line )

                # Record max column lengths if there is more than one column
                columns = filled_line.split( COL_DELIM )
                if len(columns) < 2:
                    continue # No columns

                # Record longest text for each column
                for cnum, txt in enumerate(columns[:-1]):
                    # For the first filled line, the first test will always fail
                    if not first_line:
                        self.col_widths[cnum] = max( len(txt), self.col_widths[cnum] )
                    else:
                        self.col_widths.append( len(txt) )
                first_line = False

        # Current fills have been set for every etag used in this block
        # Pad any tabbed columns (using spaces instead)
        for lnum, tline in enumerate(self.filled_lines):
            columns = tline.split( COL_DELIM )
            if len(columns) < 2:
                continue # No columns
            tline = ""
            for cnum, txt in enumerate(columns[:-1]):
                space = MIN_SPACE + self.col_widths[cnum] - len(txt)
                tline += ( txt + ' '*space )
            self.filled_lines[lnum] = tline + columns[-1]

        if not self.filled_lines:
            # Don't save or flush this block if it is empty, just forget it
            return

        if self.template.list_region:
            # If part of a list, save for later output
            self.template.list_region.add_block( self )
            return

        # Not part of a list, so just flush all expanded lines to output
        self.flush()

    def append( self, line ):
        """
        Add this line for later processing

        """
        if self.skip:
            return # Line is ignored

        # Add line along with active condition, if any
        self.template_lines.append(
                [line, {'condition':self.active_condition if self.active_condition else None} ]
            )

    def trim( self, delimiter ):
        """
        Removes trailing delimiter from last line

        """
        # Seems simple enough, get the last line in the block and chop off
        # the delimiter

        # This is tricky because there may be a trailing comment.
        # So we need to chop off any such comment, remove the delimiter
        # if it exists, and then make sure we don't lose the newline

        # Temoprarily drop the newline from the last line in the block
        last_nonl = self.filled_lines[-1].strip("\n")
        comment_text = "" # May or may not exist

        # Is there a trailing comment?
        r = trailing_comment.search( last_nonl )
        if r:
            # Chop it off, but save it for later
            last_nonl = last_nonl[:r.start()]
            comment_text = r.group()

        # Now drop the delimiter and put the rest back
        self.filled_lines[-1] = last_nonl.strip(delimiter) + comment_text + "\n"

    def flush( self ):
        """
        Flush lines out to Target

        """
        for l in self.filled_lines:
            self.template.target.lines.append( l )
