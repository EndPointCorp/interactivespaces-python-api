import sys
sys.path.append("../")
sys.path.append("/home/galadmin/src/interactivespaces-python-api/")
import interactivespaces
from optparse import OptionParser
import ConfigParser
import urllib
import tempfile
import json

class Options:
    def __init__(self, args):
        self.parser = OptionParser()
        self.args = args
        self.parser.add_option("--action",
                               dest="action",
                               default=None,
                               help="Action that should be performed on the activity.\
                               Currently: create, exists, update_metadata, metadata_up_to_date",
                               metavar="ACTION")
        self.parser.add_option("--description",
                               dest="description",
                               default=None,
                               help="Description of the live activity",
                               metavar="DESCRIPTION")
        self.parser.add_option("--name",
                               dest="name",
                               default=None,
                               help="Name of the activity",
                               metavar="NAME")
        self.parser.add_option("--activity-name",
                               dest="activity_name",
                               default=None,
                               help="Activity name of the live activity",
                               metavar="ACTIVITYNAME")
        self.parser.add_option("--controller-name",
                               dest="controller_name",
                               default=None,
                               help="Controller name for the live activity",
                               metavar="NAME")
        self.parser.add_option("--metadata",
                               dest="metadata",
                               default=None,
                               help="Metadata of the live activity in format '{\"asd\" : \"value\"}' ",
                               metavar="METADATA")
        self.parser.add_option("--configuration",
                               dest="configuration",
                               default=None,
                               help="Configuration of the live activity in format '{\"asd\" : \"value\"}' ",
                               metavar="CONFIGURATION")
        self.parser.add_option("--config",
                               dest="config",
                               default="etc/ispaces-client.cfg",
                               help="Path to ispaces-client.cfg",
                               metavar="CONFIG")

        (self.options, self.args) = self.parser.parse_args()

    def get_options(self):
        return self.options

    def get_parser(self):
        return self.parser


class ManageLiveActivity:
    def __init__(self, options, parser):
        if not options:
            exit(1)
        self.parser = parser
        self.options = options
        self.config_path = self.options.config
        self._init_config()
        self.master = interactivespaces.Master(self.host, self.port)
        self.query = {
                      'activity_name': self.options.activity_name,
                      'live_activity_name': self.options.name,
                      'metadata': self.options.metadata,
                      'config': self.options.config,
                      'space_controller_name': self.options.controller_name,
                      'live_activity_description': self.options.description
                      }

    def exists(self):
        if self.options.name and self.options.controller_name:
            pass
        else:
            raise Exception("You must provide activity's name")
            exit(1)
        try:
            live_activity = self.master.get_live_activity(self.query)
        except interactivespaces.LiveActivityNotFoundException:
            print 'False'
            exit(0)
        if type(live_activity) == interactivespaces.LiveActivity:
            print 'True'
            exit(0)
        else:
            print 'False'
            exit(0)

    def create(self):
        if not self.options.name or not self.options.controller_name or not self.options.activity_name:
            self.parser.print_help()
            print 'Live Activity name, controller name or activity name not provided'
            exit(1)
        if self.master.new_live_activity(self.query):
            print 'True'
            exit(0)
        else:
            raise Exception("Could not create live activity")
            exit(1)

    def metadata_up_to_date(self):
        if self.options.metadata == None:
            self.parser.print_help()
            exit(0)
        supplied_metadata = json.loads(self.options.metadata)
        try:
            live_activity = self.master.get_live_activity(self.query)
            metadata = live_activity.metadata()
        except interactivespaces.LiveActivityNotFoundException, e:
            print 'False'
            exit(0)

        if supplied_metadata == metadata:
            print 'True'
            exit(0)
        else:
            print 'False'
            exit(0)

    def update_metadata(self):
        if self.options.metadata == None:
            self.parser.print_help()
            exit(0)
        supplied_metadata = json.loads(self.options.metadata)
        live_activity = self.master.get_live_activity(self.query)
        if live_activity.set_metadata(supplied_metadata):
            print 'True'
            exit(0)
        else:
            print 'False'
            exit(1)

    def config_up_to_date(self):
        if self.options.config == None:
            self.parser.print_help()
            exit(0)
        supplied_config = json.loads(self.options.config)
        try:
            live_activity = self.master.get_live_activity(self.query)
            config = live_activity.config()
        except interactivespaces.LiveActivityNotFoundException, e:
            print 'False'
            exit(0)

        if supplied_config == config:
            print 'True'
            exit(0)
        else:
            print 'False'
            exit(0)

    def update_config(self):
        if self.options.configuration == None:
            self.parser.print_help()
            exit(0)
        supplied_config = json.loads(self.options.configuration)
        live_activity = self.master.get_live_activity(self.query)
        if live_activity.set_config(supplied_config):
            print 'True'
            exit(0)
        else:
            print 'False'
            exit(1)


    def run(self):
        if self.options.action == 'create':
            self.create()
        elif self.options.action == 'exists':
            self.exists()
        elif self.options.action == 'update_metadata':
            self.update_metadata()
        elif self.options.action == 'metadata_up_to_date':
            self.metadata_up_to_date()
        elif self.options.action == 'update_config':
            self.update_metadata()
        elif self.options.action == 'config_up_to_date':
            self.metadata_up_to_date()
        else:
            self.parser.print_help()

    """ Private methods below """

    def _init_config(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.config_path)
        self.host = self.config.get('master', 'host')
        self.port = self.config.get('master', 'port')

if __name__ == "__main__":
    options = Options(sys.argv).get_options()
    parser = Options(sys.argv).get_parser()
    mla = ManageLiveActivity(options, parser)
    mla.run()
