# ⚙️ 02. Docker: ClickHouse

In this section, we'll set up the Docker configuration required to run the ClickHouse locally. By the end, you'll have:
- ClickHouse Docker container running
- Docker and Docker Compose for running ClickHouse
- SQL file with table schema and user definition required for the labs

---

## 📦 Prerequisites

### ✅ 1. Docker configuration for ClickHouse (docker-compose.yml)

```yaml
services:
  clickhouse:
    image: clickhouse/clickhouse-server:25.2
    container_name: clickhouse
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - clickhouse-data:/var/lib/clickhouse
    healthcheck:
      test: wget --no-verbose --spider http://localhost:8123/ping || exit 1
      interval: 3s
      retries: 5

volumes:
  clickhouse-data:
```

To make sure the lab instruction works accordingly, we will be using a specific version of every Docker image involved. For ClickHouse we are picking version `25.2`. 

A specific container name is applied for debug and interactive purposes, `clickhouse` is picked. 

Like any software deployed, we would need to expose minimal ports for interaction purposes; here we will be exposing:
- 8123 (http default port) and 
- 9000 (Native Protocol port OR aka TCP port)

Technically the workshop only required port 8123 to be accessible but in case we are using the `clickhouse CLI` to interact with the Docker container, port 9000 would be required. More on ports available at [here](https://clickhouse.com/docs/guides/sre/network-ports). 

We would create a `volume` to store the data persisted or else all data involved in the session would be inaccessible once the container(s) is stopped. To examine the volume, run the following:
```bash
docker volume ls

# sample output

DRIVER    VOLUME NAME
...
local     docker_files_clickhouse-data
```

The `healthcheck` section helps to verify if the ClickHouse container is running correctly before moving on. As later on we would see other containers are created ONLY when the ClickHouse container is running, we named it `container dependencies`. The health-test is straightforward to ping the `http://localhost:8123/ping` api endpoint in which it would return `OK` when up running.

### ✅ 2. prepare the clickhouse-init-db.sql file

For some Docker images, they provide a way to run initialization tasks to setup the software. Such capability helps to reduce the complexity for setup as you would not need to add bulky and messy docker `command` section. 

For ClickHouse, we can create a special file named `clickhouse-init-db.sql`, in which the software would run for the very first time we created the corresponding container (it checks if a docker volume was available before deciding to run the provided sql file contents). 

---

For our workshop, our sql file would need to create the target table schema:
```sql
create table sample_logs
(
   timestamp DateTime64(3),
   message String
) engine=MergeTree()
order by tuple()
;

create table sample_logs_analytics
(
   timestamp DateTime64(3),
   service String,
   response_time UInt16,
   level String,
   actual_message String
) engine=MergeTree()
order by (service)
;

create materialized view sample_logs_analytics_mv to sample_logs_analytics
as 
select 
    extractAllGroups(message, '(\\[(\w+)]\\[(.*?)\]\\s+([\\w-]+)\\s+:\\s+(.*?)\\s+-\\s+(\\d+))') as result,
    result[1][2] as level,
    toDateTime64(result[1][3], 6) as timestamp,
    result[1][4] as service,
    result[1][5] as actual_message,
    result[1][6] as response_time
from sample_logs
;

create table default.sample_logs_anomaly 
(
   timestamp DateTime64(3),
   response_time UInt16
) engine = MergeTree()
order by tuple()
;
```
Let's take a look on what is happening here, 3 tables and 1 Materialized View are created:
- sample_logs (table) - storing the raw data logs
- sample_logs_analytics (table) - storing the parsed data obtained through sample_logs
- sample_logs_anomaly (table) - storing anomaly entries after processed by a Machine-Learning job
- sample_logs_analytics_mv (materialized view) - the transformation engine to parse sample_logs data and store the results to sample_logs_analytics

For the table DDL, they are pretty straightforward, the only new thing here is the Materialized View (aka MV). Typically MV does the transformation on source data to a desired state; for our workshop the source data contains a column named `message` which has a pattern:
```bash
[{level}][{timestamp}] {service} : {message} - {response_time}
```
the transformation logic involved is simply how to break down this raw string into various values stored in the corresponding table columns. We would be utilizing the function `extractAllGroups` in which a regexp is provided and ClickHouse tries its very best to parse the raw string into an array containing the various values parsed. More information about extractAllGroups is at [here](https://clickhouse.com/docs/sql-reference/functions/splitting-merging-functions#extractallgroups)

One important thing about MV is that it is an input trigger; meaning that only inserts on the source table (sample_logs table) would trigger the MV to process and create a corresponding row in the target table (sample_logs_analytics table). For our workshop an insert trigger is far enough. However for certain use cases, it would be nice to handle data updates as well; ClickHouse provides a `Refreshable Materialized View` to cover such use case and more information available at [here](https://clickhouse.com/docs/materialized-view/refreshable-materialized-view)

---

Next is to create a user and grant this user the minimal access rights to access the above tables
```sql
create user if not exists demo_user IDENTIFIED BY 'P@ssword1';
grant select, insert, update, delete on default.sample_logs to demo_user;
grant select, insert, update, delete on default.sample_logs_analytics to demo_user;
grant select, insert, update, delete on default.sample_logs_anomaly to demo_user;
```
Like most database systems, there is a admin / root user that can access anything. This is a security issue in general and hence it is suggested to create a dedicated user with just enough access rights to work on our applications. In our workshop, we would create a user named `demo_user` with a plain-text password (not recommended for production) and would be granted access to the 3 tables above. Technically we just need to grant 
- select and
- insert 

but as a workshop purpose, we simplify the setup by granting all CRUD rights once and for all. In production, we should examine what were the minimal access required instead.

Finally update the `volume` section of docker-compose.yml
```yaml
...
    volumes:
      - clickhouse-data:/var/lib/clickhouse
      - ./clickhouse-init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
...      
```

### ✅ 3. running the container via docker-compose

To test our Docker configurations, run the following:
```bash
docker compose up clickhouse -d

# or the legacy way
docker-compose up clickhouse -d

# verify 
docker ps -a

# sample output
CONTAINER ID   IMAGE                               COMMAND            CREATED         STATUS                   PORTS                                                      NAMES
d644815fa252   clickhouse/clickhouse-server:25.2   "/entrypoint.sh"   3 seconds ago   Up 3 seconds (healthy)   0.0.0.0:8123->8123/tcp, 0.0.0.0:9000->9000/tcp, 9009/tcp   clickhouse
```

the sample output is quite verbose, but we just need to focus on the `STATUS` column, if we see `Up xxx seconds (healthy)` that indicates our container is running healthily.

<div style="text-align:center; margin-top: 20px; font-size: 20px;">

🔧 [prev - prerequisites](01-setup.md) &nbsp;&nbsp;&nbsp; 🔍 [next - data generator](03-data-generator.md)

</div>

