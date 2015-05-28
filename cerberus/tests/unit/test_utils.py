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
"""Tests for cerberus/utils.py
"""
import datetime
import decimal

from oslotest import base

from cerberus import utils


class TestUtils(base.BaseTestCase):

    def test_datetime_to_decimal(self):
        expected = 1356093296.12
        utc_datetime = datetime.datetime.utcfromtimestamp(expected)
        actual = utils.dt_to_decimal(utc_datetime)
        self.assertAlmostEqual(expected, float(actual), places=5)

    def test_decimal_to_datetime(self):
        expected = 1356093296.12
        dexpected = decimal.Decimal(str(expected))  # Python 2.6 wants str()
        expected_datetime = datetime.datetime.utcfromtimestamp(expected)
        actual_datetime = utils.decimal_to_dt(dexpected)
        # Python 3 have rounding issue on this, so use float
        self.assertAlmostEqual(utils.dt_to_decimal(expected_datetime),
                               utils.dt_to_decimal(actual_datetime),
                               places=5)

    def test_restore_nesting_unested(self):
        metadata = {'a': 'A', 'b': 'B'}
        unwound = utils.restore_nesting(metadata)
        self.assertIs(metadata, unwound)

    def test_restore_nesting(self):
        metadata = {'a': 'A', 'b': 'B',
                    'nested:a': 'A',
                    'nested:b': 'B',
                    'nested:twice:c': 'C',
                    'nested:twice:d': 'D',
                    'embedded:e': 'E'}
        unwound = utils.restore_nesting(metadata)
        expected = {'a': 'A', 'b': 'B',
                    'nested': {'a': 'A', 'b': 'B',
                               'twice': {'c': 'C', 'd': 'D'}},
                    'embedded': {'e': 'E'}}
        self.assertEqual(expected, unwound)
        self.assertIsNot(metadata, unwound)

    def test_restore_nesting_with_separator(self):
        metadata = {'a': 'A', 'b': 'B',
                    'nested.a': 'A',
                    'nested.b': 'B',
                    'nested.twice.c': 'C',
                    'nested.twice.d': 'D',
                    'embedded.e': 'E'}
        unwound = utils.restore_nesting(metadata, separator='.')
        expected = {'a': 'A', 'b': 'B',
                    'nested': {'a': 'A', 'b': 'B',
                               'twice': {'c': 'C', 'd': 'D'}},
                    'embedded': {'e': 'E'}}
        self.assertEqual(expected, unwound)
        self.assertIsNot(metadata, unwound)

    def test_decimal_to_dt_with_none_parameter(self):
        self.assertIsNone(utils.decimal_to_dt(None))

    def test_dict_to_kv(self):
        data = {'a': 'A',
                'b': 'B',
                'nested': {'a': 'A',
                           'b': 'B',
                           },
                'nested2': [{'c': 'A'}, {'c': 'B'}]
                }
        pairs = list(utils.dict_to_keyval(data))
        self.assertEqual([('a', 'A'),
                          ('b', 'B'),
                         ('nested.a', 'A'),
                         ('nested.b', 'B'),
                         ('nested2[0].c', 'A'),
                         ('nested2[1].c', 'B')],
                         sorted(pairs, key=lambda x: x[0]))
