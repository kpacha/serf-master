#!/usr/bin/env python

import os
import logging

class SerfHandler(object):
    def __init__(self):
        self.name = os.environ['SERF_SELF_NAME']
        self.roles = (os.environ.get('SERF_TAG_ROLE') or os.environ.get('SERF_SELF_ROLE')).split(":")
        self.roles.append('default')
        self.logger = logging.getLogger(type(self).__name__)
        if os.environ['SERF_EVENT'] == 'user':
            self.event = os.environ['SERF_USER_EVENT']
        elif os.environ['SERF_EVENT'] == 'query':
            self.event = os.environ['SERF_QUERY_NAME']
        else:
            self.event = os.environ['SERF_EVENT'].replace('-', '_')

    def log(self, message):
        self.logger.info(message)


class SerfHandlerProxy(SerfHandler):

    def __init__(self):
        super(SerfHandlerProxy, self).__init__()
        self.handlers = {}

    def register(self, role, handler):
        self.handlers[role] = handler

    def get_klass(self):
        klass = []
        for role in self.roles:
            if role in self.handlers:
                klass.append(self.handlers[role])
        return klass

    def run(self):
        klass = self.get_klass()
        if len(klass) == 0:
            self.log("no handler for role")
        else:
            for k in klass:
                try:
                    getattr(k, self.event)()
                except AttributeError:
                    self.log("event not implemented by class")
