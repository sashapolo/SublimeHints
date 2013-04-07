# vim: set fileencoding=utf-8 :

import tempfile
import webbrowser
import os
import logging

from SublimeHints import HintsRenderer, SublimeUtilMixin, LIB_DIRECTORY
from jinja2 import Environment, FileSystemLoader, escape, Markup, contextfilter


logger = logging.getLogger('SublimeHints.viewers.browser')
logger.setLevel(logging.DEBUG)

PACKAGE_DIRECTORY = os.path.dirname(__file__)
env = Environment(loader=FileSystemLoader(os.path.join(PACKAGE_DIRECTORY, 'templates')))
env.globals['static_files_location'] = os.path.join(PACKAGE_DIRECTORY, 'static')
env.globals['highlightjs_location'] = os.path.join(LIB_DIRECTORY, 'highlight.js')

@contextfilter
def inject_hints(context, code):
    """This filter scans through given hints (if such variable defined
    in the context) and insert corresponding <span> tags around specified
    regions. It also escapes code fragment and wrap it in Markup object
    to prevent possible double escaping in template.
    """
    def region_to_pair(region):
        return (region.begin(), region.end())
    if 'hints' not in context:
        return escape(code)
    hints = context['hints']
    bounds = set([0, len(code)])
    for hint in hints:
        hint.places = map(region_to_pair, hint.places)
        bounds.update(*hint.places)
    bounds = sorted(list(bounds))
    regions = zip(bounds[:-1], bounds[1:])
    code_chunks = []
    for start, end in regions:
        escaped_fragment = escape(code[start:end])
        if not escaped_fragment:
            continue
        classes = []
        for i, hint in enumerate(hints):
            if filter(lambda p: p[0] <= start and end <= p[1], hint.places):
                classes.append('hint%d' % i)
        if classes:
            escaped_fragment = '<span class="%s">%s</span>' % (' '.join(classes), escaped_fragment)
        code_chunks.append(escaped_fragment)

    preprocessed = ''.join(code_chunks)
    if context.eval_ctx.autoescape:
        return Markup(preprocessed)
    return preprocessed

env.filters['inject_hints'] = inject_hints


class BrowserViewCommand(HintsRenderer):
    def __init__(self, view):
        super(BrowserViewCommand, self).__init__(view)

    def render(self, hints_file):
        logger.debug('Module name: ' + __name__)
        logger.debug('Module path: ' + __file__)
        _, tmp_file = tempfile.mkstemp(suffix='.xhtml')
        logger.info('Temporary file generated: %s', tmp_file)
        env.get_template('layout.xhtml').stream(
            title=self.file_name(),
            filetype=self.file_type(),
            code=self.file_content(),
            hints=hints_file.hints
        ).dump(tmp_file, encoding='utf-8')
        webbrowser.open_new_tab(tmp_file)