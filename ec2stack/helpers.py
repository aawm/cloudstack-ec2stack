#!/usr/bin/env python
# encoding: utf-8

import os
import hmac
import hashlib
from uuid import uuid1 as uuid
from base64 import b64encode
from urllib import urlencode
from functools import wraps

from flask import request, make_response, render_template

from ec2stack.services import USERS
from ec2stack.core import Ec2stackError


def get(item, data):
    if item in data:
        return data[item]
    else:
        return None


def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        required_params = {'Action', 'AWSAccessKeyId', 'Signature',
                           'SignatureMethod', 'SignatureVersion', 'Timestamp',
                           'Version'}
        require_parameters(required_params)

        _valid_signature_method()
        _valid_signature_version()
        _valid_signature()
        return f(*args, **kwargs)

    return decorated


def normalize_dict_keys(dct):
    return dict((key.lower(), value) for key, value in dct.iteritems())


def require_parameters(required_parameters):
    for parameter in required_parameters:
        if not contains_parameter(parameter):
            missing_paramater(parameter)


def require_one_paramater(parameters):
    parameter = None
    for parameter in parameters:
        if contains_parameter(parameter):
            return

    missing_paramater(parameter)


def missing_paramater(parameter):
    raise Ec2stackError(
        '400',
        'MissingParameter',
        'The request must contain the parameter %s' % parameter
    )


def contains_parameter(parameter):
    return (get(parameter, request.form)) is not None


def get_request_paramaters(parameter_type):
    root_parameter = parameter_type + '.'
    current_parameter_num = 1
    current_parameter = root_parameter + str(current_parameter_num)
    
    parameters = []

    while contains_parameter(current_parameter):
        paramater = get(current_parameter, request.form)
        parameters.append(get(current_parameter, request.form))
        current_parameter_num += 1
        current_parameter = root_parameter + str(current_parameter_num)

    return parameters


def get_secretkey(data=None):
    if data is None:
        data = request.form

    apikey = get('AWSAccessKeyId', data)
    user = USERS.get(apikey)

    if user is None:
        raise Ec2stackError(
            '401',
            'AuthFailure',
            'Unable to find a secret key for %s, please insure you registered'
            % apikey
        )

    return user.secretkey.encode('utf-8')


def _valid_signature_method():
    signature_method = get('SignatureMethod', request.form)
    if signature_method not in ['HmacSHA1', 'HmacSHA256']:
        raise Ec2stackError(
            '400',
            'InvalidParameterValue',
            'Value (%s) for parameter SignatureMethod is invalid. '
            'Unknown signature method.' % signature_method
        )


def _valid_signature_version():
    signature_version = get('SignatureVersion', request.form)
    if signature_version != '2':
        raise Ec2stackError(
            '400',
            'InvalidParameterValue',
            'Value (%s) for parameter SignatureVersion is invalid.'
            'Valid Signature versions are 2.'
            % signature_version
        )


def _valid_signature():
    signature = get('Signature', request.form)
    generated_signature = generate_signature()

    if signature != generated_signature:
        raise Ec2stackError(
            '401',
            'AuthFailure',
            'AWS was not able to validate the provided access credentials.'
        )


def generate_signature(data=None, method=None, host=None):
    if data is None:
        data = request.form

    secretkey = get_secretkey(data)
    request_string = _get_request_string(data, method, host)

    signature = hmac.new(
        key=secretkey,
        msg=bytes(request_string),
        digestmod=hashlib.sha256
    ).digest()

    signature = b64encode(signature)

    return signature


def _get_request_string(data=None, method=None, host=None):
    if data is None:
        data = request.form
    if method is None:
        method = request.method
    if host is None:
        host = request.host
    query_string = _get_query_string(data)

    request_string = '\n'.join(
        [method, host, '/', query_string]
    )

    return request_string.encode('utf-8')


def _get_query_string(data=None):
    if data is None:
        data = request.form

    params = {}
    for param in data:
        if param != 'Signature':
            params[param] = data[param]

    keys = sorted(params.keys())
    values = map(params.get, keys)

    query_string = urlencode(
        list(
            zip(keys, values)
        )
    )

    return query_string


def error_response(code, error, message):
    response = make_response(
        render_template(
            "generic_error.xml",
            response_type='Response',
            error=error,
            message=message,
            request_id=uuid()
        )
    )
    response.headers['Content-Type'] = 'application/xml'
    response.status_code = int(code)
    return response


def successful_response(**kwargs):
    content = render_template(request_id=uuid(), **kwargs)
    response = make_response(content)
    response.headers['Content-Type'] = 'application/xml'
    response.status_code = 200
    return response


def read_file(name):
    filepath = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '../',
        name
    )
    data = open(filepath)
    try:
        return data.read()
    except IOError:
        print "could not read %r" % name
        data.close()
