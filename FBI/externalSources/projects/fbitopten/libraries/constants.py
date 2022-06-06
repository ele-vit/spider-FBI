#!/usr/bin/python

class Constants:

    """

    Class that allows to manage the constant variables of the program,

    is carried out as a class and using the hint @properties to ensure

    that the value is not modified during the time of execution.

    """

    def __init__(self):
        self.__WANTEDS = '''{{  "mostWanted"  :   {wanteds}      }}'''


    @property
    def WANTEDS(self):

        """
        Allows to return the name affiliation section.
        """
        return self.__WANTEDS
