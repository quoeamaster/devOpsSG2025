# ⚙️ 05. Docker: Python ML execution

In this section, we'll explore the ML workflow within the `python` Docker container. By the end, you'll have:
- Python Docker container running (should be running already)
- ML operation running within the container

---

## 📦 Prerequisites

### ✅ 1. Docker running verfication

typically at this stage, the `python` container should be running; verify by the following:
```bash
docker ps -a

CONTAINER ID   IMAGE                               COMMAND                  CREATED       STATUS                 PORTS                                                      NAMES
...
abd3e4d73c2f   python:3.13.3                       "sh -c 'pip3 install…"   2 hours ago   Up 2 hours                                                                        python
...
```

### ✅ 2. running the ML script

first of all, log into the python container by:
```bash
docker exec -it python /bin/bash
```

once you have logged in, run the following commands:
```bash
# this is where the python scripts are located
root@abd3e4d73c2f:/src# cd /src

# check if the scripts are mounted correctly, we are focusing on the `anomaly_detection.py`
root@abd3e4d73c2f:/src# ls -l
total 8
-rw-r--r-- 1 root root 1839 May  1 06:13 anomaly_detection.py
-rw-r--r-- 1 root root 2551 May  3 22:44 log_generator.py
drwxr-xr-x 3 root root   96 Apr 16 20:12 obsolete

# execute the script
python3 anomaly_detection.py

# sample outputs
...
Anomaly detected at 2025-05-03 19:25:39 with response time 2984 ms -> timestamp        2025-05-03 19:25:39
response_time                   2984
cluster                            1
is_anomaly                      True
Name: 4960, dtype: object
Anomaly detected at 2025-05-03 19:24:49 with response time 4608 ms -> timestamp        2025-05-03 19:24:49
response_time                   4608
cluster                            1
is_anomaly                      True
Name: 4976, dtype: object
Anomaly detected at 2025-05-03 19:24:17 with response time 3714 ms -> timestamp        2025-05-03 19:24:17
response_time                   3714
cluster                            1
is_anomaly                      True
Name: 4986, dtype: object
...
```

### ✅ 3. verification on the ClickHouse side

Though we just see the sample output of the python script; it is recommended to verify such through either...
- Grafana dashboard - by adding a widget showing the data from table `sample_logs_anomaly`
- ClickHouse Docker container directly (steps available as follows)

if we are into the ClickHouse Docker approach, run the following:
```bash
mac$ docker_files % docker exec -it clickhouse /bin/bash

root@562021eb5b31:/# clickhouse client

ClickHouse client version 25.2.2.39 (official build).
Connecting to localhost:9000 as user default.
Connected to ClickHouse server version 25.2.2.

Warnings:
 * Linux transparent hugepages are set to "always". Check /sys/kernel/mm/transparent_hugepage/enabled
 * Delay accounting is not enabled, OSIOWaitMicroseconds will not be gathered. You can enable it using `echo 1 > /proc/sys/kernel/task_delayacct` or by using sysctl.

562021eb5b31 :) select count() from sample_logs_anomaly

SELECT count()
FROM sample_logs_anomaly

Query id: 2972e749-a308-4cf8-9835-6d50f865e1b5

   ┌─count()─┐
1. │     542 │
   └─────────┘

1 row in set. Elapsed: 0.004 sec. 

562021eb5b31 :) 
```

seeing that we have a non 0 number returning verifies that the ML script works as expected. In case you see 0 entries, one of the reasons is that indeed the data set generated do not contain an anomaly value on `response_time`; hence we could wait for a while to let the generator randomly generate some anomalies for us and re-run the `count()` SQL to verify.

### ✅ 4. (optional) looking into the ML script

this section is optional for a couple of reasons:
- for workshop purposes, the script runs a general anomaly detection job which requires further fine-tuning before applying for production. Good for referencing.
- in practice we might want to run other ML jobs instead of anomaly detection, but again for workshop purposes it is essential to provide an example to complete the workshop's flow.

```python
...
# Connect to ClickHouse
client = clickhouse_connect.get_client(
    host='clickhouse',  # or 'localhost'
    port=8123,
    username='demo_user',
    password='P@ssword1',
)

# Query the data (data frame)
query = "SELECT timestamp, response_time FROM default.sample_logs_analytics ORDER BY timestamp DESC LIMIT 5000"
data = client.query_df(query)
...
```

this section creates a ClickHouse client / connection, via the connection, we would run a select SQL to retrieve the last 5000 entries from `sample_logs_analytics`.

```python
...
# Prepare data
X = np.array(data['response_time']).reshape(-1, 1)

# Train K-Means clustering (2 clusters: normal and anomalies)
kmeans = KMeans(n_clusters=2, random_state=42)
data['cluster'] = kmeans.fit_predict(X)

# Identify the anomaly cluster
anomaly_cluster = data.groupby("cluster")["response_time"].mean().idxmax()
data["is_anomaly"] = data["cluster"] == anomaly_cluster
...
```

we employ numpy to structure / re-shape the data and runs KMeans function on it. The entries would be categorized into 2 groups with 1 group representing anomalies.

```python
...
for _, row in data[data["is_anomaly"]].iterrows():
    print(f"Anomaly detected at {row['timestamp']} with response time {row['response_time']} ms -> {row}")
    # store these into a new table... integrate with grafana for example
    client.command(f"insert into default.sample_logs_anomaly (timestamp, response_time) values (toDateTime64('{row['timestamp']}', 3), {row['response_time']} )")
...
```

once we sorted out which row(s) belong to anomaly, we can selectively insert the row into ClickHouse. The SQL is a general INSERT, we only take the `timestamp` and `response_time` into consideration.

if all goes well, the table `sample_logs_anomaly` would be populated accordingly.

## suggestions / improvements for the ML script

- instead of querying the last 5000 entries, it might make more sense to provide a timestamp range; we typically would be running the anomaly detection based on a regular interval like every hour.
- fine tune the KMeans function to produce analysis more relevant to the business use case.

<div style="text-align:center; margin-top: 20px; font-size: 20px;">

[home](../README.md)

</div>



