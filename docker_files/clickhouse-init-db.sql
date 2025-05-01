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


create user if not exists demo_user IDENTIFIED BY 'P@ssword1';
grant select, insert, update, delete on default.sample_logs to demo_user;
grant select, insert, update, delete on default.sample_logs_analytics to demo_user;
grant select, insert, update, delete on default.sample_logs_anomaly to demo_user;

