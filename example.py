import interactivespaces

master = interactivespaces.Master('127.0.0.1', '1236')

liveactivities = master.get_live_activities()
for liveactivity in liveactivities:
    print liveactivity.get_status()