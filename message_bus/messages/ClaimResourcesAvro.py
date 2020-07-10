#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 FABRIC Testbed
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# Author: Komal Thareja (kthare10@renci.org)
from uuid import uuid4, uuid1

from message_bus.messages.AuthAvro import AuthAvro
from message_bus.messages.message import IMessageAvro


class ClaimResourcesAvro(IMessageAvro):
    # Use __slots__ to explicitly declare all data members.
    __slots__ = ["name", "message_id", "guid", "broker_id", "reservation_id", "slice_id", "auth", "callback_topic", "id"]

    def __init__(self):
        self.name = IMessageAvro.ClaimResources
        self.message_id = None
        self.guid = None
        self.broker_id = None
        self.reservation_id = None
        self.slice_id = None
        self.auth = None
        self.callback_topic = None
        # Unique id used to track produce request success/failures.
        # Do *not* include in the serialized object.
        self.id = uuid4()

    def from_dict(self, value: dict):
        if value['name'] != IMessageAvro.ClaimResources:
            raise Exception("Invalid message")
        self.message_id = value['message_id']
        self.guid = value['guid']
        self.broker_id = value['broker_id']
        self.reservation_id = value['reservation_id']

        if 'slice_id' in value and value['slice_id'] != "null":
            self.slice_id = value['slice_id']

        if value.get('auth', None) is not None and value['auth'] != "null":
            self.auth = AuthAvro()
            self.auth.from_dict(value['auth'])
        self.callback_topic = value['callback_topic']

    def to_dict(self) -> dict:
        """
            The Avro Python library does not support code generation.
            For this reason we must provide a dict representation of our class for serialization.
        """
        result = {
            "name": self.name,
            "message_id": self.message_id,
            "guid": self.guid,
            "broker_id": self.broker_id,
            "reservation_id": self.reservation_id,
            "callback_topic": self.callback_topic
        }
        if self.auth is not None:
            result['auth'] = self.auth.to_dict()
        if self.slice_id is not None:
            result["slice_id"] = self.slice_id
        return result

    def get_message_id(self) -> str:
        """
        Returns the message_id
        """
        return self.message_id

    def get_message_name(self) -> str:
        return self.name

    def get_callback_topic(self) -> str:
        return self.callback_topic

    def __str__(self):
        return "name: {} message_id: {} guid: {} broker_id: {} reservation_id: {} slice_id: {} auth: {} callback_topic: {}".format(
            self.name, self.message_id, self.guid, self.broker_id, self.reservation_id, self.slice_id, self.auth, self.callback_topic)

    def get_id(self) -> str:
        return self.id.__str__()