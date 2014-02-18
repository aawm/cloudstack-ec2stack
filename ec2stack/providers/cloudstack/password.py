#!/usr/bin/env python
# encoding: utf-8

from flask import request

from ec2stack import helpers
from ec2stack.helpers import authentication_required
from ec2stack.core import Ec2stackError
from ec2stack.providers.cloudstack import requester


@authentication_required
def get_password_data():
    helpers.require_parameters(['InstanceId'])
    response = _get_password_data_request()
    return _get_password_data_format_response(response)


def _get_password_data_request():
    args = {}
    args['command'] = 'getVMPassword'
    args['id'] = helpers.get('InstanceId', request.form)

    response = requester.make_request(args)

    response = response['getvmpasswordresponse']

    return response


def _get_password_data_format_response(response):
    instanceid = helpers.get('InstanceId', request.form)
    if 'errortext' in response:
        raise Ec2stackError(
            '400',
            'InvalidInstanceID.NotFound',
            'The instance ID \'%s\' does not exist.' % instanceid
        )
    else:
        response = response['password']
        return {
            'template_name_or_list': 'password.xml',
            'response_type': 'GetPasswordDataResponse',
            'instance_id': instanceid,
            'password_data': response['encryptedpassword']
        }
