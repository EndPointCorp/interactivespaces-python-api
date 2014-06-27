import interactivespaces

master = interactivespaces.Master('127.0.0.1', '1234')


print "\n =Space controllers=\n"    
space_controllers = master.get_space_controllers({"space_controller_uuid" : "1a98af7b-58a8-4747-948a-3e3706ef2158"})
for controller in space_controllers:
    controller.fetch()
    #print controller.id(), controller.name(), controller.description(), controller.mode()
    print controller.to_json()



print "\n =Live activity groups=\n"
liveactivitygroups = master.get_live_activity_groups({"live_activity_group_name" : "1234"})
for liveactivitygroup in liveactivitygroups:
    liveactivitygroup.fetch()
    #print liveactivitygroup.name(), liveactivitygroup.id(), liveactivitygroup.description(), liveactivitygroup.live_activities()
    print liveactivitygroup.to_json()



print "\n =Activities= \n"
activities = master.get_activities({"activity_name" : "End Point Presentation Director Bridge"})
for activity in activities:
    activity.fetch()
    #print activity.name(), activity.identifying_name(), activity.version(), activity.id(), activity.description()
    print activity.to_json()

print "\n =Live activities=\n"    

liveactivities = master.get_live_activities({"live_activity_name" : "^GE$"})

for liveactivity in liveactivities:
    liveactivity.fetch()
    #print liveactivity.name(), liveactivity.status(), liveactivity.version(), liveactivity.id()
    print liveactivity.to_json()

print "\n =Spaces=\n"
spaces = master.get_spaces({"space_name" : "^Liquid$"})
for space in spaces:
    space.fetch()
    #print space.name(), space.id(), space.description()
    print space.to_json()

   
print "New live Activity"
master.new_live_activity({
                         "live_activity_name" : "example.py live activity", 
                         "activity_name" : "End Point Presentation Director Bridge", 
                         "space_controller_name" : "ISCtlDispAScreen00",
                         "live_activity_description" : "created with example.py"
                         }
                        )
