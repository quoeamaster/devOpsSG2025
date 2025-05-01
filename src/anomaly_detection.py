import clickhouse_connect
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
# import matplotlib.pyplot as plt

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
# print(f"{data}")

# Prepare data
X = np.array(data['response_time']).reshape(-1, 1)

# Train K-Means clustering (2 clusters: normal and anomalies)
kmeans = KMeans(n_clusters=2, random_state=42)
data['cluster'] = kmeans.fit_predict(X)

# Identify the anomaly cluster
anomaly_cluster = data.groupby("cluster")["response_time"].mean().idxmax()
data["is_anomaly"] = data["cluster"] == anomaly_cluster

# Visualize anomalies (works in localhost and not inside the docker container)
# plt.scatter(data.index, data['response_time'], c=data['is_anomaly'], cmap='coolwarm')
# plt.xlabel("Log Entry")
# plt.ylabel("Response Time (ms)")
# plt.title("Anomaly Detection in API Logs")
# plt.show()

for _, row in data[data["is_anomaly"]].iterrows():
    print(f"Anomaly detected at {row['timestamp']} with response time {row['response_time']} ms -> {row}")
    # store these into a new table... integrate with grafana for example
    client.command(f"insert into default.sample_logs_anomaly (timestamp, response_time) values (toDateTime64('{row['timestamp']}', 3), {row['response_time']} )")


# sample output
# ...
# Anomaly detected at 2025-04-25 05:41:29 with response time 3698 ms -> 
# timestamp        2025-04-25 05:41:29
# response_time                   3698
# cluster                            1
# is_anomaly                      True
# Name: 2, dtype: object