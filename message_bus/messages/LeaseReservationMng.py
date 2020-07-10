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

from __future__ import annotations

from message_bus.messages.ReservationPredecessorMng import ReservationPredecessorMng
from message_bus.messages.TicketReservationMng import TicketReservationMng


class LeaseReservationMng(TicketReservationMng):
    def __init__(self):
        super().__init__()
        self.authority = None
        self.join_state = None
        self.leased_units = None
        self.redeem_processors = []
        self.name = self.__class__.__name__

    def from_dict(self, value: dict):
        super().from_dict(value)
        self.authority = value.get('authority', None)
        self.join_state = value.get('join_state', None)
        self.leased_units = value.get('leased_units', None)
        temp_redeem = value.get('redeem_processors', None)
        if temp_redeem is not None:
            for p in temp_redeem:
                predecessor = ReservationPredecessorMng()
                predecessor.from_dict(p)
                self.redeem_processors.append(predecessor)

    def to_dict(self) -> dict:
        result = super().to_dict()
        if result is None:
            result = {}
        result['authority'] = self.authority
        if self.join_state is not None:
            result['join_state'] = self.join_state

        if self.leased_units is not None:
            result['leased_units'] = self.leased_units

        if self.redeem_processors is not None and len(self.redeem_processors) > 0:
            temp = []
            for p in self.redeem_processors:
                temp.append(p.to_dict())
            result['redeem_processors'] = temp

        return result

    def __str__(self):
        return "{} authority: {} join_state: {} leased_units: {} redeem_processors: {}".format(super().__str__(),
                                                                                               self.authority,
                                                                                               self.join_state,
                                                                                               self.leased_units,
                                                                                               self.redeem_processors)

    def print(self):
        print("")
        print("Reservation ID: {} Slice ID: {}".format(self.reservation_id, self.slice_id))
        if self.rtype is not None or self.notices is not None:
            print("Resource Type: {} Notices: {}".format(self.rtype, self.notices))

        if self.start is not None or self.end is not None or self.requested_end is not None:
            print("Start: {} End: {} Requested End: {}".format(self.start, self.end, self.requested_end))

        if self.units is not None or self.state is not None or self.pending_state is not None:
            print("Units: {} State: {} Pending State: {}".format(self.units, self.state, self.pending_state))

        print("Broker: {}".format(self.broker))

        if self.ticket is not None:
            print("Ticket properties: {}".format(self.ticket))

        if self.renewable is not None:
            print("Renewable: {}".format(self.renewable))

        if self.renew_time is not None:
            print("Renew Time: {}".format(self.renew_time))

        print("Authority: {}".format(self.authority))

        if self.join_state is not None:
            print("Join State: {}".format(self.join_state))

        if self.leased_units is not None:
            print("Leased Units: {}".format(self.leased_units))

        if self.redeem_processors is not None:
            index = 0
            for rp in self.redeem_processors:
                print("Redeem Predecessor# {}: {}".format(index, rp))
                index += 1

        if self.local is not None:
            print("Local Properties: {}".format(self.local))
        if self.config is not None:
            print("Config Properties: {}".format(self.config))
        if self.request is not None:
            print("Request Properties: {}".format(self.request))
        if self.resource is not None:
            print("Resource Properties: {}".format(self.resource))
        print("")

    def get_authority(self) -> str:
        return self.authority

    def set_authority(self, value: str):
        self.authority = value

    def get_join_state(self) -> int:
        return self.join_state

    def set_join_state(self, value: int):
        self.join_state = value

    def get_leased_units(self) -> int:
        return self.leased_units

    def set_leased_units(self, value: int):
        self.leased_units = value

    def get_redeem_predecessors(self) -> list:
        return self.redeem_processors