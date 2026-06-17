import bleach
import markdown as md

MD_EXTENSIONS = [
    'fenced_code',
    'codehilite',
    'tables',
    'nl2br',
]

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 's', 'a', 'hr',
    'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td',
    'span', 'div',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'code': ['class'],
    'pre': ['class'],
    'span': ['class'],
    'th': ['align'],
    'td': ['align'],
}


def render_markdown(text):
    if not text:
        return ''
    html = md.markdown(text, extensions=MD_EXTENSIONS)
    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
