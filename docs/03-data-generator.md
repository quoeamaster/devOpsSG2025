# ⚙️ 03. Docker: Python

In this section, we'll set up the Docker configuration required to run the Python powered data generator. By the end, you'll have:
- Python Docker container running
- data generator running within the container

---

## 📦 Prerequisites

### ✅ 1. Docker configuration for Python (docker-compose.yml)

Add a new section in the docker-compose.yml as follows
```yaml
...
  python:
    image: python:3.13.3
    container_name: python
    depends_on:
      - clickhouse
    volumes:
      - ./../src:/src
    command: >
      sh -c "pip3 install --no-cache-dir --root-user-action=ignore clickhouse_connect==0.7.0 scikit-learn==1.6.1 matplotlib==3.10.1 pandas==2.2.3 &&
            python3 /src/log_generator.py"
...
```
Aligning with the same logic, we will be using a specific version of every Docker image involved. For Python we are picking version `3.13.3`. 

A specific container name is applied for debug and interactive purposes, `python` is picked. 

There is docker container dependancies listed here `clickhouse` which simply means the clickhouse container MUST be running before instantiating the Python container.

### ✅ 2. python library dependancies installation

```yaml
...
    command: >
      sh -c "pip3 install --no-cache-dir --root-user-action=ignore clickhouse_connect==0.7.0 scikit-learn==1.6.1 matplotlib==3.10.1 pandas==2.2.3 &&
            python3 /src/log_generator.py"
...
```            
We have mentioned the bulky and messy `command` section earlier, the python container is an example on how it feels and works with the section. We simply run a bash shell to install various libraries via `pip3`
- clickhouse-connect (for connecting to ClickHouse)
- scikit-learn (for Machine Learning script)
- panda (for Machine Learning script)
- matplotlib (for debugging purposes only)

and finally we run the data generator script as follows:
```yaml
...
&& python3 /src/log_generator.py
...
```

A note on the python libraries, technically we do not need matplotlib unless you would like to debug visually on the dataset. Again for simplicity, we would install all libraries here.

---

Another note on this setup...

You would see that everytime when we start the python container, it would go through the library installation step. To avoid such a time consuming operation we could build our own image instead through creating a `dockerfile`. For simplicity, we would just keep the setup as is.

### ✅ 3. python data generator script

The script is pretty straightforward and available at [here](https://github.com/quoeamaster/devOpsSG2025/blob/main/src/log_generator.py). We would go through a few sections as well.

```python
...
client = clickhouse_connect.get_client(
    host='clickhouse',
    port=8123,
    username='demo_user',
    password='P@ssword1',
)
...
``` 
We create a global client object. Do not that the `host` value would need to match the Docker container's name in which it is `clickhouse` in this case. Never use the value `localhost` as there is no container named localhost within the Docker network.

Port value is `8123` which is the http port. User and password would be the credentials we have created in the previous [setup](02-clickhouse.md).

---
There are various helper functions to generate the data set, we will look at the core generate_log function here

```python
...
def generate_log():
    normal_response_time = random.randint(100, 500)  # Normal response time
    anomaly = random.random() < 0.1  # 10% chance of an anomaly
    response_time = random.randint(2000, 5000) if anomaly else normal_response_time
    
    # pick random service and message building
    ts = time.strftime("%Y-%m-%d %H:%M:%S.000")
    service = get_random_service()

    log_entry = {
        "timestamp": ts,
        "message": generate_random_message(response_time, ts, service)
    }
    client.command(f"insert into default.sample_logs (timestamp, message) values (toDateTime64('{log_entry['timestamp']}', 3), '{log_entry['message']}' )")
...
```
variable `normal_response_time` is a random value within the range 100 .. 500. Variable `anomaly` is a 10% propability value to determine if the to-be generate data should have an anomaly response time. Variable `response_time` is the final value generated based on considering the anomaly variable's value (True or False).

`log_entry` is the data row (json / object format) to be generated. It will call the function `generate_random_message` which simply is picking a pre-built string message and replacing some arguments.

Finally, we insert this log entry to ClickHouse container. The `command` function is utilized and we simply provide the SQL insert statement directly.

---

Remember to update the `volume` in docker-compose.yml
```yaml
...
    volumes:
      - ./../src:/src
...
```
our setup (check the github repo [here](https://github.com/quoeamaster/devOpsSG2025/)) puts all python scripts inside the `src` folder and that is why the Docker volume section is configured as above and we are copying the scripts to the container's `/src` location. Make sure that this target folder location matches with the `command` section above or else your data generator script would fail to run

### ✅ 3. python container debugging

In general it is very challenging to debug the python container as there is no obvious ways to obtain logs from stdout or stderr. Thankfully Docker provides a mechanism to read the stdout / stderr of a running container via

```bash
docker logs python -f
```

By now you should be able to see the python container's console output. Normally if everything is ok, we should not see any error messages showing in the logs. Worst case scenarios are that you would see some python exeecution errors, by then you would know something is wrong with the script(s) and need to start debugging.

### ✅ 4. data generation validation

we can login to the `clickhouse` container by 
```bash
docker exec -it clickhouse /bin/bash
```

after logging in, run the following commands
```bash
mac$ docker_files % docker exec -it clickhouse /bin/bash

root@562021eb5b31:/# clickhouse client

ClickHouse client version 25.2.2.39 (official build).
Connecting to localhost:9000 as user default.
Connected to ClickHouse server version 25.2.2.

Warnings:
 * Linux transparent hugepages are set to "always". Check /sys/kernel/mm/transparent_hugepage/enabled
 * Delay accounting is not enabled, OSIOWaitMicroseconds will not be gathered. You can enable it using `echo 1 > /proc/sys/kernel/task_delayacct` or by using sysctl.

562021eb5b31 :) select count() from sample_logs_analytics;

SELECT count()
FROM sample_logs_analytics

Query id: d172bdd1-e3bc-455f-8fbf-5d03e8230b09

   ┌─count()─┐
1. │   19381 │
   └─────────┘

1 row in set. Elapsed: 0.012 sec. 

562021eb5b31 :) 
```

if the Python data generator is working as expected, we would see the `count()` SQL returning a number, if we run the same SQL for a few times, we should notice the number is incremented.

```sql
select count() from sample_logs_analytics;
```

<div style="text-align:center; margin-top: 20px; font-size: 20px;">

🔧 [prev - clickhouse](02-clickhouse.md) &nbsp;&nbsp;&nbsp; 🔍 [next - grafana](04-grafana.md)

</div>

