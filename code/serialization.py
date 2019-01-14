# -*- coding: utf-8 -*-
import json


def encoder(obj):
    try:
        encoding = obj.to_json()
    except AttributeError:
        encoding = json.JSONEncoder.default(obj)
    return encoding

def pretty_print(obj):
    try:
        encoding = obj.to_json()['__kw__']
    except AttributeError:
        encoding = json.JSONEncoder.default(obj)
    return encoding
