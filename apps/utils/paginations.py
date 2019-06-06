from __future__ import unicode_literals

from base64 import b64encode
from collections import namedtuple

from django.utils.encoding import force_str
from django.utils.six.moves.urllib import parse as urlparse
from rest_framework.pagination import CursorPagination, _positive_int

Cursor = namedtuple('Cursor', ['offset', 'reverse', 'position'])


class CustomCursorPagination(CursorPagination):
    """Custom cursor pagination"""

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def inject_cursor_value(self, query: str = None) -> str:
        q_list = query.split('&')
        for query in q_list:
            query = query.split('=')
            if query[0] == 'cursor':
                return query[1]

    def replace_query_param(self, url, key, val):
        """
        Given a URL and a key/val pair, set or replace an item in the query
        parameters of the URL, and return the new URL.
        """
        (scheme, netloc, path, query, fragment) = urlparse.urlsplit(force_str(url))
        query_dict = urlparse.parse_qs(query, keep_blank_values=True)
        query_dict[force_str(key)] = [force_str(val)]
        query = urlparse.urlencode(sorted(list(query_dict.items())), doseq=True)
        return self.inject_cursor_value(query)

    def encode_cursor(self, cursor):
        """
        Given a Cursor instance, return an url with encoded cursor.
        """
        tokens = {}
        if cursor.offset != 0:
            tokens['o'] = str(cursor.offset)
        if cursor.reverse:
            tokens['r'] = '1'
        if cursor.position is not None:
            tokens['p'] = cursor.position

        querystring = urlparse.urlencode(tokens, doseq=True)
        encoded = b64encode(querystring.encode('ascii')).decode('ascii')
        return self.replace_query_param(self.base_url, self.cursor_query_param, encoded)


class NewsCursorPagination(CustomCursorPagination):
    """Custom cursor pagination"""

    ordering = '-publish_date'
