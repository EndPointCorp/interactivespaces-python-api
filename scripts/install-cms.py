import interactivespaces
import re
import string

master = interactivespaces.Master('127.0.0.1', '8081', '8091')

def remove_activities():
    activities = master.get_activities({"activity_name" : ""})
    for activity in activities:
        activity.fetch()
        print "Removing activity \"%s\" (%s)" % (activity.name(), activity.id())
        activity.send_delete()

def remove_live_activities():
    liveactivities = master.get_live_activities({"live_activity_name" : ""})
    for liveactivity in liveactivities:
        liveactivity.fetch()
        print "Removing live activity \"%s\"" % liveactivity.name()
        liveactivity.send_delete()

def remove_live_activity_groups():
    liveactivitygroups = master.get_live_activity_groups({"live_activity_group_name":""})
    for liveactivitygroup in liveactivitygroups:
        print "Removing live activity group \"%s\"" % liveactivitygroup.name()
        liveactivitygroup.send_delete()

def create_new_activity(filename):
    with open(filename, "r") as zipfile:
        new_activity = master.new_activity({'zip_file_handler' : zipfile})

def create_new_live_activity(name, activity_name, controller_name, description):
    new_live_activity = master.new_live_activity({
                             "live_activity_name" : name,
                             "activity_name" : activity_name,
                             "space_controller_name" : controller_name,
                             "live_activity_description" : description
                             }
                            )
    return new_live_activity

def create_new_live_activity_group(group_name, description, live_activities):
    return master.new_live_activity_group({"live_activity_group_name" : group_name,
                                            "live_activity_group_description" : "group_description",
                                            "live_activities" : live_activities })

controller_config = {
    'Head node controller' : {
        'NOTHING SPECIAL' : 'GOES HERE'
    },
    '42-a controller' : {
        'VIEWPORT' : 'left_three',
        'GUI_HIDDEN' : 'true',
        'VIEWSYNC' : '-style GTK+ -sConnection/disableRequestBatching=true -sViewSync/receive=true -sViewSync/hostname=10.42.4 controller2.255 -sViewSync/port=45678 -sViewSync/yawOffset=-36 -sViewSync/pitchOffset=0 -sViewSync/rollOffset=0 -sViewSync/horizFov=29 -multiple',
        'SPACENAV' : 'false',
        'SPACENAV_1' : '',
        'SPACENAV_2' : '',
        'SPACENAV_3' : '',
        'SPACENAV_4' : '',
        'SPACENAV_5' : '',
        'SPACENAV_6' : '',
        'SPACENAV_7' : ''
    },
    '42-b controller' : {
        'VIEWPORT' : 'left_two',
        'GUI_HIDDEN' : 'true',
        'VIEWSYNC' : '-style GTK+ -sConnection/disableRequestBatching=true -sViewSync/receive=true -sViewSync/hostname=10.42.42.255 -sViewSync/port=45678 -sViewSync/yawOffset=-36 -sViewSync/pitchOffset=0 -sViewSync/rollOffset=0 -sViewSync/horizFov=29 -multiple',
        'SPACENAV' : 'false',
        'SPACENAV_1' : '',
        'SPACENAV_2' : '',
        'SPACENAV_3' : '',
        'SPACENAV_4' : '',
        'SPACENAV_5' : '',
        'SPACENAV_6' : '',
        'SPACENAV_7' : ''
    },
    '42-c controller' : {
        'VIEWPORT' : 'left_one',
        'GUI_HIDDEN' : 'true',
        'VIEWSYNC' : '-style GTK+ -sConnection/disableRequestBatching=true -sViewSync/receive=true -sViewSync/hostname=10.42.42.255 -sViewSync/port=45678 -sViewSync/yawOffset=-36 -sViewSync/pitchOffset=0 -sViewSync/rollOffset=0 -sViewSync/horizFov=29 -multiple',
        'SPACENAV' : 'false',
        'SPACENAV_1' : '',
        'SPACENAV_2' : '',
        'SPACENAV_3' : '',
        'SPACENAV_4' : '',
        'SPACENAV_5' : '',
        'SPACENAV_6' : '',
        'SPACENAV_7' : ''
    },
    '42-d controller' : {
        'VIEWPORT' : 'center',
        'GUI_HIDDEN' : 'true',
        'VIEWSYNC' : '-style GTK+ -sConnection/disableRequestBatching=true -sViewSync/receive=true -sViewSync/hostname=10.42.42.255 -sViewSync/port=45678 -sViewSync/yawOffset=-36 -sViewSync/pitchOffset=0 -sViewSync/rollOffset=0 -sViewSync/horizFov=29 -multiple',
        'SPACENAV' : 'false',
        'SPACENAV_1' : '',
        'SPACENAV_2' : '',
        'SPACENAV_3' : '',
        'SPACENAV_4' : '',
        'SPACENAV_5' : '',
        'SPACENAV_6' : '',
        'SPACENAV_7' : ''
    },
    '42-e controller' : {
        'VIEWPORT' : 'touchscreen',
        'GUI_HIDDEN' : 'true',
        'SPACENAV' : 'true',
        'SPACENAV_1' : '-sSpaceNavigator/device=/dev/input/spacenavigator',
        'SPACENAV_2' : '-sSpaceNavigator/gutterValue=0.1 -sSpaceNavigator/sensitivityPitch=.010',
        'SPACENAV_3' : '-sSpaceNavigator/sensitivityRoll=.0010 -sSpaceNavigator/sensitivityYaw=.00350',
        'SPACENAV_4' : '-sSpaceNavigator/sensitivityX=.250 -sSpaceNavigator/sensitivityY=.250',
        'SPACENAV_5' : '-sSpaceNavigator/sensitivityZ=.020 -sSpaceNavigator/zeroPitch=0.0',
        'SPACENAV_6' : '-sSpaceNavigator/zeroRoll=0.0 -sSpaceNavigator/zeroYaw=0.0',
        'SPACENAV_7' : '-sSpaceNavigator/zeroX=0.0 -sSpaceNavigator/zeroY=0.0 -sSpaceNavigator/zeroZ=0.0',
        'VIEWSYNC' : '-style GTK+ -sConnection/disableRequestBatching=true -sViewSync/send=true -sViewSync/hostname=10.42.42.255 -sViewSync/port=45678 -sViewSync/yawOffset=0 -sViewSync/pitchOffset=0 -sViewSync/rollOffset=0 -sViewSync/horizFov=29',
    },
    '42-f controller' : {
        'VIEWPORT' : 'right_one',
        'GUI_HIDDEN' : 'true',
        'VIEWSYNC' : '-style GTK+ -sConnection/disableRequestBatching=true -sViewSync/receive=true -sViewSync/hostname=10.42.42.255 -sViewSync/port=45678 -sViewSync/yawOffset=-36 -sViewSync/pitchOffset=0 -sViewSync/rollOffset=0 -sViewSync/horizFov=29 -multiple',
        'SPACENAV' : 'false',
        'SPACENAV_1' : '',
        'SPACENAV_2' : '',
        'SPACENAV_3' : '',
        'SPACENAV_4' : '',
        'SPACENAV_5' : '',
        'SPACENAV_6' : '',
        'SPACENAV_7' : ''
    },
    '42-g controller' : {
        'VIEWPORT' : 'right_two',
        'GUI_HIDDEN' : 'true',
        'VIEWSYNC' : '-style GTK+ -sConnection/disableRequestBatching=true -sViewSync/receive=true -sViewSync/hostname=10.42.42.255 -sViewSync/port=45678 -sViewSync/yawOffset=-36 -sViewSync/pitchOffset=0 -sViewSync/rollOffset=0 -sViewSync/horizFov=29 -multiple',
        'SPACENAV' : 'false',
        'SPACENAV_1' : '',
        'SPACENAV_2' : '',
        'SPACENAV_3' : '',
        'SPACENAV_4' : '',
        'SPACENAV_5' : '',
        'SPACENAV_6' : '',
        'SPACENAV_7' : ''
    },
    '42-h controller' : {
        'VIEWPORT' : 'right_three',
        'GUI_HIDDEN' : 'true',
        'VIEWSYNC' : '-style GTK+ -sConnection/disableRequestBatching=true -sViewSync/receive=true -sViewSync/hostname=10.42.42.255 -sViewSync/port=45678 -sViewSync/yawOffset=-36 -sViewSync/pitchOffset=0 -sViewSync/rollOffset=0 -sViewSync/horizFov=29 -multiple',
        'SPACENAV' : 'false',
        'SPACENAV_1' : '',
        'SPACENAV_2' : '',
        'SPACENAV_3' : '',
        'SPACENAV_4' : '',
        'SPACENAV_5' : '',
        'SPACENAV_6' : '',
        'SPACENAV_7' : ''
    },
}

config = {
    'Earth KML Sync' : {
        'name' : 'Google Earth KML NetworkLinkUpdate Service',
        'jar' : 'jars/com.endpoint.lg.earth.kmlsync-1.0.0.dev.zip',
        'config' : 'jars/earth-kmlsync.conf',
        'liveactivities' : [
            { 'name' : 'Earth KML Sync', 'controller' : 'Head node controller' }
        ]
    },
	'Browser service': {
        'name': 'LG Browser Service',
        'jar' : 'jars/com.endpoint.lg.browser.service-0.0.1.zip',
        'config' : 'jars/browser-service.conf',
        'liveactivitygroup' : 'Browser services',
        'liveactivities' : [
            {
                'name' : 'Browser service',
                'each_controller' : {'space_controller_name' : re.compile('42-. controller')},
            }
        ]
    },
    'Earth client' : {
        'name' : 'Google Earth Client',
        'jar' : 'jars/com.endpoint.lg.earth.client-1.0.0.dev.zip',
        'config' : 'jars/earth-client.conf',
        'liveactivitygroup' : 'Earth clients',
        'liveactivities' : [
            { 'name' : 'Earth Client service', 'each_controller' : {'space_controller_name' : re.compile('42')} }
        ]
    },
    'Media service' : {
        'name' : 'Media Service',
        'jar' : 'jars/com.endpoint.lg.media.service-0.0.1.zip',
        'config' : 'jars/media-service.conf',
        'liveactivitygroup' : 'Media services',
        'liveactivities' : [
            { 'name' : 'Media service', 'each_controller' : {'space_controller_name' : re.compile('42')} }
        ]
    },
}

def configure_live_activity(activity, config_filename, controller_name):
    activity_config = {}
    print "Configuring activity %s on controller %s with filename %s" % (activity.name(), controller_name, config_filename)
    for line in open(config_filename, 'r').readlines():
        line = line.rstrip()
        if line.find('#') == 0:
            continue
        item = string.split(line, '=', 1)
        val = string.Template(item[1]).safe_substitute(controller_config[controller_name])
        activity_config[item[0]] = val
    print "Final config for activity %s on controller %s: %s" % (activity.name(), controller_name, activity_config.__repr__())
    activity.set_config(activity_config)
    activity.send_configure()

# Delete extra controllers chef(?) is creating
print "Removing extraneous controllers"
for c in master.get_space_controllers():
    c.fetch()
    if c.name().find('controller') == -1:
        print "    Deleting controller \"%s\"" % c.name()
        c.send_delete()
        print "    ... deleted"

# Clean things out
print "Removing existing live activity groups"
remove_live_activity_groups()
print "... and live activities"
remove_live_activities()
print "... and activities"
remove_activities()

print "Uploading new activities"
# Upload activites' JAR files
for i in config:
    create_new_activity(config[i]['jar'])

# Create live activities
for i in config:
    print "Creating and configuring live activity \"%s\"" % i
    activity_name = config[i]['name']
    for l in config[i]['liveactivities']:
        if 'controller' in l.keys():
            n = create_new_live_activity(l['name'], activity_name, l['controller'], l['name'])
            n.send_deploy()
            configure_live_activity(n, config[i]['config'], l['controller'])
        elif 'each_controller' in l.keys():
            live_activities = []
            for c in master.get_space_controllers(l['each_controller']):
                c.fetch()
                activity_name = string.Template(config[i]['name']).substitute(controller=c.name())
                live_activity_name = "%s %s" % (l['name'], c.name())
                n = create_new_live_activity(live_activity_name, activity_name, c.name(), l['name'])
                n.send_deploy()
                configure_live_activity(n, config[i]['config'], c.name())
                live_activities.append({
                    "live_activity_name" : live_activity_name,
                    "space_controller_name" : c.name()
                })
            if 'liveactivitygroup' in config[i].keys():
                print "Creating live activity group for config item %s" % config[i]['name']
                create_new_live_activity_group(config[i]['liveactivitygroup'], activity_name, live_activities)
