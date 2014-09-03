from misc import Logger
from exception import SerializerException
import json


class Serializer(object):
    """
        Should be responsible for representing instances of classes in desired form
    """
    def __init__(self):
        self.log = Logger().get_logger()
        self.log.debug("Instantiated Serializer with data %s" % self.data_hash)
        pass

    def __repr__(self):
        return str(self.data_hash)

    def __str__(self):
        return self.data_hash

    def _assign_attributes(self):
        """
            Should change the key names from original API keys to the ones we want
            :return: None
        """
        for new_key, old_key in self.attributes.iteritems():
            try:
                self.data[new_key] = self.data_hash[old_key]
            except SerializerException, e:
                """ possible do something fancy here """
            except Exception, e:
                self.log.info("Could not assign attribute %s while operating on Object: %s because %s" % (old_key, self.data_hash, e))


class StringSerializer(Serializer):
    """
        In future should be responsible for custom string serialization
    """
    def __init__(self):
        super(StringSerializer, self).__init__()

    def to_string(self, key):
        """
            Should accept key that needs to retrieved from Activity attributes
            :return: string
        """
        self._assign_attributes()
        pass

class JsonSerializer(Serializer):
    """
        Should know everything about serializing data to json format
    """

    def __init__(self):
        super(JsonSerializer, self).__init__()
        self.log.info("Instantiated JsonSerializer")

    def to_json_raw(self):
        """
            Should return data_hash in original form
            :rtype: dict
        """
        return self.data_hash

    def to_json(self):
        """
            :return: json string formatted by attributes dictionary
        """
        self._assign_attributes()
        return json.dumps(self.data)


class ActivitySerializer(JsonSerializer, StringSerializer):
    """
        Should be responsible for representing Activity data using
        desired format, attributes and method of representation
        Should be initialized only with the Activity data_hash
    """

    def __init__(self, data_hash):
        self.data_hash = data_hash['activity']
        self.data = {}
        self.attributes = {
                            "name" : "name",
                            "id" : "id",
                            "version" : "version",
                            "description" : "description"
                            }
        super(ActivitySerializer, self).__init__()


class LiveActivitySerializer(JsonSerializer, StringSerializer):
    """
        Should be responsible for representing LiveActivity data using
        desired format, attributes and method of representation
        Should be initialized only with the Activity data_hash

    """

    def __init__(self, data_hash):
        self.data_hash = data_hash
        self.data = {}
        self.attributes = {
                            "name" : "name",
                            "id" : "id",
                            "state" : "active",
                            "description" : "description"
                            }
        super(LiveActivitySerializer, self).__init__()


class LiveActivityGroupSerializer(JsonSerializer, StringSerializer):
    """
        Should be responsible for representing LiveActivity data using
        desired format, attributes and method of representation
        Should be initialized only with the Activity data_hash

    """

    def __init__(self, data_hash):
        self.data_hash = data_hash
        self.data = {}
        self.attributes = {
                            "name" : "name",
                            "id" : "id",
                            "description" : "description",
                            "live_activities" : "liveActivities"
                            }

        super(LiveActivityGroupSerializer, self).__init__()

class SpaceSerializer(JsonSerializer, StringSerializer):
    """
        Should be responsible for representing LiveActivity data using
        desired format, attributes and method of representation
        Should be initialized only with the Activity data_hash
    """

    def __init__(self, data_hash):
        self.data_hash = data_hash
        self.data = {}
        self.attributes = {
                            "name" : "name",
                            "id" : "id",
                            "description" : "description",
                            "live_activity_groups" : "liveActivityGroups"
                            }

        super(SpaceSerializer, self).__init__()

class SpaceControllerSerializer(JsonSerializer, StringSerializer):
    """
        Should be responsible for representing LiveActivity data using
        desired format, attributes and method of representation
        Should be initialized only with the Activity data_hash

    """

    def __init__(self, data_hash):
        self.data_hash = data_hash
        self.data = {}
        self.attributes = {
                            "name" : "name",
                            "id" : "id",
                            "description" : "description",
                            "mode" : "mode",
                            "uuid" : "uuid"
                            }

        super(SpaceControllerSerializer, self).__init__()
