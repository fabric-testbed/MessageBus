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
import unittest

from fabric.message_bus.admin import AdminApi
from fabric.message_bus.consumer import AvroConsumerApi
from fabric.message_bus.messages.AddSliceAvro import AddSliceAvro
from fabric.message_bus.messages.AuthAvro import AuthAvro
from fabric.message_bus.messages.ClaimAvro import ClaimAvro
from fabric.message_bus.messages.ClaimResourcesAvro import ClaimResourcesAvro
from fabric.message_bus.messages.CloseReservationsAvro import CloseReservationsAvro
from fabric.message_bus.messages.FailedRPCAvro import FailedRPCAvro
from fabric.message_bus.messages.GetReservationsRequestAvro import GetReservationsRequestAvro
from fabric.message_bus.messages.GetReservationsResponseAvro import GetReservationsResponseAvro
from fabric.message_bus.messages.GetSlicesRequestAvro import GetSlicesRequestAvro
from fabric.message_bus.messages.GetSlicesResponseAvro import GetSlicesResponseAvro
from fabric.message_bus.messages.QueryAvro import QueryAvro
from fabric.message_bus.messages.QueryResultAvro import QueryResultAvro
from fabric.message_bus.messages.RedeemAvro import RedeemAvro
from fabric.message_bus.messages.RemoveReservationAvro import RemoveReservationAvro
from fabric.message_bus.messages.RemoveSliceAvro import RemoveSliceAvro
from fabric.message_bus.messages.ReservationAvro import ReservationAvro
from fabric.message_bus.messages.ReservationMng import ReservationMng
from fabric.message_bus.messages.ResourceDataAvro import ResourceDataAvro
from fabric.message_bus.messages.ResourceSetAvro import ResourceSetAvro
from fabric.message_bus.messages.ResultAvro import ResultAvro
from fabric.message_bus.messages.SliceAvro import SliceAvro
from fabric.message_bus.messages.StatusResponseAvro import StatusResponseAvro
from fabric.message_bus.messages.TermAvro import TermAvro
from fabric.message_bus.messages.UpdateDataAvro import UpdateDataAvro
from fabric.message_bus.messages.UpdateReservationAvro import UpdateReservationAvro
from fabric.message_bus.messages.UpdateSliceAvro import UpdateSliceAvro
from fabric.message_bus.messages.UpdateTicketAvro import UpdateTicketAvro
from fabric.message_bus.messages.message import IMessageAvro
from fabric.message_bus.producer import AvroProducerApi


class MessageBusTest(unittest.TestCase):
    def test_consumer_producer(self):
        from confluent_kafka import avro
        from threading import Thread
        import time

        conf = {'bootstrap.servers': "localhost:9092"}
        # Create Admin API object
        api = AdminApi(conf)

        for a in api.list_topics():
            print("Topic {}".format(a))

        #tt = ["fabric-broker-topic", "fabric-vm-am-topic"]
        #api.delete_topics(tt)

        topics = ['fabric-mb-public-test1', 'fabric-mb-public-test2']

        # create topics
        api.delete_topics(topics)
        api.create_topics(topics, num_partitions=1, replication_factor=1)

        # load AVRO schema
        file = open('../schema/key.avsc', "r")
        key_bytes = file.read()
        file.close()
        key_schema = avro.loads(key_bytes)
        file = open('../schema/message.avsc', "r")
        val_bytes = file.read()
        file.close()
        val_schema = avro.loads(val_bytes)

        conf['schema.registry.url']="http://localhost:8081"

        # create a producer
        producer = AvroProducerApi(conf, key_schema, val_schema)

        # push messages to topics

        # udd
        udd = UpdateDataAvro()
        udd.message = "message"
        udd.failed = False

        auth = AuthAvro()
        auth.guid = "testguid"
        auth.name = "testactor"

        # Query
        query = QueryAvro()
        query.message_id = "msg1"
        query.callback_topic = "topic"
        query.properties = {"abc": "def"}
        query.auth = auth
        #print(query.to_dict())
        producer.produce_sync("topic1", query)

        # QueryResult
        query_result = QueryResultAvro()
        query_result.message_id = "msg2"
        query_result.request_id = "req2"
        query_result.properties = {"abc": "def"}
        query_result.auth = auth
        #print(query_result.to_dict())
        producer.produce_sync("topic2", query_result)

        # FailedRPC
        failed_rpc = FailedRPCAvro()
        failed_rpc.message_id = "msg3"
        failed_rpc.request_id = "req3"
        failed_rpc.reservation_id = "rsv_abc"
        failed_rpc.request_type = 1
        failed_rpc.error_details = "test error message"
        failed_rpc.auth = auth
        #print(failed_rpc.to_dict())
        producer.produce_sync("fabric-mb-public-test2", failed_rpc)

        claim_req = ClaimResourcesAvro()
        claim_req.guid = "dummy-guid"
        claim_req.auth = auth
        claim_req.broker_id = "brokerid"
        claim_req.reservation_id = "rsv_id"
        claim_req.message_id = "test_claim_1"
        claim_req.callback_topic = "test"

        #print(claim_req.to_dict())
        producer.produce_sync("fabric-mb-public-test2", claim_req)

        reservation = ReservationAvro()
        reservation.reservation_id = "res123"
        reservation.sequence = 1
        reservation.slice = SliceAvro()
        reservation.slice.guid = "slice-12"
        reservation.slice.slice_name = "test_slice"
        reservation.term = TermAvro()
        reservation.term.start_time = 1593854111999
        reservation.term.end_time = 1593854111999
        reservation.term.new_start_time = 1593854111999
        reservation.resource_set = ResourceSetAvro()
        reservation.resource_set.units = 0
        reservation.resource_set.type = "type1"
        reservation.resource_set.resource_data = ResourceDataAvro()
        reservation.resource_set.resource_data.request_properties = {'type': 'site.vlan', 'label': 'Net AM',
                                                                     'attributescount': '1',
                                                                     'attribute.0.key': 'resource.class.invfortype',
                                                                     'resource.class.invfortype.type': '6',
                                                                     'resource.class.invfortype.value': 'actor.core.policy.SimplerUnitsInventory.SimplerUnitsInventory',
                                                                     'pool.name': 'Net AM'}

        reservation.resource_set.concrete = b'\x80\x04\x95\xb9\x02\x00\x00\x00\x00\x00\x00\x8c\x16actor.core.core.Ticket\x94\x8c\x06Ticket\x94\x93\x94)\x81\x94}\x94(\x8c\tauthority\x94\x8c,actor.core.proxies.kafka.KafkaAuthorityProxy\x94\x8c\x13KafkaAuthorityProxy\x94\x93\x94)\x81\x94}\x94(\x8c\nproxy_type\x94\x8c\x05kafka\x94\x8c\x08callback\x94\x89\x8c\nactor_name\x94\x8c\x0cfabric-vm-am\x94\x8c\nactor_guid\x94\x8c\x12actor.core.util.ID\x94\x8c\x02ID\x94\x93\x94)\x81\x94}\x94\x8c\x02id\x94\x8c\x11fabric-vm-am-guid\x94sb\x8c\x04auth\x94\x8c\x18actor.security.AuthToken\x94\x8c\tAuthToken\x94\x93\x94)\x81\x94}\x94(\x8c\x04name\x94h\x0f\x8c\x04guid\x94h\x14ub\x8c\x0bkafka_topic\x94\x8c\x12fabric-vm-am-topic\x94\x8c\x04type\x94K\x03\x8c\x10bootstrap_server\x94\x8c\x0elocalhost:9092\x94\x8c\x0fschema_registry\x94\x8c\x15http://localhost:8081\x94\x8c\x0fkey_schema_file\x94\x8cK/Users/komalthareja/renci/code/fabric/ActorBase/message_bus/schema/key.avsc\x94\x8c\x11value_schema_file\x94\x8cO/Users/komalthareja/renci/code/fabric/ActorBase/message_bus/schema/message.avsc\x94ub\x8c\x0fresource_ticket\x94N\x8c\told_units\x94K\x0fub.'

        claim = ClaimAvro()
        claim.auth = auth
        claim.message_id = "msg4"
        claim.callback_topic = "test"
        claim.reservation = reservation
        #print(claim.to_dict())
        producer.produce_sync("fabric-mb-public-test2", claim)

        # Redeem
        redeem = RedeemAvro()
        redeem.message_id = "msg4"
        redeem.callback_topic = "test"
        redeem.reservation = reservation
        #print(redeem.to_dict())
        producer.produce_sync("fabric-mb-public-test2", redeem)

        update_ticket = UpdateTicketAvro()
        update_ticket.auth = auth
        update_ticket.message_id = "msg11"
        update_ticket.callback_topic = "test"
        update_ticket.reservation = reservation
        update_ticket.update_data = UpdateDataAvro()
        update_ticket.update_data.failed = False

        #print(update_ticket.to_dict())
        producer.produce_sync("fabric-mb-public-test2", update_ticket)

        get_slice = GetSlicesRequestAvro()
        get_slice.auth = auth
        get_slice.message_id = "msg11"
        get_slice.callback_topic = "test"
        get_slice.guid = "guid"

        #print(get_slice.to_dict())

        producer.produce_sync("fabric-mb-public-test2", get_slice)

        result = ResultAvro()
        result.code = 0

        slice_res = GetSlicesResponseAvro()
        slice_res.message_id = "msg11"
        slice_res.status = result

        s1 = SliceAvro()
        s1.set_slice_name("abc")
        s1.set_slice_id("11111")
        s1.set_owner(auth)
        s1.set_description("abcd")
        prop = {}
        s1.set_config_properties(prop)
        s1.set_resource_type('site.vm')
        s1.set_client_slice(False)
        s1.set_broker_client_slice(False)

        slice_res.slices = []
        slice_res.slices.append(s1)

        #print(slice_res.to_dict())

        producer.produce_sync("fabric-mb-public-test2", slice_res)

        res_req = GetReservationsRequestAvro()
        res_req.message_id = "abc123"
        res_req.callback_topic = "test"
        res_req.guid = "guid"

        print(res_req.to_dict())

        producer.produce_sync("fabric-mb-public-test2", res_req)

        res = ReservationMng()
        res.reservation_id = "abcd123"
        res.rtype = 'site.baremetalce'
        res.notices = 'noice'
        res.slice_id = "slice_1"
        res.start = 1264827600000
        res.end = 1927515600000
        res.requested_end = 1927515600000
        res.state = 2
        res.pending_state = 1

        res_list = [res]

        res_res = GetReservationsResponseAvro()
        res_res.message_id = res_req.message_id
        res_res.status = result
        res_res.reservations = res_list

        #print(res_res.to_dict())

        producer.produce_sync("fabric-mb-public-test2", res_res)

        remove_slice = RemoveSliceAvro()
        remove_slice.message_id = "msg1"
        remove_slice.guid = 'guid1'
        remove_slice.slice_id = 'slice1'
        remove_slice.callback_topic = 'test_topic'
        remove_slice.auth = auth
        #print(remove_slice.to_dict())

        producer.produce_sync("fabric-mb-public-test2", remove_slice)

        status_resp = StatusResponseAvro()
        status_resp.message_id = "msg1"
        status_resp.result = "abc"
        status_resp.status = result

        producer.produce_sync("fabric-mb-public-test2", status_resp)

        add_slice = AddSliceAvro()
        add_slice.message_id = "msg1"
        add_slice.guid = 'guid1'
        add_slice.slice_obj = s1
        add_slice.callback_topic = 'test_topic'
        add_slice.auth = auth
        # print(add_slice.to_dict())

        producer.produce_sync("fabric-mb-public-test2", add_slice)

        update_slice = UpdateSliceAvro()
        update_slice.message_id = "msg1"
        update_slice.guid = 'guid1'
        update_slice.slice_obj = s1
        update_slice.callback_topic = 'test_topic'
        update_slice.auth = auth
        # print(update_slice.to_dict())

        producer.produce_sync("fabric-mb-public-test2", update_slice)

        remove_res = RemoveReservationAvro()
        remove_res.message_id = "msg1"
        remove_res.guid = 'guid1'
        remove_res.reservation_id = 'rid1'
        remove_res.callback_topic = 'test_topic'
        remove_res.auth = auth
        # print(remove_res.to_dict())

        producer.produce_sync("fabric-mb-public-test2", remove_res)

        close_res = CloseReservationsAvro()
        close_res.message_id = "msg1"
        close_res.guid = 'guid1'
        close_res.reservation_id = 'rid1'
        close_res.callback_topic = 'test_topic'
        close_res.auth = auth
        # print(close_res.to_dict())

        producer.produce_sync("fabric-mb-public-test2", close_res)

        update_res = UpdateReservationAvro()
        update_res.message_id = "msg1"
        update_res.guid = 'guid1'
        update_res.reservation_obj = res
        update_res.callback_topic = 'test_topic'
        update_res.auth = auth
        print(update_res.to_dict())

        producer.produce_sync("fabric-mb-public-test2", update_res)

        # Fallback to earliest to ensure all messages are consumed
        conf['group.id'] = "example_avro"
        conf['auto.offset.reset'] = "earliest"

        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("++++++++++++++++++++++CONSUMER+++++++++++++++++++++")
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        class TestConsumer(AvroConsumerApi):
            def set_parent(self, parent):
                self.parent = parent

            def handle_message(self, message: IMessageAvro):
                if message.get_message_name() == IMessageAvro.Query:
                   self.parent.validate_query(message, query)

                elif message.get_message_name() == IMessageAvro.QueryResult:
                   self.parent.validate_query_result(message, query_result)

                elif message.get_message_name() == IMessageAvro.FailedRPC:
                   self.parent.validate_failed_rpc(message, failed_rpc)

                elif message.get_message_name() == IMessageAvro.ClaimResources:
                   self.parent.validate_claim_resources(message, claim_req)

                elif message.get_message_name() == IMessageAvro.Claim:
                   self.parent.validate_claim(message, claim)

                elif message.get_message_name() == IMessageAvro.Redeem:
                   self.parent.validate_redeem(message, redeem)

                elif message.get_message_name() == IMessageAvro.UpdateTicket:
                   self.parent.validate_update_ticket(message, update_ticket)

                elif message.get_message_name() == IMessageAvro.GetSlicesRequest:
                   self.parent.validate_get_slices_request(message, get_slice)

                elif message.get_message_name() == IMessageAvro.GetSlicesResponse:
                   self.parent.validate_get_slices_response(message, slice_res)

                elif message.get_message_name() == IMessageAvro.GetReservationsRequest:
                   self.parent.validate_get_reservations_request(message, res_req)

                elif message.get_message_name() == IMessageAvro.GetReservationsResponse:
                   self.parent.validate_get_reservations_response(message, res_res)

                elif message.get_message_name() == IMessageAvro.RemoveSlice:
                    self.parent.validate_remove_slice(message, remove_slice)

                elif message.get_message_name() == IMessageAvro.StatusResponse:
                    self.parent.validate_status_response(message, status_resp)

                elif message.get_message_name() == IMessageAvro.AddSlice:
                    self.parent.validate_add_slice(message, add_slice)

                elif message.get_message_name() == IMessageAvro.UpdateSlice:
                    self.parent.validate_update_slice(message, update_slice)

                elif message.get_message_name() == IMessageAvro.RemoveReservation:
                    self.parent.validate_remove_reservation(message, remove_res)

                elif message.get_message_name() == IMessageAvro.CloseReservations:
                    self.parent.validate_close_reservation(message, close_res)

                elif message.get_message_name() == IMessageAvro.UpdateReservation:
                    self.parent.validate_update_reservation(message, update_res)



        # create a consumer
        consumer = TestConsumer(conf, key_schema, val_schema, topics)
        consumer.set_parent(self)

        # start a thread to consume messages
        consume_thread = Thread(target=consumer.consume_auto, daemon=True)
        # consume_thread = Thread(target = consumer.consume_sync, daemon=True)

        consume_thread.start()
        time.sleep(10)

        # trigger shutdown
        consumer.shutdown()

        # delete topics
        api.delete_topics(topics)

    def validate_query(self, incoming: QueryAvro, outgoing: QueryAvro):
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.message_id, outgoing.message_id)
        self.assertEqual(incoming.properties, outgoing.properties)
        self.assertEqual(incoming.auth, outgoing.auth)
        self.assertEqual(incoming.callback_topic, outgoing.callback_topic)

    def validate_query_result(self, incoming: QueryResultAvro, outgoing: QueryResultAvro):
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.message_id, outgoing.message_id)
        self.assertEqual(incoming.request_id, outgoing.request_id)
        self.assertEqual(incoming.properties, outgoing.properties)
        self.assertEqual(incoming.auth, outgoing.auth)

    def validate_failed_rpc(self, incoming: FailedRPCAvro, outgoing: FailedRPCAvro):
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.message_id, outgoing.message_id)
        self.assertEqual(incoming.error_details, outgoing.error_details)
        self.assertEqual(incoming.request_type, outgoing.request_type)
        self.assertEqual(incoming.reservation_id, outgoing.reservation_id)
        self.assertEqual(incoming.request_id, outgoing.request_id)
        self.assertEqual(incoming.auth, outgoing.auth)

    def validate_claim_resources(self, incoming: ClaimResourcesAvro, outgoing: ClaimResourcesAvro):
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.message_id, outgoing.message_id)
        self.assertEqual(incoming.guid, outgoing.guid)
        self.assertEqual(incoming.broker_id, outgoing.broker_id)
        self.assertEqual(incoming.reservation_id, outgoing.reservation_id)
        self.assertEqual(incoming.slice_id, outgoing.slice_id)
        self.assertEqual(incoming.auth, outgoing.auth)
        self.assertEqual(incoming.callback_topic, outgoing.callback_topic)

    def validate_claim(self, incoming: ClaimAvro, outgoing: ClaimAvro):
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.message_id, outgoing.message_id)
        self.assertEqual(incoming.reservation, outgoing.reservation)
        self.assertEqual(incoming.auth, outgoing.auth)
        self.assertEqual(incoming.callback_topic, outgoing.callback_topic)

    def validate_redeem(self, incoming: RedeemAvro, outgoing: RedeemAvro):
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.message_id, outgoing.message_id)
        self.assertEqual(incoming.reservation, outgoing.reservation)
        self.assertEqual(incoming.auth, outgoing.auth)
        self.assertEqual(incoming.callback_topic, outgoing.callback_topic)

    def validate_update_ticket(self, incoming: UpdateTicketAvro, outgoing: UpdateTicketAvro):
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.message_id, outgoing.message_id)
        self.assertEqual(incoming.reservation, outgoing.reservation)
        self.assertEqual(incoming.update_data, outgoing.update_data)
        self.assertEqual(incoming.auth, outgoing.auth)
        self.assertEqual(incoming.callback_topic, outgoing.callback_topic)

    def validate_get_slices_request(self, incoming: GetSlicesRequestAvro, outgoing: GetSlicesRequestAvro):
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.guid, outgoing.guid)
        self.assertEqual(incoming.message_id, outgoing.message_id)
        self.assertEqual(incoming.slice_id, outgoing.slice_id)
        self.assertEqual(incoming.auth, outgoing.auth)
        self.assertEqual(incoming.callback_topic, outgoing.callback_topic)

    def validate_get_slices_response(self, incoming: GetSlicesResponseAvro, outgoing: GetSlicesResponseAvro):
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.message_id, outgoing.message_id)
        self.assertEqual(incoming.slices, outgoing.slices)
        self.assertEqual(incoming.reservations, outgoing.reservations)
        self.assertEqual(incoming.status, outgoing.status)

    def validate_get_reservations_request(self, incoming: GetReservationsRequestAvro, outgoing: GetReservationsRequestAvro):
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.guid, outgoing.guid)
        self.assertEqual(incoming.message_id, outgoing.message_id)
        self.assertEqual(incoming.slice_id, outgoing.slice_id)
        self.assertEqual(incoming.reservation_id, outgoing.reservation_id)
        self.assertEqual(incoming.reservation_state, outgoing.reservation_state)
        self.assertEqual(incoming.auth, outgoing.auth)
        self.assertEqual(incoming.callback_topic, outgoing.callback_topic)

    def validate_get_reservations_response(self, incoming: GetReservationsResponseAvro, outgoing: GetReservationsResponseAvro):
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.message_id, outgoing.message_id)
        self.assertEqual(incoming.slices, outgoing.slices)
        self.assertEqual(incoming.reservations, outgoing.reservations)
        self.assertEqual(incoming.status, outgoing.status)

    def validate_remove_slice(self, incoming: RemoveSliceAvro, outgoing: RemoveSliceAvro):
        self.assertEqual(incoming.auth, outgoing.auth)
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.guid, outgoing.guid)
        self.assertEqual(incoming.slice_id, outgoing.slice_id)
        self.assertEqual(incoming.callback_topic, outgoing.callback_topic)

    def validate_status_response(self, incoming: StatusResponseAvro, outgoing: StatusResponseAvro):
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.message_id, outgoing.message_id)
        self.assertEqual(incoming.result, outgoing.result)
        self.assertEqual(incoming.status, outgoing.status)

    def validate_add_slice(self, incoming: AddSliceAvro, outgoing: AddSliceAvro):
        self.assertEqual(incoming.auth, outgoing.auth)
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.guid, outgoing.guid)
        self.assertEqual(incoming.slice_obj, outgoing.slice_obj)
        self.assertEqual(incoming.callback_topic, outgoing.callback_topic)

    def validate_update_slice(self, incoming: UpdateSliceAvro, outgoing: UpdateSliceAvro):
        self.assertEqual(incoming.auth, outgoing.auth)
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.guid, outgoing.guid)
        self.assertEqual(incoming.slice_obj, outgoing.slice_obj)
        self.assertEqual(incoming.callback_topic, outgoing.callback_topic)

    def validate_remove_reservation(self, incoming: RemoveReservationAvro, outgoing: RemoveReservationAvro):
        self.assertEqual(incoming.auth, outgoing.auth)
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.guid, outgoing.guid)
        self.assertEqual(incoming.reservation_id, outgoing.reservation_id)
        self.assertEqual(incoming.callback_topic, outgoing.callback_topic)

    def validate_close_reservation(self, incoming: CloseReservationsAvro, outgoing: CloseReservationsAvro):
        self.assertEqual(incoming.auth, outgoing.auth)
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.guid, outgoing.guid)
        self.assertEqual(incoming.slice_id, outgoing.slice_id)
        self.assertEqual(incoming.reservation_id, outgoing.reservation_id)
        self.assertEqual(incoming.reservation_state, outgoing.reservation_state)
        self.assertEqual(incoming.callback_topic, outgoing.callback_topic)

    def validate_update_reservation(self, incoming: UpdateReservationAvro, outgoing: UpdateReservationAvro):
        self.assertEqual(incoming.auth, outgoing.auth)
        self.assertEqual(incoming.name, outgoing.name)
        self.assertEqual(incoming.guid, outgoing.guid)
        self.assertEqual(incoming.reservation_obj, outgoing.reservation_obj)
        self.assertEqual(incoming.callback_topic, outgoing.callback_topic)