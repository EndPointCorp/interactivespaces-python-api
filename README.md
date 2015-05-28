[![travis](https://api.travis-ci.org/EndPointCorp/interactivespaces-python-api.svg)](https://travis-ci.org/EndPointCorp/interactivespaces-python-api)
interactivespaces-python-api
============================

[Interactive Spaces](https://github.com/interactivespaces/interactivespaces) API client

Built to manage interactivespaces environment.

Some examples:

```python

import interactivespaces

# initialize Master() object that acts as a proxy
master = interactivespaces.Master('ispaces.master.com', '8080')

# return LiveActivity object by getting it
live_activity = master.get_live_activity({
                                         "live_activity_name" : "GEViewSync Slave 01 on Node A",
                                         "space_controller_name" : "ISCtlDispAScreen00"
                                         })

# represent the object as json
print live_activity.to_json()

# change metadata of the remote object
print "Setting metadata of live activity"
live_activity.set_metadata({
                          "some_key" : "some_value",
                          "another_key" :"another_value"})

# refresh remote object
live_activity.fetch()

# represent it as json
print live_activity.to_json()

# force status refresh of the live activity on the controller
print "Lets refresh live activity"
live_activity.send_status_refresh()

# fetch the change
live_activity.fetch()

# print it again
print live_activity.to_json()

# delete the live activity
print "Lets delete live activity"
live_activity.send_delete()

```
