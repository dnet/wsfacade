#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# test_wsfacade.py - unit tests for wsfacade module
#
# Copyright (c) 2013 András Veres-Szentkirályi
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import unittest, wsfacade

class TestProcessFormData(unittest.TestCase):
	def test_empty(self):
		output = {}
		wsfacade.process_formdata(output.__setitem__, {}, None)
		self.assertEquals(output, {})
	

	KEY = 'testkey_with_Underscores_and_Uppercase_letters'
	VALUE = u'Unicode test value: Árvíztűrő tükörfúrógép'
	def test_string(self):
		output = {}
		data = {self.KEY + '__string': self.VALUE}
		wsfacade.process_formdata(output.__setitem__, data, None)
		self.assertEquals(output, {self.KEY: self.VALUE})
	

	TYPENAME = '{http://vsza.hu/}TypeName'
	def test_valid_enum(self):
		output = {}
		data = {self.KEY + '__' + self.TYPENAME + '__enum': self.KEY}
		mcf = MockClientFactory({self.TYPENAME: [self.KEY]})
		wsfacade.process_formdata(output.__setitem__, data, mcf)
		self.assertEquals(output.keys(), [self.KEY])


	def test_invalid_enum(self):
		output = {}
		data = {self.KEY + '__' + self.TYPENAME + '__enum': self.KEY}
		mcf = MockClientFactory({self.TYPENAME: []})
		wsfacade.process_formdata(output.__setitem__, data, mcf)
		self.assertEquals(output, {})


	KEY2 = 'second_testkey'
	def test_complex(self):
		output = {}
		data = {self.KEY + '__string__' + self.KEY2 + '__' + self.TYPENAME + '__complex': self.VALUE}
		mcf = MockClientFactory({self.TYPENAME: [self.KEY]})
		wsfacade.process_formdata(output.__setitem__, data, mcf)
		self.assertEquals(output.keys(), [self.KEY2])
		self.assertEquals(getattr(output[self.KEY2], self.KEY), self.VALUE)


class MockClientFactory(object):
	def __init__(self, typemap):
		self.factory = self
		self.typemap = typemap


	def create(self, typename):
		return MockObject(self.typemap[typename])


class MockObject(object):
	def __init__(self, values):
		for value in values:
			setattr(self, value, None)
