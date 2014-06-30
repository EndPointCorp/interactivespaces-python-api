import interactivespaces

master = interactivespaces.Master('127.0.0.1', '1234')

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
        
def get_one_live_activity_and_refresh_status():
    print "\n =Live Activity= \n"
    activity = master.get_live_activity({
                                         "live_activity_name" : "GE ViewSync Slave 01 on Node A",
                                         "space_controller_name" : "ISCtlDispAScreen00"
                                         })
    activity.to_json()
    print "Sending status refresh to live activity"
    activity.send_status_refresh_command()

def get_one_space_controller_and_refresh_status():
    print "\n =Space Controller + refresh status= \n"
    space_controller = master.get_space_controller({
                                         "space_controller_name" : "ISCtlDispBScreen00"
                                         })
    space_controller.to_json()
    print "Sending status refresh space controller"
    space_controller.send_status_refresh_command()
        
def list_live_activities():
    print "\n =Live activities=\n"        
    liveactivities = master.get_live_activities({"live_activity_name" : "^GE"})
    for liveactivity in liveactivities:
        liveactivity.fetch()
        #print liveactivity.name(), liveactivity.status(), liveactivity.version(), liveactivity.id()
        print liveactivity.to_json()

def list_spaces():
    print "\n =Spaces=\n"
    spaces = master.get_spaces({"space_name" : "^Liquid$"})
    for space in spaces:
        space.fetch()
        #print space.name(), space.id(), space.description()
        print space.to_json()

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

list_live_activities()
get_one_space_controller_and_refresh_status()
