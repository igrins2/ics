# -*- coding: utf-8 -*-

"""
Created on Sep 15, 2022

Modified on , 2022

@author: hilee
"""

import pika

# ics -> dcs gui consumer
# ics <- dcs core producer

class ICS_SERVER():
    def __init__(self, ip_addr, id, pwd, ics_exchange, ics_routing_key, type, dcs_exchange, dcs_routing_key):
        self.ip_addr = ip_addr
        self.id = id
        self.pwd = pwd
        self.ics_exchange = ics_exchange
        self.ics_routing_key = ics_routing_key
        self.type = type
        self.dcs_exchange = dcs_exchange
        self.dcs_routing_key = dcs_routing_key
        
        self.com_sts = False

    # RabbitMQ communication
    def connect_to_server(self, name):
        try:       
            id_pwd = pika.PlainCredentials(self.id, self.pwd)
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.ip_addr, port=5672, credentials=id_pwd))
            channel = connection.channel()

            self.com_sts = True

            return connection, channel
            
        except:
            print(name, "cannot connect to RabbitMQ server.\r\nPlease check the server and try again!")
            return None, None


    # as producer
    def define_producer(self, channel, name):
        if self.com_sts == False:
            return False

        try:
            channel.exchange_declare(exchange=self.ics_exchange, exchange_type=self.type)
            return True
        
        except:
            print(name, "cannot define producer.\r\nPlease check the server and try again!")
            return False


    # as consumer
    def define_consumer(self, channel, name):
        if self.com_sts == False:
            return None

        try:
            channel.exchange_declare(exchange=self.dcs_exchange, exchange_type=self.type)
            result = channel.queue_declare(queue='', exclusive=True)
            _queue = result.method.queue
            channel.queue_bind(exchange=self.dcs_exchange, queue=_queue, routing_key=self.dcs_routing_key)
            return _queue
        
        except:
            print(name, "cannot define consumer.\r\nPlease check the server and try again!")
            return None


    # as producer
    def send_message(self, channel, producers, consumers, message):
        if self.com_sts == False:
            return

        channel.basic_publish(exchange=self.ics_exchange, routing_key=self.ics_routing_key, body=message.encode())
        msg = '[%s->%s] %s' % (producers, consumers, message)
        print(msg)
            

        