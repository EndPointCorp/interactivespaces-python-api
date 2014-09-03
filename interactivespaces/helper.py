#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

class SearchPattern(dict):
    """
    Class that holds dictionary with default values for safe search patterns
    """
    def __missing__(self,key):
        return None

    def __setitem__(self, key, value):
        if value==None:
            if key in self:  # returns zero anyway, so no need to store it
                del self[key]
        else:
            dict.__setitem__(self, key, value)

class Searcher(dict):
    """
         Class responsible for search methods on strings
    """
    def match(self, string, regular_expression):
        """
        Match string with a regular expression
        
        :rtype: bool
        
        :param string: given string for matching
        
        :param regular_expression: expression to be run against the given string
        """
        regex = re.compile(regular_expression)
        if re.match(regex, string):
            return True
        else:
            return False
