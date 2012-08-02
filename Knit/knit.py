#! /usr/bin/env python

"""
Knit

Processes the hand code subdirectories of each subsystem directory and, for each
hand coded file, splices the content into the designated section of a corresponding
generated file in the parent directory.  Both the hand coded file in its special
subdirectory and the corresponding generated file in a parent directory share the
same file name.

It is assumed that this program executes in the directory which contains all of the
subsystem directories.

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
import os
import glob
import sys

# Local
_MODULE_DIR = os.path.abspath("../Modules")
sys.path.append(_MODULE_DIR)
from mi_Error import *

# Diagnostic
import pdb # debug

# Constants
_GLOB_SUFFIX = "*.sql"
_START_SECTION = "-- ++"
_END_SECTION = "-- =="
_DEFAULT_PROJECT_HOME = "miumlhome" # Environment var name

# Global
hand_code = {}

def read_hand_code( hand_code_file ):
    """
    Read all lines between named section headers into the hand_code
    dictionary.

    """
    # Read all the hand code
    try:
        hcfile = open( hand_code_filename )
    except:
        raise mi_File_Error( 'Could not read', hand_code_filename )

    this_section = None
    global hand_code

    for line in hcfile:

        if line.lstrip().startswith(_START_SECTION):
            # Start a new section.  The name is the first non-space word to the right
            # of the start section marker.
            this_section = line.split( _START_SECTION )[1].strip().split()[0].lower()
            if not this_section:
                raise mi_Error( "Bad section header start in hand code file" )
            hand_code[this_section] = []
            continue

        if line.lstrip().startswith(_END_SECTION):
            this_section = None # Now we are between sections
            continue

        if this_section:
            # Inside a section, append line
            hand_code[this_section].append( line )

def splice_hand_code( gen_file ):
    """
    Splice (insert) each section at the correspondng section marker
    in the generated code file.

    """
    try:
        gen_file = open( gen_filename )
    except:
        raise mi_File_Error( "Could not open", gen_filename )

    global hand_code
    target_lines = []
    inside_splice_section = False

    for line in gen_file:

        if line.lstrip().startswith(_START_SECTION):
            target_lines.append( line )
            this_section = line.split( _START_SECTION )[1].strip().split()[0].lower()
            if not this_section:
                raise mi_Error( "Bad section header start in gen code file" )
            if this_section in hand_code:
                inside_splice_section = True
                target_lines.extend( hand_code[this_section] )
                del hand_code[this_section] # So it won't be reinserted
            continue

        if line.lstrip().startswith(_END_SECTION):
            inside_splice_section = False
            target_lines.append(line)
            continue

        if not inside_splice_section:
            target_lines.append( line )

    try:
        # Write out the target lines buffer
        with open( gen_filename, 'w' ) as gen_file:
            gen_file.write( ''.join( target_lines ) )
    except:
        raise mi_File_Error( "Could not write", gen_filename )

# Main

hand_code_dirs = ( 'Hand', 'Comments' )

# Set project_dir
if len(sys.argv) > 2:
    print( "Usage: knit [<project home dir>]" )
    exit(1)

if len(sys.argv) == 2:
    project_dir = sys.argv[1]
else:
    try:
        project_dir = os.getenv( _DEFAULT_PROJECT_HOME )
    except:
        print( "Usage: knit <project home dir>" )
        print( "or set: {} environment variable to project home dir".format(
            _DEFAULT_PROJECT_HOME ) )
        exit(1)

# cd into the project home directory
try:
    os.chdir( project_dir )
except:
    print( "Could not access project home directory: " + project_dir )
    exit(1)

print()
print("Knitting hand code below: " + project_dir )

# Get all subdirectories (all or most of which should be subsystems)
# Hidden directories are excluded by glob (as opposed to os.listdir())
subsys_dirs = [ f for f in glob.glob('*') if os.path.isdir(f) ]

for subsys in subsys_dirs:
    # Process if it contains a hand code subdirectory
    try:
        os.chdir( project_dir + os.sep + subsys )
    except:
        print( "Could not access subdir: {}  Skipped.".format( d ) )
        continue

    # Assert: In project_dir/subsystem_dir

    print( "   Processing subsystem: " + subsys )
    subdirs = { f for f in os.listdir() if os.path.isdir(f) and not f.startswith('.') }
    for hc_dir in hand_code_dirs:
        # There may be a directory here containing hand written comments or code
        # If not, just move on to the next subsystem directory
        if hc_dir in subdirs:
            # There's a hand code dir in this subdir, cd into it
            try:
                os.chdir( hc_dir )
            except:
                # Maybe subdirs is stale?
                print( "Could not access dir: {}  Skipping.".format(
                    subsys + os.sep + hc_dir
                ) )
                continue

            # Assert: In project_dir/subsystem_dir/knit_dir

            for hand_code_filename in glob.glob( _GLOB_SUFFIX ):
                print("      Knitting: " + hand_code_filename )

                # The target gen'd file will have the same name in the parent dir
                gen_filename = os.pardir + os.sep + hand_code_filename

                # Read all the hand code and break into sections
                read_hand_code( hand_code_filename )

                # Splice in each section into the designated location in the gen file
                splice_hand_code( gen_filename )
        
            try:
                os.chdir( os.pardir ) # pop back up into the subsys dir
            except:
                raise mi_Error( "Could not return to parent dir: {}  Abort.".format(
                    os.abspath(subsys)
                ) )
