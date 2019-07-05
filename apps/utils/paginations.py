from __future__ import unicode_literals

import re
from base64 import b64encode
from collections import namedtuple

from django.db.models import F
from django.utils.encoding import force_str
from django.utils.six.moves.urllib import parse as urlparse
from rest_framework.pagination import CursorPagination
from rest_framework.pagination import _reverse_ordering, _positive_int

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

    def inject_cursor_value(self, query: str, scheme: str = None, netloc: str = None,
                            path: str = None, fragment: str = None) -> str:
        """
        # Eject cursor value without url and filters
        Example of response:
        ```
            {
                "next": "cD0yMDE5LTA2LTA2KzA4JTNBMjYlM0EyNi4zOTMxMjElMkIwMCUzQTAw"
                ...
            }
        ```
        """
        pattern = r'cursor[=]{1}[\w]*[%\w]+'
        match = re.search(pattern, query)
        if match:
            return match.group().split('=')[1]
        else:
            # Default mechanism to return cursor value (with url and filter params)
            return urlparse.urlunsplit((scheme, netloc, path, query, fragment))

    def replace_query_param(self, url, key, val):
        """
        Given a URL and a key/val pair, set or replace an item in the query
        parameters of the URL, and return the new URL.
        """
        (scheme, netloc, path, query, fragment) = urlparse.urlsplit(force_str(url))
        query_dict = urlparse.parse_qs(query, keep_blank_values=True)
        query_dict[force_str(key)] = [force_str(val)]
        query = urlparse.urlencode(sorted(list(query_dict.items())), doseq=True)
        return self.inject_cursor_value(query, scheme, netloc, path, fragment)

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


class ChatCursorPagination(CustomCursorPagination):

    ordering = 'last_message_datetime'

    def paginate_queryset(self, queryset, request, view=None):
        self.page_size = self.get_page_size(request)
        if not self.page_size:
            return None

        self.base_url = request.build_absolute_uri()
        self.ordering = self.get_ordering(request, queryset, view)

        self.cursor = self.decode_cursor(request)
        if self.cursor is None:
            (offset, reverse, current_position) = (0, False, None)
        else:
            (offset, reverse, current_position) = self.cursor

        # Cursor pagination always enforces an ordering.
        if reverse:
            queryset = queryset.order_by(*_reverse_ordering(self.ordering))
        else:
            queryset = queryset.order_by(F(*self.ordering).desc(nulls_last=True))

        # If we have a cursor with a fixed position then filter by that.
        if current_position is not None:
            order = self.ordering[0]
            is_reversed = order.startswith('-')
            order_attr = order.lstrip('-')

            # Test for: (cursor reversed) XOR (queryset reversed)
            if self.cursor.reverse != is_reversed:
                kwargs = {order_attr + '__lt': current_position}
            else:
                kwargs = {order_attr + '__gt': current_position}

            queryset = queryset.filter(**kwargs)

        # If we have an offset cursor then offset the entire page by that amount.
        # We also always fetch an extra item in order to determine if there is a
        # page following on from this one.
        results = list(queryset[offset:offset + self.page_size + 1])
        self.page = list(results[:self.page_size])

        # Determine the position of the final item following the page.
        if len(results) > len(self.page):
            has_following_position = True
            following_position = self._get_position_from_instance(results[-1], self.ordering)
        else:
            has_following_position = False
            following_position = None

        if reverse:
            # If we have a reverse queryset, then the query ordering was in reverse
            # so we need to reverse the items again before returning them to the user.
            self.page = list(reversed(self.page))

            # Determine next and previous positions for reverse cursors.
            self.has_next = (current_position is not None) or (offset > 0)
            self.has_previous = has_following_position
            if self.has_next:
                self.next_position = current_position
            if self.has_previous:
                self.previous_position = following_position
        else:
            # Determine next and previous positions for forward cursors.
            self.has_next = has_following_position
            self.has_previous = (current_position is not None) or (offset > 0)
            if self.has_next:
                self.next_position = following_position
            if self.has_previous:
                self.previous_position = current_position

        # Display page controls in the browsable API if there is more
        # than one page.
        if (self.has_previous or self.has_next) and self.template is not None:
            self.display_page_controls = True

        return self.page
