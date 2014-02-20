#!/usr/bin/env python
# encoding: utf-8

from base64 import b64encode

import mock

from ec2stack.helpers import read_file, generate_signature
from . import Ec2StackAppTestCase


class KeyPairTestCase(Ec2StackAppTestCase):

    def test_create_keypair(self):
        data = self.get_example_data()
        data['Action'] = 'CreateKeyPair'
        data['KeyName'] = 'Test'
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get = mock.Mock()
        text = get.return_value.text = read_file(
            'tests/data/valid_create_keypair.json'
        )
        status_code = get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            response = self.post(
                '/',
                data=data
            )

        self.assertOk(response)
        assert 'CreateKeyPairResponse' in response.data

    def test_duplicate_keypair(self):
        data = self.get_example_data()
        data['Action'] = 'CreateKeyPair'
        data['KeyName'] = 'Test'
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get = mock.Mock()
        text = get.return_value.text = read_file(
            'tests/data/duplicate_create_keypair.json'
        )
        status_code = get.return_value.status_code = 431

        with mock.patch('requests.get', get):
            response = self.post(
                '/',
                data=data
            )

        self.assertBadRequest(response)
        assert 'InvalidKeyPair.Duplicate' in response.data

    def test_delete_keypair(self):
        data = self.get_example_data()
        data['Action'] = 'DeleteKeyPair'
        data['KeyName'] = 'Test'
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get = mock.Mock()
        text = get.return_value.text = read_file(
            'tests/data/delete_keypair.json'
        )
        status_code = get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            response = self.post(
                '/',
                data=data
            )

        self.assertOk(response)
        assert 'DeleteKeyPairResponse' in response.data

    def test_import_keypair(self):
        data = self.get_example_data()
        data['Action'] = 'ImportKeyPair'
        data['KeyName'] = 'Test'
        data['PublicKeyMaterial'] = b64encode(
            'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCaqPfl99phOoszUD6n9xNKUtjqof'
            'hktvGxuhT2BgiTNi55FNfHAPyXyakQ86NbZPEQoRiDGyOI6BQVOmd+811Z+tFpB8Es'
            'Y9t7tFAohid6G6bn7/Z78beXXMk9lcc7bnCVZaeZmAjHSTBHinlcWqB3P5IPJTASVe'
            'ktX8drPXXyTCEp5NlJdSTmfnQJAm9Ho5YMlHGAMyW8aIBKBrpwjx6RAYnPcIWm0Jsv'
            'oSrPTeM9koziSRBROG06UT3FSslwuetcQvHsvIPHJ1IrwHljXQomOf7GLgSzbp6Czv'
            'lY6Leh9OQOcv70dYy5RcoEoVh+Lta5LpyiUL/ntW270M29lxpB'
        )
        data['Signature'] = generate_signature(data, 'POST', 'localhost')

        get = mock.Mock()
        text = get.return_value.text = read_file(
            'tests/data/valid_import_keypair.json'
        )
        status_code = get.return_value.status_code = 200

        with mock.patch('requests.get', get):
            response = self.post(
                '/',
                data=data
            )

        self.assertOk(response)
        assert 'ImportKeyPairResponse' in response.data
