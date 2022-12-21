# -*- coding: utf-8 -*-

"""
Created on Nov 22, 2022

Modified on Dec 15, 2022

@author: hilee, Francisco
"""

import pika
import threading
import time as ti

# RabbitMQ communication
class MsgMiddleware():
    
    def __init__(self, iam, ip_addr, id, pwd, exchange, type, producer = False):
        
        self.iam = iam       
        self.ip_addr = ip_addr
        self.id = id
        self.pwd = pwd
        
        self.exchange = exchange
        self.type = type
        self.producer = producer
                
        self.channel = None
        self.connection = None
        
        self.queue = None
        
        
    def __del__(self):
        
        for th in threading.enumerate():
            print(th.name + " exit.")
            
        if self.producer:
            print(self.iam, 'Closed rabbitmq queue and connections (producer)')
        else:
            print(self.iam, 'Closed rabbitmq queue and connections (consumer)')
      
        if self.producer is False:
            self.channel.cancel()
            if self.queue:
                self.stop_consumer()        
        try:
            if self.connection.is_open:
                self.connection.close()
        except Exception as e:
            raise
                                   

    def connect_to_server(self):
        try:       
            id_pwd = pika.PlainCredentials(self.id, self.pwd)
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.ip_addr, port=5672, credentials=id_pwd, heartbeat=0, tcp_options={"TCP_KEEPIDLE":60}))
            self.channel = self.connection.channel()
                        
        except Exception as e:
            print(self.iam, "cannot connect to RabbitMQ server.\r\nPlease check the server and try again!")
            raise 

        
    # as producer
    def define_producer(self):
        try:
            self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.type)
                    
        except Exception as e:
            print(self.iam, "cannot define producer.\r\nPlease check the server and try again!")
            raise
        
    
    def send_message(self, target, _routing_key, _message):        
        '''
        th = threading.Thread(self.publish, args=(target, _routing_key, _message))
        th.start()
        
    def publish(self, target, _routing_key, _message):
        '''
        if target == "tmc1" or target == "pdu" or target == "vm":
            ti.sleep(0.7)
        else:
            ti.sleep(0.2)
                
        try:
            self.channel.basic_publish(exchange=self.exchange, routing_key=_routing_key, body=_message.encode())
            
        except Exception as e:
            print("Cannot send the {_message} for the {_routing_key} provider.")
            raise
    
    
    # as consumer
    def define_consumer(self, _routing_key, _callback):        
        try:
            #if self.queue is None:
            self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.type)
            result = self.channel.queue_declare(queue='', durable=True, exclusive=True)
            self.queue = result.method.queue
            print(f"queueName= {self.queue}")
            
            self.channel.queue_bind(exchange=self.exchange, queue=self.queue, routing_key=_routing_key)
            self.channel.basic_consume(queue=self.queue, on_message_callback=_callback, auto_ack=True)

        except Exception as e:
            print(self.iam, "cannot define consumer for the {_routing_key} provider.")      
            raise 
                
        
    def start_consumer(self):
        try:
            if self.queue:
                self.channel.start_consuming()
                
        except Exception as e:            
            print("Error starting consuming msg")         
            raise
        
        
               
    def stop_consumer(self):        
        try:
            if self.queue:
                self.channel.stop_consuming()
            
                ti.sleep(3)
                
        except Exception as e:
            print("Error stopping consuming msg")
            raise

        

    
        

            