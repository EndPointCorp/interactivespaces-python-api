interactivespaces-python-api
============================

[Interactive Spaces](https://github.com/interactivespaces/interactivespaces) API client


```python

import interactivespaces
master = interactivespaces.Master('ispaces.master.com', '8080')

live_activity = master.get_live_activity({
                                         "live_activity_name" : "GEViewSync Slave 01 on Node A",
                                         "space_controller_name" : "ISCtlDispAScreen00"
                                         })
print live_activity.to_json()
print "Setting metadata of live activity"
live_activity.set_metadata({
                          "some_key" : "some_value",
                          "another_key" :"another_value"})
live_activity.fetch()
print live_activity.to_json()

print "Lets refresh live activity"
live_activity.send_status_refresh()

live_activity.fetch()
print live_activity.to_json()

print "Lets delete live activity"
live_activity.send_delete()

```
