import logging
import os
import test

from hints import HintFile, HintFormatError
from nose.tools import raises

# Keys that are being checked
valid_meta_keys = ['created', 'author']
valid_hint_keys = ['text', 'places']

class TestHintsLoader(object):
    """Hints loader tests"""

    def test_correct_file(self):
        """Asserts that all supported key-value pairs are read correctly
        from correct JSON.
        This is implemented by comparison with predefined python dict_enum.
        Currently, following keys are asserted:
        * created
        * author
        """
        hints_file_name = 'example/test_hints_all_correct.txt.hints'
        if not os.path.exists(hints_file_name):
            logging.error("Hint file %s not found", hints_file_name)
            return
        hint_file = HintFile.load_json(test._current_view, hints_file_name)
        from example import test_hints_all_correct_pydict
        for key in valid_meta_keys:
            try:
                value = getattr(hint_file.meta, key)
            except AttributeError:
                logging.exception("No key '%s' is found in file %s", key, hints_file_name)
            assert value == test_hints_all_correct_pydict.hints_all_correct['key']
            # ToDo: implement hint assertions

    @raises(HintFormatError)
    def test_missing_hints(self):
        """Asserts that HintFormatError is raised when given JSON
        doesn't have "hints" key
        """
        hints_file_name = 'test/hints/no-hints.hints'
        if not os.path.exists(hints_file_name):
            logging.error("Hint file %s not found", hints_file_name)
            return
        HintFile.load_json(test._current_view, hints_file_name)