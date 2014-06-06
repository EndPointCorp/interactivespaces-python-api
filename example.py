import interactivespaces

master = interactivespaces.Master('127.0.0.1', '1236')

liveactivities = master.get_live_activities()
activities = master.get_activities()

print "=Activities= \n"

for activity in activities:
    print activity.name()

print "=Live activities=\n"

for liveactivity in liveactivities:
    print liveactivity.status(), liveactivity.name()
