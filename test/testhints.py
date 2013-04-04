import logging
import os
import test

from hints import HintFile, HintFormatError
from nose.tools import raises

class TestHintsLoader(object):
    """Hints loader tests"""

    @raises(HintFormatError)
    def test_missing_hints(self):
        """Asserts that HintFormatError is raised when given JSON
        doesn't have "hints" key
        """
        hints_file_name = "test/hints/no-hints.hints"
        if not os.path.exists(hints_file_name):
            logging.info("Hint file %s not found", hints_file_name)
            return
        HintFile.load_json(test._current_view, hints_file_name)