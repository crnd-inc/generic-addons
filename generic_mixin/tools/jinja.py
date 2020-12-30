import logging
import datetime
import functools
from werkzeug import urls
from dateutil.relativedelta import relativedelta
from jinja2.sandbox import SandboxedEnvironment
from odoo import tools

_logger = logging.getLogger(__name__)

# Jinja template environment
template_env = SandboxedEnvironment(
    trim_blocks=True,               # do not output newline after blocks
    autoescape=True,                # XML/HTML automatic escaping
)
template_env.globals.update({
    'str': str,
    'quote': urls.url_quote,
    'urlencode': urls.url_encode,
    'datetime': datetime,
    'len': len,
    'abs': abs,
    'min': min,
    'max': max,
    'sum': sum,
    'filter': filter,
    'reduce': functools.reduce,
    'map': map,
    'round': round,

    # dateutil.relativedelta is an old-style class and cannot be directly
    # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
    # is needed, apparently.
    # pylint: disable=unnecessary-lambda
    'relativedelta': lambda *a, **kw: relativedelta.relativedelta(*a, **kw),
})


def render_jinja_string(template_str, context, on_error='empty'):
    """ on_error values:
            raw: return template_str unchanged
            raise: reraise error
            empty: return empty string
    """
    # Compile template
    try:
        template = template_env.from_string(tools.ustr(template_str))
    except Exception:
        _logger.error(
            "Cannot parse template:\n\n---\n\n%s\n\n---\n",
            template, exc_info=True)
        if on_error == 'raw':
            return template_str
        if on_error == 'raise':
            raise
        return ''

    # Render template
    try:
        result = template.render(context)
    except Exception:
        _logger.error(
            "Cannot render template:\n\n---\n\n%s\n\n---\n",
            template, exc_info=True)
        if on_error == 'raw':
            return template_str
        if on_error == 'raise':
            raise
        return ''
    return result
