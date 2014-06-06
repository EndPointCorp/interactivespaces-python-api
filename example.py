import interactivespaces

master = interactivespaces.Master('127.0.0.1', '1237')

liveactivities = master.get_live_activities()
activities = master.get_activities()

print "\n =Activities= \n"

for activity in activities:
    activity.refresh()
    print activity.name(), activity.identifying_name(), activity.version(), activity.activity_id()

print "\n =Live activities=\n"

for liveactivity in liveactivities:
    activity.refresh()
    print liveactivity.name(), liveactivity.status(), liveactivity.version(), liveactivity.live_activity_id()
