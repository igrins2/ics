#!/usr/bin/env python
import pika
import time

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()


channel.queue_declare(queue='hello')

#channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')

for i in range(10):
    time.sleep(1)
    message = 'Hello World %d' % (i+1)
    channel.basic_publish(exchange='', routing_key='hello', body=message)
    print(" [x] Sent " + message)
    
connection.close()