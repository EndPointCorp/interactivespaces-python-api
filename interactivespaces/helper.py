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
    def wrap(self, regular_expression):
        """
        Turns windows/search type of regexp into python re regexp.
        It adds explicit begining '^' and end '$' to matcher and converts
        all wildcards to re wildcard '(.*)'

        :rtype: str
        :param string: regular_expression
        """
        return '^' + regular_expression.replace('*','(.*)') + '$'

    def match(self, string, regular_expression):
        """
        Match string with a regular expression

        :rtype: bool

        :param string: given string for matching

        :param regular_expression: expression to be run against the given string
        """
        regular_expression = self.wrap(regular_expression)

        regex = re.compile(regular_expression)
        if re.match(regex, string):
            return True
        else:
            return False
