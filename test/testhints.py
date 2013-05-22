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
        hints_file_name = 'test/hintfiles/correct.hints'
        if not os.path.exists(hints_file_name):
            logging.error("Hint file %s not found", hints_file_name)
            return
        hint_file = HintFile.load_json(test._current_view, hints_file_name)
        from hintfiles import correct_pydict
        for key in valid_meta_keys:
            try:
                value = getattr(hint_file.meta, key)
            except AttributeError:
                logging.exception("No key '%s' is found in file %s", key, hints_file_name)
                # ToDo: ?assertFail?
                assert False
            assert value == correct_pydict.filedata[key]
            # ToDo: implement hint assertions

    @raises(HintFormatError)
    def test_missing_hints(self):
        """Asserts that HintFormatError is raised when given JSON
        doesn't have "hints" key
        """
        hints_file_name = 'test/hintfiles/no_hints.hints'
        if not os.path.exists(hints_file_name):
            logging.error("Hint file %s not found", hints_file_name)
            return
        HintFile.load_json(test._current_view, hints_file_name)

    @raises(HintFormatError)
    def test_missing_places(self):
        """Asserts that HintFormatError is raised when given JSON
        doesn't have "places" key in hint
        """
        hints_file_name = 'test/hintfiles/no_places_in_hint.hints'
        if not os.path.exists(hints_file_name):
            logging.error("Hint file %s not found", hints_file_name)
            return
        HintFile.load_json(test._current_view, hints_file_name)

    @raises(HintFormatError)
    def test_illegal_places(self):
        """Asserts that HintFormatError is raised when given JSON
        has illegal value by "places" key in hint
        """
        hints_file_name = 'test/hintfiles/illegal_places_in_hint.hints'
        if not os.path.exists(hints_file_name):
            logging.error("Hint file %s not found", hints_file_name)
            return
        HintFile.load_json(test._current_view, hints_file_name)

    @raises(HintFormatError)
    def test_missing_text(self):
        """Asserts that HintFormatError is raised when given JSON
        doesn't have "text" key in hint
        """
        hints_file_name = 'test/hintfiles/no_text_in_hint.hints'
        if not os.path.exists(hints_file_name):
            logging.error("Hint file %s not found", hints_file_name)
            return
        HintFile.load_json(test._current_view, hints_file_name)

    @raises(HintFormatError)
    def test_unknown_key(self):
        """Asserts that HintFormatError is raised when given JSON
        has unknown key in hint
        """
        hints_file_name = 'test/hintfiles/unknown_keys_in_hint.hints'
        if not os.path.exists(hints_file_name):
            logging.error("Hint file %s not found", hints_file_name)
            return
        HintFile.load_json(test._current_view, hints_file_name)
