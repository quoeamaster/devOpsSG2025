import time
import random
import clickhouse_connect
import json
import socket

client = clickhouse_connect.get_client(
    host='clickhouse',
    port=8123,
    username='demo_user',
    password='P@ssword1',
)

def get_random_service():
    return random.choice(["api-service", "web-service", "database-service"])

def generate_random_message(response_time, timestamp, service):
    # pattern 
    # [{level}][{timestamp}] {service} : {message} - {response_time}
    choices = [
        "[SUCCESS][{}] {} : operation completed - {}".format(timestamp, service, response_time),
        "[ERROR][{}] {} : API endpoint not available - {}".format(timestamp, service, response_time),
        "[ERROR][{}] {} : Illegal argument - {}".format(timestamp, service, response_time),
        "[ERROR][{}] {} : 401 unauthorized - {}".format(timestamp, service, response_time),
        "[ERROR][{}] {} : missing parameter - {}".format(timestamp, service, response_time),
        "[WARNING][{}] {} : memory consumption over 70 percent - {}".format(timestamp, service, response_time),
        "[WARNING][{}] {} : computation power is exhausted, over 60 percent consumed - {}".format(timestamp, service, response_time),
    ]

    return random.choice(choices)

def generate_log():
    normal_response_time = random.randint(100, 500)  # Normal response time
    anomaly = random.random() < 0.1  # 10% chance of an anomaly
    response_time = random.randint(2000, 5000) if anomaly else normal_response_time
    
    # pick random service and message building
    ts = time.strftime("%Y-%m-%d %H:%M:%S.000")
    service = get_random_service()

    # [todo]
    # update the log_entry to only having timestamp and message
    # let MV to extract the values of service, response_time, LEVEL
    # total 5 fields
    log_entry = {
        "timestamp": ts,
        #"service": service,
        #"response_time": response_time,
        "message": generate_random_message(response_time, ts, service)
    }
    #client.command(f"insert into default.sample_logs (timestamp, service, response_time, message) values (toDateTime64('{log_entry['timestamp']}', 3), '{log_entry['service']}', {log_entry['response_time']}, '{log_entry['message']}' )")
    client.command(f"insert into default.sample_logs (timestamp, message) values (toDateTime64('{log_entry['timestamp']}', 3), '{log_entry['message']}' )")
    
while True:
    generate_log()
    time.sleep(3)  # Generate logs every n second

# ddl schema
# {  
#   timestamp DateTime64(3),
#   service String,
#   response_time UInt16,
#   message String
# }
