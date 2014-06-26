import interactivespaces

master = interactivespaces.Master('127.0.0.1', '1234')

liveactivities = master.get_live_activities()
activities = master.get_activities()
liveactivitygroups = master.get_live_activity_groups()
spaces = master.get_spaces()
space_controllers = master.get_space_controllers()


print "\n =Space controllers=\n"    

for controller in space_controllers:
    controller.fetch()
    print controller.id(), controller.name(), controller.description(), controller.mode()
    print controller.to_json()

print "\n = Spaces =\n"

for space in spaces:
    space.fetch()
    print space.name(), space.id(), space.description()
    print space.to_json()
 


print "\n =Live activity groups=\n"

for liveactivitygroup in liveactivitygroups:
    liveactivitygroup.fetch()
    print liveactivitygroup.name(), liveactivitygroup.id(), liveactivitygroup.description(), liveactivitygroup.live_activities()
    print liveactivitygroup.to_json()


print "\n =Activities= \n"

for activity in activities:
    activity.fetch()
    print activity.data_hash
    print activity.name(), activity.identifying_name(), activity.version(), activity.id(), activity.description()
    print activity.to_json()


print "\n =Live activities=\n"    

for liveactivity in liveactivities:
    liveactivity.fetch()
    print liveactivity.name(), liveactivity.status(), liveactivity.version(), liveactivity.id()
    print liveactivity.to_json()


