#
#   Copyright (c) 2014 EUROGICIEL
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
"""Utilities and helper functions."""

import calendar
import copy
import datetime
import decimal
import multiprocessing

from oslo.utils import timeutils
from oslo.utils import units
import six


def restore_nesting(d, separator=':'):
    """Unwinds a flattened dict to restore nesting.
    """
    d = copy.copy(d) if any([separator in k for k in d.keys()]) else d
    for k, v in d.items():
        if separator in k:
            top, rem = k.split(separator, 1)
            nest = d[top] if isinstance(d.get(top), dict) else {}
            nest[rem] = v
            d[top] = restore_nesting(nest, separator)
            del d[k]
    return d


def dt_to_decimal(utc):
    """Datetime to Decimal.

    Some databases don't store microseconds in datetime
    so we always store as Decimal unixtime.
    """
    if utc is None:
        return None

    decimal.getcontext().prec = 30
    return decimal.Decimal(str(calendar.timegm(utc.utctimetuple()))) + \
        (decimal.Decimal(str(utc.microsecond)) /
         decimal.Decimal("1000000.0"))


def decimal_to_dt(dec):
    """Return a datetime from Decimal unixtime format.
    """
    if dec is None:
        return None

    integer = int(dec)
    micro = (dec - decimal.Decimal(integer)) * decimal.Decimal(units.M)
    daittyme = datetime.datetime.utcfromtimestamp(integer)
    return daittyme.replace(microsecond=int(round(micro)))


def sanitize_timestamp(timestamp):
    """Return a naive utc datetime object."""
    if not timestamp:
        return timestamp
    if not isinstance(timestamp, datetime.datetime):
        timestamp = timeutils.parse_isotime(timestamp)
    return timeutils.normalize_time(timestamp)


def stringify_timestamps(data):
    """Stringify any datetimes in given dict."""
    isa_timestamp = lambda v: isinstance(v, datetime.datetime)
    return dict((k, v.isoformat() if isa_timestamp(v) else v)
                for (k, v) in six.iteritems(data))


def dict_to_keyval(value, key_base=None):
    """Expand a given dict to its corresponding key-value pairs.

    Generated keys are fully qualified, delimited using dot notation.
    ie. key = 'key.child_key.grandchild_key[0]'
    """
    val_iter, key_func = None, None
    if isinstance(value, dict):
        val_iter = six.iteritems(value)
        key_func = lambda k: key_base + '.' + k if key_base else k
    elif isinstance(value, (tuple, list)):
        val_iter = enumerate(value)
        key_func = lambda k: key_base + '[%d]' % k

    if val_iter:
        for k, v in val_iter:
            key_gen = key_func(k)
            if isinstance(v, dict) or isinstance(v, (tuple, list)):
                for key_gen, v in dict_to_keyval(v, key_gen):
                    yield key_gen, v
            else:
                yield key_gen, v


def lowercase_keys(mapping):
    """Converts the values of the keys in mapping to lowercase."""
    items = mapping.items()
    for key, value in items:
        del mapping[key]
        mapping[key.lower()] = value


def lowercase_values(mapping):
    """Converts the values in the mapping dict to lowercase."""
    items = mapping.items()
    for key, value in items:
        mapping[key] = value.lower()


def update_nested(original_dict, updates):
    """Updates the leaf nodes in a nest dict, without replacing
       entire sub-dicts.
    """
    dict_to_update = copy.deepcopy(original_dict)
    for key, value in six.iteritems(updates):
        if isinstance(value, dict):
            sub_dict = update_nested(dict_to_update.get(key, {}), value)
            dict_to_update[key] = sub_dict
        else:
            dict_to_update[key] = updates[key]
    return dict_to_update


def cpu_count():
    try:
        return multiprocessing.cpu_count() or 1
    except NotImplementedError:
        return 1


def uniq(dupes, attrs):
    """Exclude elements of dupes with a duplicated set of attribute values."""
    key = lambda d: '/'.join([getattr(d, a) or '' for a in attrs])
    keys = []
    deduped = []
    for d in dupes:
        if key(d) not in keys:
            deduped.append(d)
            keys.append(key(d))
    return deduped


def create_datetime_obj(date):
    """
    '20150109T10:53:50'
    :param date: The date to build a datetime object. Format: 20150109T10:53:50
    :return: a datetime object
    """
    return datetime.datetime.strptime(date, '%Y%m%dT%H:%M:%S')
