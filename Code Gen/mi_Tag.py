#! /usr/bin/env python

"""
Current and expanding fill values are defined here.

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


fill = {} # Current fill values
# A fill holds the value to be filled in for any corresponding tag replaced
# in a template line.  For example, let's say that fill['year'] = 2012.  Then
# anywhere the tag <year> is encountered, it will be replaced by 2012.

expanding_tag = {} # Set of fill values to be supplied during block expansion
# An expanding tag will specify multiple fills, one for each expansion within
# an expansion block.  If there are two values, 'color' and 'size' supplied for
# the expanding tag <modify_attribute>, for example, it will be filled in differently
# for each expansion.
#
# In fact, for each expansion, a corresponding fill will be set.  So
# fill['modify_attribute'] will be 'color' in one expansion and then reset to
# 'size' in another.
