# Round Robin Database
## Note
I have started writing with the command name (and general abbreviation) RRDB, and that is what I will call it! Because... idk.
## Prompt
Requirements for a Round Robin Database tool (RRD)
- An RRD is a circular structure (list) with a fixed number of slots to store data.
- It is filled in order, and once you reach the end of the list, the first element gets overwritten. This
ensures the size of the database does not grow over time while keeping the most recent data available.
- The RRD will store a timestamp (epoch) and a value (float).
- The goal is to build a command line executable to (1) save and (2) query the data.
- Save command:
    - The value will be saved in two round robin structures in a simple database (e.g. SQLite)
    - The first RRD will keep the values for the last hour (i.e. each slot will represent a minute
within the last 60 minutes)
    - The second keeps values per hour, for the last 24 hours. To determine the value per
hour to save, please choose the minimum from the list of values per minute:
i.e. `valueOnHour1 = min(valueOnMinute0, valueOnMinute1, valueOnMinute2, ..., valueOnMinute59)`
    - Assume `NULL` for slots with no information.
    - `rrd save {epoch_timestamp} {float_to_save}`
    - E.g. `rrd save 1674476760 33.1`
- Query command: retrieves the data from the RRD
    - Display the data stored in the minutes or hours RRD files, and output the average, maximum
and minimum values.
    - `rrd query minutes`. Example output:

```
1345018980, 132.1
1345019040, 322.1
1345019160, NULL
...
1345022580, 53.3
minutes: min: 53.3, avg: 403.3, max: 512.11
```
-
    - `rrd query hours`. Example output:

```
1345021200, 132.1
1345024800, 122.1
...
1345028400, 453.3
hours: min: 53.3, avg: 403.3, max: 512.11
```