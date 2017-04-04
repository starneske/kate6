#!/usr/bin/python
"""
Add docstring here
"""
import os
import time
import unittest

import mock
from mock import patch
import mongomock


with patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient):
    os.environ['KATE6_MONGOALCHEMY_CONNECTION_STRING'] = ''
    os.environ['KATE6_MONGOALCHEMY_SERVER'] = ''
    os.environ['KATE6_MONGOALCHEMY_PORT'] = ''
    os.environ['KATE6_MONGOALCHEMY_DATABASE'] = ''

    from qube.src.models.kate6 import kate6
    from qube.src.services.kate6service import kate6Service
    from qube.src.commons.context import AuthContext
    from qube.src.commons.error import ErrorCodes, kate6ServiceError


class Testkate6Service(unittest.TestCase):
    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        context = AuthContext("23432523452345", "tenantname",
                              "987656789765670", "orgname", "1009009009988",
                              "username", False)
        self.kate6Service = kate6Service(context)
        self.kate6_api_model = self.createTestModelData()
        self.kate6_data = self.setupDatabaseRecords(self.kate6_api_model)
        self.kate6_someoneelses = \
            self.setupDatabaseRecords(self.kate6_api_model)
        self.kate6_someoneelses.tenantId = "123432523452345"
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            self.kate6_someoneelses.save()
        self.kate6_api_model_put_description \
            = self.createTestModelDataDescription()
        self.test_data_collection = [self.kate6_data]

    def tearDown(self):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            for item in self.test_data_collection:
                item.remove()
            self.kate6_data.remove()

    def createTestModelData(self):
        return {'name': 'test123123124'}

    def createTestModelDataDescription(self):
        return {'description': 'test123123124'}

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setupDatabaseRecords(self, kate6_api_model):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            kate6_data = kate6(name='test_record')
            for key in kate6_api_model:
                kate6_data.__setattr__(key, kate6_api_model[key])

            kate6_data.description = 'my short description'
            kate6_data.tenantId = "23432523452345"
            kate6_data.orgId = "987656789765670"
            kate6_data.createdBy = "1009009009988"
            kate6_data.modifiedBy = "1009009009988"
            kate6_data.createDate = str(int(time.time()))
            kate6_data.modifiedDate = str(int(time.time()))
            kate6_data.save()
            return kate6_data

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_post_kate6(self, *args, **kwargs):
        result = self.kate6Service.save(self.kate6_api_model)
        self.assertTrue(result['id'] is not None)
        self.assertTrue(result['name'] == self.kate6_api_model['name'])
        kate6.query.get(result['id']).remove()

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_kate6(self, *args, **kwargs):
        self.kate6_api_model['name'] = 'modified for put'
        id_to_find = str(self.kate6_data.mongo_id)
        result = self.kate6Service.update(
            self.kate6_api_model, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['name'] == self.kate6_api_model['name'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_kate6_description(self, *args, **kwargs):
        self.kate6_api_model_put_description['description'] =\
            'modified for put'
        id_to_find = str(self.kate6_data.mongo_id)
        result = self.kate6Service.update(
            self.kate6_api_model_put_description, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['description'] ==
                        self.kate6_api_model_put_description['description'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_kate6_item(self, *args, **kwargs):
        id_to_find = str(self.kate6_data.mongo_id)
        result = self.kate6Service.find_by_id(id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_kate6_item_invalid(self, *args, **kwargs):
        id_to_find = '123notexist'
        with self.assertRaises(kate6ServiceError):
            self.kate6Service.find_by_id(id_to_find)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_kate6_list(self, *args, **kwargs):
        result_collection = self.kate6Service.get_all()
        self.assertTrue(len(result_collection) == 1,
                        "Expected result 1 but got {} ".
                        format(str(len(result_collection))))
        self.assertTrue(result_collection[0]['id'] ==
                        str(self.kate6_data.mongo_id))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_not_system_user(self, *args, **kwargs):
        id_to_delete = str(self.kate6_data.mongo_id)
        with self.assertRaises(kate6ServiceError) as ex:
            self.kate6Service.delete(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_ALLOWED)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_by_system_user(self, *args, **kwargs):
        id_to_delete = str(self.kate6_data.mongo_id)
        self.kate6Service.auth_context.is_system_user = True
        self.kate6Service.delete(id_to_delete)
        with self.assertRaises(kate6ServiceError) as ex:
            self.kate6Service.find_by_id(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_FOUND)
        self.kate6Service.auth_context.is_system_user = False

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_item_someoneelse(self, *args, **kwargs):
        id_to_delete = str(self.kate6_someoneelses.mongo_id)
        with self.assertRaises(kate6ServiceError):
            self.kate6Service.delete(id_to_delete)
