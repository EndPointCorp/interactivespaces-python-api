import interactivespaces

master = interactivespaces.Master('127.0.0.1', '8080')

""" Listing """
def list_space_controllers():
    print "\n =Space controllers=\n"    
    space_controllers = master.get_space_controllers({"space_controller_uuid" : "1a98af7b-58a8-4747-948a-3e3706ef2158"})
    for controller in space_controllers:
        controller.fetch()
        #print controller.id(), controller.name(), controller.description(), controller.mode()
        print controller.to_json()

def list_live_activity_groups():
    print "\n =Live activity groups=\n"
    liveactivitygroups = master.get_live_activity_groups({"live_activity_group_name" : "1234"})
    for liveactivitygroup in liveactivitygroups:
        liveactivitygroup.fetch()
        #print liveactivitygroup.name(), liveactivitygroup.id(), liveactivitygroup.description(), liveactivitygroup.live_activities()
        print liveactivitygroup.to_json()

def list_activities():
    print "\n =Activities= \n"
    activities = master.get_activities({"activity_name" : "End Point Presentation Director Bridge"})
    for activity in activities:
        activity.fetch()
        #print activity.name(), activity.identifying_name(), activity.version(), activity.id(), activity.description()
        print activity.to_json()

def list_live_activities():
    print "\n =Live activities=\n"
    liveactivities = master.get_live_activities({"live_activity_name" : "^GE"})
    for liveactivity in liveactivities:
        liveactivity.fetch()
        #print liveactivity.name(), liveactivity.status(), liveactivity.version(), liveactivity.id()
        print liveactivity.to_json()

def list_spaces():
    print "\n =Spaces=\n"
    spaces = master.get_spaces({"space_name" : ""})
    for space in spaces:
        space.fetch()
        #print space.name(), space.id(), space.description()
        print space.to_json()

""" Creating """
def create_new_live_activity():
    print "New live Activity"
    new_live_activity = master.new_live_activity({
                             "live_activity_name" : "example.py live activity omgomg", 
                             "activity_name" : "End Point Presentation Director Bridge", 
                             "space_controller_name" : "ISCtlDispAScreen00",
                             "live_activity_description" : "created with example.py"
                             }
                            )

    print "Json of the freshly created live_activity %s" % new_live_activity.to_json()

def create_new_activity():
    print "New activity"
    with open("/Users/wojtek/Sources/lg-ispaces-activities/com.endpoint.lg.director.bridge/build/com.endpoint.lg.director.bridge-1.0.0.zip", "r") as zipfile:
        new_activity = master.new_activity({'zip_file_handler' : zipfile})
        print "Json of the freshly created activity %s" % new_activity.to_json()

def create_new_controller():
    print "New Controller"
    new_controller = master.new_space_controller({"space_controller_name" : "Testing space controller", 
                                                  "space_controller_description" : "Created by example.py", 
                                                  "space_controller_host_id" : "testingctl" })
    print new_controller.to_json()
    
def create_new_live_activity_group():
    print "New Live Activity Group"
    new_live_activity_group = master.new_live_activity_group({"live_activity_group_name" : "example.py live_activity_group_name",
                                                              "live_activity_group_description" : "created by example.py",
                                                              "live_activities" : [{"live_activity_name" : "SV Master on Node A",
                                                                                    "space_controller_name" : "ISCtlDispAScreen00"},
                                                                                   {"live_activity_name" : "SV Slave 01 on Node A",
                                                                                    "space_controller_name" : "ISCtlDispAScreen00"}
                                                                                   ]})
    print new_live_activity_group.to_json()

""" Status refresh """
def send_status_refresh_to_a_live_activity():
    print "\n =Live Activity= \n"
    activity = master.get_live_activity({
                                         "live_activity_name" : "GE ViewSync Slave 01 on Node A",
                                         "space_controller_name" : "ISCtlDispAScreen00"
                                         })
    activity.to_json()
    print "Sending status refresh to live activity"
    activity.send_status_refresh()

def send_status_refresh_to_a_live_activity_group():
    print "\n =Live Activity Group= \n"
    live_activity_group = master.get_live_activity_group({"live_activity_group_name" : "GE and Supporting"})
    live_activity_group.to_json()
    print "Sending status refresh to live activity group"
    live_activity_group.send_status_refresh()

def send_status_refresh_to_a_space():
    print "\n =Space \n"
    space = master.get_space({"space_name" : "ok"})
    space.to_json()
    print "Sending status refresh to space"
    space.send_status_refresh()

def send_status_refresh_to_a_controller():
    print "\n = Controller \n"
    controller = master.get_space_controller({"space_controller_name" : "ISCtlDispBScreen00"})
    print controller.to_json()
    print "Sending status refresh to controller"
    controller.send_status_refresh()
  
""" Deleting """
def delete_live_activity():
    print "\n =Live Activity= \n"
    live_activity = master.get_live_activity({
                                         "live_activity_name" : "LOLOLO",
                                         "space_controller_name" : "ISCtlDispAScreen00"
                                         })
    print live_activity.to_json()
    print "Sending delete to live activity"
    live_activity.send_delete()
    
def delete_live_activity_group():
    print "\n =Live Activity Group= \n"
    live_activity_group = master.get_live_activity_group({"live_activity_group_name": "^SV and Supporting$"})
    print live_activity_group.to_json()
    print "Sending delete to live activity group"
    live_activity_group.send_delete()

def delete_space():
    print "\n =Live Activity Group= \n"
    space = master.get_space({"space_name" : "ok"})
    print space.to_json()
    print "Sending delete to space"
    space.send_delete()
    
def delete_controller():
    print "\n =Controller= \n"
    controller = master.get_space_controller({"space_controller_uuid" : "af733f63-d2f9-466f-98ba-826072605ab4"})
    print controller.to_json()
    print "Sending delete to controller"
    controller.send_delete()

""" Shutting down """
def shutdown_live_activity():
    print "\n =Live Activity= \n"
    activity = master.get_live_activity({
                                         "live_activity_name" : "GE ViewSync Slave 01 on Node A",
                                         "space_controller_name" : "ISCtlDispAScreen00"
                                         })
    activity.to_json()
    print "Sending shutdown to live activity"
    activity.send_shutdown()
    
def shutdown_live_activity_group():
    print "\n =Live Activity Group= \n"
    live_activity_group = master.get_live_activity_group({"live_activity_group_name" : "^GE and Supporting$"})
    live_activity_group.to_json()
    print "Sending shutdown to live activity group"
    live_activity_group.send_shutdown()

""" Starting up """

def startup_live_activity():
    print "\n =Live Activity= \n"
    activity = master.get_live_activity({
                                         "live_activity_name" : "GE ViewSync Slave 01 on Node A",
                                         "space_controller_name" : "ISCtlDispAScreen00"
                                         })
    activity.to_json()
    print "Sending startup to live activity"
    activity.send_startup()
    
def startup_live_activity_group():
    print "\n =Live Activity Group= \n"
    live_activity_group = master.get_live_activity_group({"live_activity_group_name" : "^GE and Supporting$"})
    live_activity_group.to_json()
    print "Sending startup to live activity group"
    live_activity_group.send_startup()


""" Activating """

def activate_live_activity():
    print "\n =Live Activity= \n"
    activity = master.get_live_activity({
                                         "live_activity_name" : "GE ViewSync Slave 01 on Node A",
                                         "space_controller_name" : "ISCtlDispAScreen00"
                                         })
    activity.to_json()
    print "Sending activate to live activity"
    activity.send_activate()

def activate_live_activity_group():
    print "\n =Live Activity Group= \n"
    live_activity_group = master.get_live_activity_group({"live_activity_group_name" : "^GE and Supporting$"})
    live_activity_group.to_json()
    print "Sending acticate to live activity group"
    live_activity_group.send_activate()

""" Deactivating """

def deactivate_live_activity():
    print "\n =Live Activity= \n"
    activity = master.get_live_activity({
                                         "live_activity_name" : "GE ViewSync Slave 01 on Node A",
                                         "space_controller_name" : "ISCtlDispAScreen00"
                                         })
    activity.to_json()
    print "Sending activate to live activity"
    activity.send_deactivate()

def deactivate_live_activity_group():
    print "\n =Live Activity Group= \n"
    live_activity_group = master.get_live_activity_group({"live_activity_group_name" : "^GE and Supporting$"})
    live_activity_group.to_json()
    print "Sending acticate to live activity group"
    live_activity_group.send_deactivate()

    
""" Deploying """

def deploy_live_activity():
    print "\n =Live Activity= \n"
    activity = master.get_live_activity({
                                         "live_activity_name" : "GE ViewSync Slave 01 on Node A",
                                         "space_controller_name" : "ISCtlDispAScreen00"
                                         })
    activity.to_json()
    print "Sending deploy to live activity"
    activity.send_deploy()

def deploy_live_activity_group():
    print "\n =Live Activity Group= \n"
    live_activity_group = master.get_live_activity_group({"live_activity_group_name" : "^GE and Supporting$"})
    print live_activity_group.to_json()
    print "Sending deploy to live activity group"
    live_activity_group.send_deploy()
    
""" Configuring """

def configure_live_activity():
    print "\n =Live Activity= \n"
    activity = master.get_live_activity({
                                         "live_activity_name" : "GE ViewSync Slave 01 on Node A",
                                         "space_controller_name" : "ISCtlDispAScreen00"
                                         })
    print activity.to_json()
    print "Sending configure to live activity"
    activity.send_configure()

def configure_live_activity_group():
    print "\n =Live Activity Group= \n"
    live_activity_group = master.get_live_activity_group({"live_activity_group_name" : "^GE and Supporting$"})
    print live_activity_group.to_json()
    print "Sending configure to live activity group"
    live_activity_group.send_configure()

""" Cleaning """

def clean_tmp_live_activity():
    print "\n =Live Activity= \n"
    activity = master.get_live_activity({
                                         "live_activity_name" : "GE ViewSync Slave 01 on Node A",
                                         "space_controller_name" : "ISCtlDispAScreen00"
                                         })
    print activity.to_json()
    print "Sending clean_tmp to live activity"
    activity.send_clean_tmp()

def clean_permanent_live_activity():
    print "\n =Live Activity= \n"
    activity = master.get_live_activity({
                                         "live_activity_name" : "GE ViewSync Slave 01 on Node A",
                                         "space_controller_name" : "ISCtlDispAScreen00"
                                         })
    print activity.to_json()
    print "Sending clean_permanent to live activity"
    activity.send_clean_permanent()

""" Connecting """

def send_connect_to_a_controller():
    print "\n = Controller \n"
    controller = master.get_space_controller({"space_controller_name" : "ISCtlDispBScreen00"})
    print controller.to_json()
    print "Sending connect to controller"
    controller.send_connect()

def send_disconnect_to_a_controller():
    print "\n = Controller \n"
    controller = master.get_space_controller({"space_controller_name" : "ISCtlDispBScreen00"})
    print controller.to_json()
    print "Sending disconnect to controller"
    controller.send_disconnect()


""" Updating metadata """

def update_metadata_of_live_activity():
    print "\n =Live Activity= \n"
    activity = master.get_live_activity({
                                         "live_activity_name" : "GE ViewSync Slave 01 on Node A",
                                         "space_controller_name" : "ISCtlDispAScreen00"
                                         })
    print activity.to_json()
    print "Setting metadata of live activity"
    activity.set_metadata({"some_key" : "some_value", "another_key" : "another_value"})
    activity.fetch()
    print activity.to_json()
    
def update_metadata_of_live_activity_group():
    print "\n =Live Activity Group= \n"
    live_activity_group = master.get_live_activity_group({"live_activity_group_name" : "^GE and Supporting$"})
    print live_activity_group.to_json()
    print "Setting metadata of  live activity group"
    live_activity_group.set_metadata({"some_key" : "some_value", "another_key" : "another_value"})

def update_metadata_of_space():
    print "\n =Space \n"
    space = master.get_space({"space_name" : "ok"})
    print space.to_json()
    print "Setting metadata of space"
    space.set_metadata({"some_key" : "some_value", "another_key" : "another_value"})

