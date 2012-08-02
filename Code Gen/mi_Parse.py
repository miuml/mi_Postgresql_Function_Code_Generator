#! /usr/bin/env python

"""
Parse - Functions to parse an mi import file.

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

def parse( record_no, record, filename ):
    """
    """
    global _filename
    _filename = filename
    global _record_no
    _record_no = record

    if ':' in record:
        return parse_entity_record( record )

    return 'properties', None, parse_property_record( record )

def parse_entity_record( record ):
    """
    Process record that specifies an entity type

    """
    # Split the record on the required colon delimiter
    try:
        left, right = record.strip().split(':')
    except ValueError:

        # Colon missing
        raise mi_Parse_Error( "Colon missing", _filename, _record_no, record ) 

    # [Assertion 1] There must be a colon delmiter with data on each side
    if not left or not right:
        raise mi_Parse_Error( "Data missing on colon", _filename, _record_no, record ) 

    model_element_type = left.strip()

    if ',' in right:
        name_data, property_record = right.strip().split(', ', 1)
    else:
        name_data = right.strip()
        property_record = None

    if '/' not in name_data:
        # By default, the model element Name is it's dictionary key
        name_key = 'Name'
        name_value = name_data.strip()
    else:
        # / means that key other than Name (Rnum, for example) is specified
        # Use that instead
        name_value, name_key = [f.strip() for f in name_data.split('/')]
        if not name_key or not name_value:
            # Correct format is <name_value> / <name_key>
            raise mi_Parse_Error(
                "Format: <name_value> / <name_key>", _filename, _record_no, record
            ) 

    mdict = { name_value : { 'name_key' : name_key } }

    # Add properties key with data, if there was a property_record otherwise, empty set
    mdict[name_value]['properties'] = \
        {} if not property_record else parse_property_record( property_record )

    return model_element_type, name_value, mdict


def parse_property_record( record ):
    """

    """
    if '=' not in record:
        raise mi_Error( _filename, record )
    return { k.strip() : v.strip() for (k, v) in [ t.split('=') for t in record.split(',') ] }

if __name__ == '__main__':
    test_records = (
        "domain: Air Traffic Control, alias=ATC",
        "subsystem: Landing Patterns / Title, alias=LP",
        "class: Aircraft", 
        "alias=AIR"
    )
    print()
    for r in test_records:
        e, m = parse( r, "somefile.mi")
        print( "Record: [{}]".format(r) )
        print( "Parse: {}, {}".format(e, m) )
        print()


