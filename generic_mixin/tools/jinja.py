import logging
import datetime
import functools
import pytz
from werkzeug import urls
from dateutil.relativedelta import relativedelta
from jinja2.sandbox import SandboxedEnvironment

_logger = logging.getLogger(__name__)


def prepare_jinja_template_env(env_kwargs=None, extra_context=None):
    """ Prepare custom jinja2 template environment.
    """
    env_params = {
        'trim_blocks': True,               # do not output newline after blocks
        'autoescape': True,                # XML/HTML automatic escaping
    }
    if env_kwargs:
        env_params.update(env_kwargs)

    env = SandboxedEnvironment(**env_params)

    def as_timezone(dt, tz_name='UTC'):
        """ Convert datetime to specified timezone
            :param datetime dt: datetime object to convert
            :param str tz_name:
                name of timezone to convert to (e.g. 'UTC', 'Europe/Kiev')
            :return: formatted datetime string without timezone info
        """
        if not dt:
            return dt

        if isinstance(dt, str):
            dt = datetime.datetime.fromisoformat(dt)

        if not dt.tzinfo:
            # Assume naive datetime is in UTC
            dt = pytz.UTC.localize(dt)

        target_tz = pytz.timezone(tz_name)
        dt_with_tz = dt.astimezone(target_tz)

        # Return datetime formatted as string without timezone info
        return dt_with_tz.strftime('%Y-%m-%d %H:%M:%S')

    env_ctx = {
        'str': str,
        'quote': urls.url_quote,
        'urlencode': urls.url_encode,
        'datetime': datetime,
        'pytz': pytz,
        'as_timezone': as_timezone,
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
        'relativedelta': lambda *a, **kw: (
            relativedelta.relativedelta(*a, **kw)),
    }
    if extra_context:
        env_ctx.update(extra_context)

    env.globals.update(env_ctx)
    return env


def render_jinja_string(template_str, context, on_error='empty', env=None):
    """ :param str template_str: Template string to process with jinja
        :param dict context: Additional context to pass to template
        :param str on_error: Possible values are:
            raw: return template_str unchanged
            raise: reraise error
            empty: return empty string
        :param jinja2.sandbox.SandboxedEnvironment env: specific sendbox env
           if needed
    """
    template_env = prepare_jinja_template_env() if env is None else env

    # Compile template
    try:
        template = template_env.from_string(template_str)
    except Exception:
        _logger.error(
            "Cannot parse template:\n\n---\n\n%s\n\n---\n",
            template_str, exc_info=True)
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
            template_str, exc_info=True)
        if on_error == 'raw':
            return template_str
        if on_error == 'raise':
            raise
        return ''
    return result
