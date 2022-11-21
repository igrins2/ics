# -*- coding: utf-8 -*-

"""
Created on Sep 15, 2022

Modified on Oct 24, 2022

@author: hilee
"""

import pika

# ics -> dcs gui consumer
# ics <- dcs core producer

# RabbitMQ communication
def connect_to_server(iam, ip_addr, id, pwd):
    try:       
        id_pwd = pika.PlainCredentials(id, pwd)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=ip_addr, port=5672, credentials=id_pwd, heartbeat=0, tcp_options={"TCP_KEEPIDLE":60}))
        channel = connection.channel()
        return connection, channel
        
    except:
        print(iam, "cannot connect to RabbitMQ server.\r\nPlease check the server and try again!")
        return None, None
    
# as producer
def define_producer(iam, channel, type, _exchange):
    try:
        channel.exchange_declare(exchange=_exchange, exchange_type=type)
        return True
    
    except:
        print(iam, "cannot define producer.\r\nPlease check the server and try again!")
        return False
    
# as consumer
def define_consumer(iam, channel, type, _exchange, _routing_key):
    try:
        channel.exchange_declare(exchange=_exchange, exchange_type=type)
        result = channel.queue_declare(queue='', exclusive=True)
        _queue = result.method.queue
        channel.queue_bind(exchange=_exchange, queue=_queue, routing_key=_routing_key)
        return _queue
    
    except:
        print(iam, "cannot define consumer.\r\nPlease check the server and try again!")
        return None
    
# as producer
def send_message(iam, target, channel, _exchange, _routing_key, message):
    channel.basic_publish(exchange=_exchange, routing_key=_routing_key, body=message.encode())
    msg = '[%s->%s] %s' % (iam, target, message)
    print(msg)
    

        