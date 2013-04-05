# vim: set fileencoding=utf-8 :

from jinja2 import Environment, FileSystemLoader, escape, Markup, contextfilter
env = Environment(loader=FileSystemLoader('templates/'))

SAMPLE_HINTS = [
    {'places': [(0, 30), (500, 600)], 'content': 'Take a look'},
    {'places': [(5, 20)], 'content': 'Nice solution!'},
    {'places': [(30, 100)], 'content': 'Spam!'},
]

@contextfilter
def inject_hints(context, code):
    if 'hints' not in context:
        return escape(code)
    hints = context.resolve('hints')
    bounds = {0, len(code)}
    for hint in hints:
        bounds.update(*hint['places'])
    bounds = sorted(list(bounds))
    regions = zip(bounds[:-1], bounds[1:])
    code_chunks = []
    for start, end in regions:
        escaped_fragment = escape(code[start:end])
        if not escaped_fragment:
            continue
        classes = []
        for i, hint in enumerate(hints):
            if filter(lambda p: p[0] <= start and end <= p[1], hint['places']):
                classes.append('hint%d' % i)
        if classes:
            escaped_fragment = '<span class="%s">%s</span>' % (' '.join(classes), escaped_fragment)
        code_chunks.append(escaped_fragment)

    preprocessed = ''.join(code_chunks)
    if context.eval_ctx.autoescape:
        return Markup(preprocessed)
    return preprocessed

env.filters['inject_hints'] = inject_hints

def main():
    with open('main.py') as source_file:
        source = source_file.read()

    env.get_template('layout.xhtml').stream(
        title='Spam!',
        code=source,
        hints=SAMPLE_HINTS
    ).dump('output/rendered.xhtml', encoding='utf-8')

if __name__ == '__main__':
    main()
