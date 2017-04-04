#!/usr/bin/python
"""
Add docstring here
"""
import time
import unittest

import mock

from mock import patch
import mongomock


class Testkate6Model(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("before class")

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def test_create_kate6_model(self):
        from qube.src.models.kate6 import kate6
        kate6_data = kate6(name='testname')
        kate6_data.tenantId = "23432523452345"
        kate6_data.orgId = "987656789765670"
        kate6_data.createdBy = "1009009009988"
        kate6_data.modifiedBy = "1009009009988"
        kate6_data.createDate = str(int(time.time()))
        kate6_data.modifiedDate = str(int(time.time()))
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            kate6_data.save()
            self.assertIsNotNone(kate6_data.mongo_id)
            kate6_data.remove()

    @classmethod
    def tearDownClass(cls):
        print("After class")


if __name__ == '__main__':
    unittest.main()
