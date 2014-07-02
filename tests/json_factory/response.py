import json

class JsonResponse(object):
    """
        @summary: needs to be initialized with path to json_factory dir
    """
    def __init__(self, path_to_json_factory_directory="json_factory"):
        self.path_to_json_factory_directory = path_to_json_factory_directory
        
    def activity_all(self):
        return self._read_file('activity_all.json')
    
    def liveactivity_all(self):
        return self._read_file('liveactivity_all.json')
        
    def liveactivitygroup_all(self):
        return self._read_file('liveactivitygroup_all.json')
    
    def space_all(self):
        return self._read_file('space_all.json')

    def spacecontroller_all(self):
        return self._read_file('spacecontroller_all.json')
    
    """ Picked id = 56 for tests """
    def activity_56_view(self):
        return self._read_file('activity_56_view.json')
    
    def activity_56_uri(self):
        return "http://lg-head:8080/interactivespaces"
    
    def activity_56_absolute_url(self):
        return "http://lg-head:8080/interactivespaces/activity/56/view.json"
    
    def activity_56_initial_data_hash(self):
        return self._read_file('activity_56_initial_data_hash.json')
    
    def activity_56_upload_uri(self):
        return "http://lg-head:8080/interactivespaces/activity/upload"

    def _read_file(self, filename):
        """
            @summary: reads a file and returns it
            @rtype: dict
        """
        filename = self.path_to_json_factory_directory + "/" + filename
        with open(filename, 'r') as f:
            content = f.read().strip()
        
        if content:
            return json.loads(content)   