# TODO

* make support for restarting one controller

* add configuration parameter for "autodeploy" and "autoconfigure"
* user filters
* use metadata to relaunch
* Test the rest of the new_ methods in Master
* Test get_ methods with lambda patterns in Master
* Separate .fetch(), _get_absoslute_url() and part of .new() methods from API classes to Communicable to make everything more DRY
* when more than one object is returned for singular methods like .get_space_controller or .get_live_activity, a proper exception should be thrown
* make master.get_live_activity_group() accept "live_activities" list as a param and parse it. Currently it's being ignored.
* refactor connect_all_controllers()
* manage sys.path in the appropriate way without hardcoded paths and .append()
* make config file steer the debug level for the @debug decorator
