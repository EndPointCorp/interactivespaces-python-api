# -*- coding: utf-8 -*-

import urllib2
import json
from abstract import Path
from misc import Logger
from exception import CommunicableException
import requests
import urlparse
import os

"""
    :todo: aggregate mixins common for LiveActivity, LiveActivityGroup and Space into one
"""

class Communicable(object):
    def __init__(self):
        """
           Should be responsible for communication with the API
        """
        self.log = Logger().get_logger()

    def _compose_url(self, uri, class_name=None, method_name=None, context=None, action=None):
        """
        Should compose URL trying to do that in two steps:
            1. return if object that tries to retrieve the url
            has route that is already staticaly defined
            2. try to compose the custom route on the basis of URL data
            
        :rtype: string
        """
        if class_name and method_name:
            self.log.info("Composing url for class_name '%s' and method name '%s'" % (class_name, method_name))
            static_route = Path().get_route_for(class_name, method_name)
            if static_route :
                self.log.info("Returned auto url %s" % (static_route))
                url = "%s%s" % (uri, static_route)
                return url

        elif context and action:
            url = "%s%s%s" % (uri, context, action)
            self.log.info("Composed url %s" % (url))
            return url
        else:
            self.log.info("Could not compose an url.")
            raise CommunicableException

    def _urlopen(self, url, data=None):
        """Helper for opening urls."""
        return urllib2.urlopen(url, data)

    def _api_get_json(self, url):
        """
        Sends a json request to the master. Returns only ['data'] part of the json response

        :rtype: dict or bool
        """
        try:
            response = urllib2.urlopen(url)
            data = json.loads(response.read())
        except urllib2.URLError, e:
            self.log.error("Could not communicate with Master API becasue: %s" % e)
            print "Could not communicate with Master API because %s" % e
            sys.exit(1)

        try:
            out_data = data['data']
        except Exception:
            out_data = None

        if data['result'] != 'success':
            self.log.info("Could not retrieve data for URL=%s" % url)
            return False

        if out_data:
            return out_data
        else:
            return True

    def _api_get_html(self, url, content=False):
        """
        Sends a request to the master, returns True if 200, False if anything else.
        
        :rtype: bool
        """
        response = urllib2.urlopen(url)
        data = response.read()
        if response.getcode() == 200:
            if content == True:
                return data
            else:
                return True
        else:
            return False

    def _api_post_json(self, url, payload, file_handler=None):
        """
        Sends data to the master.
        
        :rtype: string or False
        
        :param payload: dictionary containing data to send
        
        :param url: string containing url that we talk to
        
        :param file_handler: path to local zipfile - if provided, a multi-part post will be sent to the URL
        """
        if file_handler:
            head, tail = os.path.split(file_handler.name)
            file_name = tail
            file_content_type = "application/zip"
            files = {"activityFile" : (file_name , file_handler, file_content_type)}
        else:
            files = None
        self.log.info("Doing a POST request to %s with payload %s" %(url, payload))
        session = requests.session()
        get_response = session.get(url)
        query = urlparse.urlparse(get_response.url).query
        cookies = {"JSESSIONID" : session.cookies['JSESSIONID']}
        url = url + "?" + query
        post_response = session.post(url=url, cookies=cookies, data=payload, files=files) 
        if post_response.status_code == 200:
            self.log.info("_api_post_json returned 200 with post_response.url=%s" % post_response.url)
            return post_response
        else:
            self.log.info("_api_post_json returned post_response.status_code %s" % post_response.status_code)
            return False

    def _api_post_json_no_cookies(self, url, payload, file_handler=None):
        """
        Sends data to the master without looking for cookies
        
        :rtype: string or False
        
        :param payload: dictionary containing data to send
        
        :param url: string containing url that we talk to
        
        :param file_handler: path to local zipfile - if provided, a multi-part
        post will be sent to the URL
        """
        if file_handler:
            head, tail = os.path.split(file_handler.name)
            file_name = tail
            file_content_type = "application/zip"
            files = {"activityFile" : (file_name , file_handler, file_content_type)}
        else:
            files = None
        self.log.info("Doing a POST request to %s with payload %s" %(url, payload))
        session = requests.session()
        get_response = session.get(url)
        query = urlparse.urlparse(get_response.url).query
        url = url + "?" + query
        post_response = session.post(url=url, data=payload, files=files) 
        if post_response.status_code == 200:
            self.log.info("_api_post_json returned 200 with post_response.url=%s" % post_response.url)
            return post_response
        else:
            self.log.info("_api_post_json returned post_response.status_code %s" % post_response.status_code)
            return False

    def _api_post_html(self, command, query=None, data=None):
        """Sends data to the master."""
        raise NotImplementedError

    def json_raw(self):
        """
            Returns raw unformatted/unmapped json from Master API
            :rtype: dict
        """
        return self.data

class Fetchable(Communicable):
    """
        Should be responsible for fetching most up to date data from API
    """
    def __init__(self):
        super(Fetchable, self).__init__()

    def _refresh_object(self, url):
        """
        Should retrieve fresh data from API
        
        :param url: string defining from which url to fetch the data
        """
        self.log.info("Refreshing object for url=%s" % url)
        data = self._api_get_json(url)
        if data:
            self.log.info("Successfully refresh object for url=%s" % url)
            return data
        else:
            self.log.info("Could not refresh object for url=%s" % url)
            return False

    def fetch(self):
        """
             Should retrieve private data for an object from Master API
        """
        self.data_hash = self._refresh_object(self.absolute_url)

class Statusable(Communicable):
    """
    Should be responsible for _refreshing_ status of the object,
    which means that it will send "status" command to IS Controllers.
    In order to fetch the fresh and most up-to-date status you should use
    .fetch() method on the object.
    """

    def __init__(self):
        self.log = Logger().get_logger()
        super(Statusable, self).__init__()

    def send_status_refresh(self):
        """
        Extracts self.data_hash and self.class_name from children class
        and finds out to which route send GET request to ands sends it
        """
        refresh_route = Path().get_route_for(self.class_name, 'status') % self.data_hash['id']
        if self._send_status_refresh(refresh_route):
            self.log.info("Successfully refreshed status for url=%s" % self.absolute_url)
            return True
        else:
            return False

    def _send_status_refresh(self, refresh_route):
        """
        Should tell master to retrieve status info from controller
        so master has the most up to date info from the controller
        
        :param refresh_route: status.json route for specific class
        
        :rtype: bool
        """
        url = "%s%s" % (self.uri, refresh_route)
        self.log.info("Sending status refresh to url=%s" %url)
        try:
            response = self._api_get_json(url)
        except urllib2.HTTPError, e:
            response = None
            self.log.error("Could not send status refresh because %s" % e)
        if response:
            return True
        else:
            return False

class Deletable(Communicable):
    """
    Should be responsible for the deletion of an object
    """
    def __init__(self):
        self.log = Logger().get_logger()
        super(Deletable, self).__init__()

    def send_delete(self):
        """
        Sends the "delete" GET request to a route
        """
        delete_route = Path().get_route_for(self.class_name, 'delete') % self.data_hash['id']
        if self._send_delete_request(delete_route):
            self.log.info("Successfully sent 'delete' to url=%s" % self.absolute_url)
            return True
        else:
            return False

    def _send_delete_request(self, delete_route):
        """
        :rtype: bool
        """
        url = "%s%s" % (self.uri, delete_route)
        self.log.info("Sending 'delete' to url=%s" %url)
        try:
            response = self._api_get_html(url)
        except urllib2.HTTPError, e:
            response = None
            self.log.error("Could not send 'delete' because %s" % e)
        if response:
            return True
        else:
            return False

class Shutdownable(Communicable):
    """
    Should be responsible for sending "shutdown" command to live activities,
    controllers, spaces and live groups.
    """

    def __init__(self):
        self.log = Logger().get_logger()
        super(Shutdownable, self).__init__()

    def send_shutdown(self):
        shutdown_route = Path().get_route_for(self.class_name, 'shutdown') % self.data_hash['id']
        if self._send_shutdown_request(shutdown_route):
            self.log.info("Successfully sent shutdown for url=%s" % self.absolute_url) 
            return True
        else:
            return False

    def _send_shutdown_request(self, shutdown_route):
        """
        Makes a shutdown request
        """
        url = "%s%s" % (self.uri, shutdown_route)
        self.log.info("Sending 'shutdown' GET request to url=%s" %url)
        try:
            response = self._api_get_json(url)
        except urllib2.HTTPError, e:
            response = None
            self.log.error("Could not send 'shutdown' GET request because %s" % e)
            if e=='HTTP Error 500: No connection to controller in 5000 milliseconds':
                raise CommunicableException('HTTP Error 500: No connection to controller in 5000 milliseconds')
        if response:
            return True
        else:
            return False

class Startupable(Communicable):
    """
    Should be responsible for sending "startup" command to live activities,
    controllers, spaces and live groups.
    """

    def __init__(self):
        self.log = Logger().get_logger()
        super(Startupable, self).__init__()

    def send_startup(self):
        startup_route = Path().get_route_for(self.class_name, 'startup') % self.data_hash['id']
        if self._send_startup_request(startup_route):
            self.log.info("Successfully sent 'startup' for url=%s" % self.absolute_url)
            return True
        else:
            return False

    def _send_startup_request(self, startup_route):
        """
        Makes a startup request
        """
        url = "%s%s" % (self.uri, startup_route)
        self.log.info("Sending 'startup' GET request to url=%s" %url)
        try:
            response = self._api_get_json(url)
        except urllib2.HTTPError, e:
            response = None
            self.log.error("Could not send 'startup' GET request because %s" % e)
            if e=='HTTP Error 500: No connection to controller in 5000 milliseconds':
                raise CommunicableException('HTTP Error 500: No connection to controller in 5000 milliseconds')
        if response:
            return True
        else:
            return False

class Activatable(Communicable):
    """
    Should be responsible for sending the "activate" action
    """
    def __init__(self):
        self.log = Logger().get_logger()
        super(Activatable, self).__init__()

    def send_activate(self):
        activate_route = Path().get_route_for(self.class_name, 'activate') % self.data_hash['id']
        if self._send_activatable_request(activate_route):
            self.log.info("Successfully sent 'activate' for url=%s" % self.absolute_url)
            return True
        else:
            return False

    def send_deactivate(self):
        deactivate_route = Path().get_route_for(self.class_name, 'deactivate') % self.data_hash['id']
        if self._send_activatable_request(deactivate_route):
            self.log.info("Successfully sent 'deactivate' for url=%s" % self.absolute_url)
            return True
        else:
            return False

    def _send_activatable_request(self, activatable_route):
        """
        Makes a activate/deactivate request
        """
        url = "%s%s" % (self.uri, activatable_route)
        self.log.info("Sending activatable GET request to url=%s" %url)
        try:
            response = self._api_get_json(url)
        except urllib2.HTTPError, e:
            response = None
            self.log.error("Could not send activatable GET request because %s" % e)
        if response:
            return True
        else:
            return False

class Deployable(Communicable):
    """
    Should be responsible for sending the "deploy" action
    """
    def __init__(self):
        self.log = Logger().get_logger()
        super(Deployable, self).__init__()

    def send_deploy(self):
        deploy_route = Path().get_route_for(self.class_name, 'deploy') % self.data_hash['id']
        if self._send_deploy_request(deploy_route):
            self.log.info("Successfully sent 'deploy' for url=%s" % self.absolute_url) 
            return True
        else:
            return False

    def _send_deploy_request(self, deploy_route):
        """
            Makes a 'deploy' request
        """
        url = "%s%s" % (self.uri, deploy_route)
        self.log.info("Sending deploy GET request to url=%s" %url)
        try:
            response = self._api_get_json(url)
        except urllib2.HTTPError, e:
            response = None
            self.log.error("Could not send deploy GET request because %s" % e)
        if response:
            return True
        else:
            return False

class Configurable(Communicable):
    """
    Should be responsible for sending the "configure" action
    """
    def __init__(self):
        self.log = Logger().get_logger()
        super(Configurable, self).__init__()

    def send_configure(self):
        configure_route = Path().get_route_for(self.class_name, 'configure') % self.data_hash['id']
        if self._send_configure_request(configure_route):
            self.log.info("Successfully sent 'configure' for url=%s" % self.absolute_url)
            return True
        else:
            return False

    def _send_configure_request(self, configure_route):
        """
        Makes a 'configure' request
        """
        url = "%s%s" % (self.uri, configure_route)
        self.log.info("Sending configure GET request to url=%s" %url)
        try:
            response = self._api_get_json(url)
        except urllib2.HTTPError, e:
            response = None
            self.log.error("Could not send configure GET request because %s" % e)
        if response:
            return True
        else:
            return False

class Cleanable(Communicable):
    """
    Should be responsible for permanent clean and cleaning the tmp
    """
    def __init__(self):
        self.log = Logger().get_logger()
        super(Cleanable, self).__init__()

    def send_clean_permanent(self):
        configure_route = Path().get_route_for(self.class_name, 'clean_permanent') % self.data_hash['id']
        if self._send_cleanable_request(configure_route):
            self.log.info("Successfully sent 'clean_permanent' for url=%s" % self.absolute_url)
            return True
        else:
            return False

    def send_clean_tmp(self):
        configure_route = Path().get_route_for(self.class_name, 'clean_tmp') % self.data_hash['id']
        if self._send_cleanable_request(configure_route):
            self.log.info("Successfully sent 'clean_tmp' for url=%s" % self.absolute_url)
            return True
        else:
            return False

    def _send_cleanable_request(self, cleanable_route):
        """
        Makes a cleanable request
        """
        url = "%s%s" % (self.uri, cleanable_route)
        self.log.info("Sending cleanable GET request to url=%s" %url)
        try:
            response = self._api_get_json(url)
        except urllib2.HTTPError, e:
            response = None
            self.log.error("Could not send cleanable GET request because %s" % e)
            if e=='HTTP Error 500: No connection to controller in 5000 milliseconds':
                raise CommunicableException('HTTP Error 500: No connection to controller in 5000 milliseconds')
        if response:
            return True
        else:
            return False

class Connectable(Communicable):
    """
    Should be responsible for connecting/disconnecting space controllers
    """
    def __init__(self):
        self.log = Logger().get_logger()
        super(Connectable, self).__init__()

    def send_connect(self):
        connect_route = Path().get_route_for(self.class_name, 'connect') % self.data_hash['id']
        if self._send_connectable_request(connect_route):
            self.log.info("Successfully sent 'connect' for url=%s" % self.absolute_url)
            return True
        else:
            return False

    def send_disconnect(self):
        disconnect_route = Path().get_route_for(self.class_name, 'disconnect') % self.data_hash['id']
        if self._send_connectable_request(disconnect_route):
            self.log.info("Successfully sent 'disconnect' for url=%s" % self.absolute_url)
            return True
        else:
            return False

    def _send_connectable_request(self, connectable_route):
        """
        Makes a connectable request
        """
        url = "%s%s" % (self.uri, connectable_route)
        self.log.info("Sending connectable GET request to url=%s" %url)
        try:
            response = self._api_get_json(url)
        except urllib2.HTTPError, e:
            response = None
            self.log.error("Could not send connectable GET request because %s" % e)
        if response:
            return True
        else:
            return False

class Configable(Communicable):
    """
    Should be responsible for setting the 'Edit config' section.
    Name of thix mixin is such because there's already "configure" action for live activities
    """
    def __init__(self):
        self.log = Logger().get_logger()
        super(Configable, self).__init__()

    def get_config(self):
        config_route = Path().get_route_for(self.class_name, 'config') % self.data_hash['id']
        self.log.info("Getting config of %s" % (self.class_name))
        response = self._send_configable_get_request(config_route)
        if response:
            self.log.info("Successfully got config from url=%s" % self.absolute_url)
            return self._scrap_config(response)
        else:
            return False

    def set_config(self, config_dictionary):
        """
        Accepts dictionary of keys that will be unpacked to "key=value" strings and
        makes a request overwriting any previous config
        :rtype: bool
        :param config_dictionary: Dictionary with keys and values
        """
        config = {"values" : self._unpack_config(config_dictionary)}
        self.log.info("Updating config of %s with %s" % (self.class_name, config))
        config_route = Path().get_route_for(self.class_name, 'config') % self.data_hash['id']
        if self._send_configable_set_request(config_route, config):
            self.log.info("Successfully sent config for url=%s" % self.absolute_url)
            return True
        else:
            return False

    def _scrap_config(self, html):
        import BeautifulSoup
        soup = BeautifulSoup.BeautifulSoup(html)
        self.log.info("Received config response: %s" % soup)
        textarea = soup.findAll('textarea')[0].text.split('\n')
        config_dict = self._pack_config(textarea)
        self.log.info("Scrapped config: %s" % config_dict)
        return config_dict

    def _pack_config(self, config_list):
        """
        Accepts list of strings and converts it into dictionary
        :rtype: dict
        :param config_string: string containing scraped config
        """
        config_dict = {}
        self.log.info("Textarea: %s" % config_list)
        try:
            for config_item in config_list:
                key, value = config_item.split('=')
                self.log.info("Assigning %s to %s" % (key,value))
                config_dict[key] = value
        except:
            self.log.info("Could not do a _pack_config for scraped config on item: %s for config_list %s" % (config_item, config_list))
            config_dict = {}
        return config_dict

    def _unpack_config(self, config_dictionary):
        """
        Accepts dictionary and converts it to string
        :rtype: string
        :param config_dictionary: dict containing config
        """
        config_text = ""
        try:
            for key, value in config_dictionary.iteritems():
                config_text = config_text + ("\r\n") + key + "=" + value
            return config_text
        except Exception, e:
            self.log.error("Could not unpack supplied config dictionary because %s" % e)
            raise


    def _send_configable_get_request(self, config_route):
        """
        Makes a configable get request
        """
        url = "%s%s" % (self.uri, config_route)
        self.log.info("Sending configable GET request to url=%s" %url)
        try:
            response = self._api_get_html(url, content=True)
        except urllib2.HTTPError, e:
            response = None
            self.log.error("Could not send configable GET request because %s" % e)
        if response:
            return response
        else:
            return False

    def _send_configable_set_request(self, config_route, config):
        """
        Makes a configable set request
        """
        url = "%s%s" % (self.uri, config_route)
        self.log.info("Sending configable POST request to url=%s" %url)
        try:
            response = self._api_post_json_no_cookies(url, config)
        except urllib2.HTTPError, e:
            response = None
            self.log.error("Could not send configable GET request because %s" % e)
        if response:
            return True
        else:
            return False

class Metadatable(Communicable):
    """
    Should be responsible for setting metadata
    """
    def __init__(self):
        self.log = Logger().get_logger()
        super(Metadatable, self).__init__()

    def set_metadata(self, metadata_dictionary):
        """
        Accepts dictionary of keys that will be unpacked to "key=value" strings and
        makes a request overwriting any previous metadata
        :rtype: bool
        :param metadata_args: Dictionary with keys and values
        """
        metadata = {"values" : self._unpack_metadata(metadata_dictionary)}
        self.log.info("Updating metadata of %s with %s" % (self.class_name, metadata))
        metadata_route = Path().get_route_for(self.class_name, 'metadata') % self.data_hash['id']
        if self._send_metadatable_request(metadata_route, metadata):
            self.log.info("Successfully sent metadata for url=%s" % self.absolute_url)
            return True
        else:
            return False

    def _unpack_metadata(self, metadata_dictionary):
        """
        Accepts dictionary and converts it to string
        :rtype: string
        :param metadata_dictionary: dict containing metadata
        """
        metadata_text = ""
        try:
            for key, value in metadata_dictionary.iteritems():
                metadata_text = metadata_text + ("\r\n") + key + "=" + value
            return metadata_text
        except Exception, e:
            self.log.error("Could not unpack supplied metadata dictionary because %s" % e)
            raise

    def _send_metadatable_request(self, metadata_route, metadata):
        """
        Makes a editable request
        """
        url = "%s%s" % (self.uri, metadata_route)
        self.log.info("Sending editable POST request to url=%s" %url)
        try:
            response = self._api_post_json_no_cookies(url, metadata)
        except urllib2.HTTPError, e:
            response = None
            self.log.error("Could not send connectable GET request because %s" % e)
        if response:
            return True
        else:
            return False

class Updatable(Communicable):
    """
    :todo: Create methods for updating all the fields
    """
    pass
