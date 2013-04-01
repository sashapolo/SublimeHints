import json
import logging
#from nose.tools import *
import os
import sys

from hints import *

class TestHintsLoader():
    """ Hints loader tests
    """

#    @raises(HintFormatError)
    def test_missing_hints(self):
        """ Asserts that HintFormatError is raised when given JSON
        doesn't have "hints" key
        """
        hints_file_name = "no-hints.hints"
        if not os.path.exists(hints_file_name):
            logging.info("Hint file %s not found", hints_file_name)
            return
        with open(hints_file_name, 'r') as hints_file:
            HintFile.load_json(self.view, hints_file)
