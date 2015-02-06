import sys
sys.path.append("../")
sys.path.append("/home/galadmin/src/interactivespaces-python-api/")
import interactivespaces
from optparse import OptionParser
import ConfigParser
import urllib
import tempfile


class Options:
    def __init__(self, args):
        self.parser = OptionParser()
        self.args = args
        self.parser.add_option("--action",
                               dest="action",
                               default=None,
                               help="Action that should be performed on the controller.\
                               Currently available options: create or exists",
                               metavar="ACTION")
        self.parser.add_option("--name",
                               dest="name",
                               default=None,
                               help="Name of the controller",
                               metavar="NAME")
        self.parser.add_option("--hostid",
                               dest="hostid",
                               default=None,
                               help="Host id of the controller",
                               metavar="HOSTID")
        self.parser.add_option("--description",
                               dest="description",
                               default=None,
                               help="Controller's description",
                               metavar="description")
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


class ManageController:
    def __init__(self, options, parser):
        if not options:
            exit(1)
        self.parser = parser
        self.options = options
        self.config_path = self.options.config
        self._init_config()
        self.master = interactivespaces.Master(self.host, self.port)
        self.query = {'space_controller_name': self.options.name,
                     'space_controller_host_id': self.options.hostid,
                     'space_controller_description': self.options.description
                     }

    def exists(self):
        controller = ''
        if self.options.name:
            pass
        else:
            raise Exception("You must provide controller's name")
        try:
            controller = self.master.get_space_controller(self.query)
        except interactivespaces.ControllerNotFoundException:
            print 'False'
            exit(0)
        if type(controller) == interactivespaces.SpaceController:
            print 'True'
            exit(0)
        else:
            print 'False'
            exit(0)

    def create(self):
        if not self.options.name or not self.options.hostid:
            self.parser.print_help()
            print 'Controller name or hostid not provided via options'
            exit(1)
        if self.master.new_space_controller(self.query):
            print 'True'
            exit(0)
        else:
            raise Exception("Could not create controller")

    def get_uuid(self):
        controller = ''
        if self.options.name or self.options.hostid:
            pass
        else:
            raise Exception("You must provide controller's name and hostid")
        try:
            controller = self.master.get_space_controller(self.query)
        except interactivespaces.ControllerNotFoundException:
            print 'False'
            exit(0)
        if type(controller) == interactivespaces.SpaceController:
            print controller.uuid()
            exit(0)
        else:
            print 'False'
            exit(0)

    def run(self):
        if self.options.action == 'create':
            self.create()
        elif self.options.action == 'exists':
            self.exists()
        elif self.options.action == 'get_uuid':
            self.get_uuid()
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
    mc = ManageController(options, parser)
    mc.run()
