from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='localhost:9092')
msg1=dict({'first_name':'bhk','last_name':'kum','company_name':'test'})
producer.send('test', bytes(str(msg1), 'utf-8'))

producer.flush()

