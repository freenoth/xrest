# from django.test import TestCase

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from django.conf import settings

import os
import shutil


# Create your tests here.

class APITestCaseWithFiles(APITestCase):
    _rm_files = []
    _path_to_files = settings.MEDIA_ROOT + '\\test\\'

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls._path_to_files):
            os.mkdir(cls._path_to_files)

    @classmethod
    def tearDownClass(cls):
        for path in cls._rm_files:
            if os.path.exists(settings.MEDIA_ROOT + path):
                os.remove(settings.MEDIA_ROOT + path)
        shutil.rmtree(cls._path_to_files)

    @classmethod
    def make_test_file(cls, name, data_string):
        # make one SomeFile
        new_file_path = cls._path_to_files + name
        cls._rm_files.append(name)
        with open(new_file_path, 'w+', encoding='utf-8') as new_file:
            new_file.write(data_string)
        return new_file_path


class FilesTests(APITestCaseWithFiles):

    def test_get_files_is_available(self):
        url = reverse('api:files')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_files_check_response_headers(self):
        url = reverse('api:files')
        response = self.client.get(url)

        self.assertEqual(response['Content-Type'], 'application/json')

    def test_get_files_check_response_json_fields(self):
        url = reverse('api:files')
        response = self.client.get(url)

        self.assertEqual(response.json()['status'], 'OK')
        self.assertEqual(response.json()['code'], status.HTTP_200_OK)
        self.assertIsNotNone(response.json()['data'])

    def test_get_files_with_currently_uploaded_file(self):
        url = reverse('api:files')

        filename = 'test_get_files_with_currently_uploaded_file.txt'
        file_path = self.make_test_file(filename, 'test file 1')
        with open(file_path, 'rb') as file:
            response = self.client.post(url, {'file': file})

        # check for created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['status'], 'OK')
        self.assertEqual(response.json()['code'], status.HTTP_200_OK)
        self.assertIsNotNone(response.json()['data'])
        self.assertEqual(len(response.json()['data']), 1)
        self.assertIsNotNone(response.json()['data'][0]['id'])
        self.assertEqual(response.json()['data'][0]['name'], filename)

    def test_post_files_upload_some_file(self):
        url = reverse('api:files')

        filename = 'test_post_files_upload_some_file.txt'
        file_path = self.make_test_file(filename, 'test_post_files_upload_some_file')

        with open(file_path, 'rb') as file:
            response = self.client.post(url, {'file': file})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['status'], 'OK')
        self.assertEqual(response.json()['code'], status.HTTP_201_CREATED)
        self.assertIsNotNone(response.json()['data'])
        self.assertIsNotNone(response.json()['data']['id'])
        self.assertEqual(response.json()['data']['name'], filename)

    def test_post_files_without_file_parameter(self):
        url = reverse('api:files')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['status'], 'Error')
        self.assertEqual(response.json()['code'], status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.json()['data'])

    def test_post_files_upload_existing_file(self):
        url = reverse('api:files')

        filename = 'test_post_files_upload_existing_file.txt'

        file_path = self.make_test_file(filename, 'test_post_files_upload_existing_file')
        with open(file_path, 'rb') as file:
            response = self.client.post(url, {'file': file})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        file_path = self.make_test_file(filename, 'test_post_files_upload_existing_file THE SECOND')
        with open(file_path, 'rb') as file:
            response = self.client.post(url, {'file': file})

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['status'], 'Error')
        self.assertEqual(response.json()['code'], status.HTTP_409_CONFLICT)
        self.assertIsNotNone(response.json()['data'])


class FileDetailTests(APITestCaseWithFiles):

    def setUp(self):
        url = reverse('api:files')
        filename = 'FileDetailTests_test_file.txt'

        file_path = self.make_test_file(filename, 'TEST DATA')
        with open(file_path, 'rb') as file:
            response = self.client.post(url, {'file': file})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self._url = reverse('api:file_detail', args=(response.json()['data']['id'],))

    def tearDown(self):
        if self._url:
            response = self.client.delete(self._url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._url = None

    def test_get_file_with_bad_file_id(self):
        some_url = reverse('api:file_detail', args=(666,))

        response = self.client.get(some_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['status'], 'Error')
        self.assertEqual(response.json()['code'], status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(response.json()['data'])

    def test_get_file_correct_file_id(self):
        response = self.client.get(self._url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertIsNotNone(response.get('Content-Length', None))
        # self.assertEqual(b''.join([x for x in response.streaming_content]), b'TEST DATA')

    def test_delete_file_not_existing(self):
        some_url = reverse('api:file_detail', args=(666,))

        response = self.client.delete(some_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['status'], 'Error')
        self.assertEqual(response.json()['code'], status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(response.json()['data'])

    def test_delete_file_correct_file_id(self):
        response = self.client.delete(self._url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['status'], 'OK')
        self.assertEqual(response.json()['code'], status.HTTP_200_OK)
        self.assertIsNotNone(response.json()['data'])
        self.assertIsNotNone(response.json()['data']['result'])

        self._url = None

    def test_put_file_not_existing_id(self):
        some_url = reverse('api:file_detail', args=(666,))

        response = self.client.put(some_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['status'], 'Error')
        self.assertEqual(response.json()['code'], status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(response.json()['data'])

    def test_put_file_correct_id_without_file_parameters(self):
        response = self.client.put(self._url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['status'], 'Error')
        self.assertEqual(response.json()['code'], status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.json()['data'])

    def test_put_filt_correct_id_with_new_file(self):
        new_file_name = 'new_file_for_put.txt'
        new_file = self.make_test_file(new_file_name, 'SOME NEW INFO')
        with open(new_file, 'rb') as file:
            response = self.client.put(self._url, {'file': file})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['status'], 'OK')
        self.assertEqual(response.json()['code'], status.HTTP_200_OK)
        self.assertIsNotNone(response.json()['data'])
        self.assertIsNotNone(response.json()['data']['id'])
        self.assertIsNotNone(response.json()['data']['name'])
        self.assertNotEqual(response.json()['data']['name'], new_file_name)


class FileMetaTests(APITestCaseWithFiles):

    def setUp(self):
        url = reverse('api:files')
        filename = 'FileMetaTests_test_file.txt'

        file_path = self.make_test_file(filename, 'TEST DATA')
        with open(file_path, 'rb') as file:
            response = self.client.post(url, {'file': file})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self._url = reverse('api:file_detail', args=(response.json()['data']['id'],))
        self._url_meta = reverse('api:file_meta', args=(response.json()['data']['id'],))
        self._filename = filename

    def tearDown(self):
        if self._url:
            response = self.client.delete(self._url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self._url = None

    def test_get_file_meta_with_bad_file_id(self):
        some_url = reverse('api:file_meta', args=(666,))
        response = self.client.get(some_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['status'], 'Error')
        self.assertEqual(response.json()['code'], status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(response.json()['data'])

    def test_get_file_meta_correct_file_id(self):
        response = self.client.get(self._url_meta)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['status'], 'OK')
        self.assertEqual(response.json()['code'], status.HTTP_200_OK)
        self.assertEqual(response.json()['data']['name'], self._filename)
        self.assertIsNotNone(response.json()['data']['size'])
        self.assertIsNotNone(response.json()['data']['mime_type'])
        self.assertIsNotNone(response.json()['data']['ext'])
        self.assertIsNotNone(response.json()['data']['created'])
        self.assertIsNotNone(response.json()['data']['modified'])
