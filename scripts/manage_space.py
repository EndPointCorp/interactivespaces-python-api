import sys
import json
sys.path.append("../")
sys.path.append("./")
sys.path.append("/home/galadmin/src/interactivespaces-python-api/")
import interactivespaces
import ConfigParser
from optparse import OptionParser

# TODO (wz): make support for checking not only if the LAG exists but also if it has proper members

class Options:
    def __init__(self, args):
        self.parser = OptionParser()
        self.args = args
        self.parser.add_option("--action",
                               dest="action",
                               default=None,
                               help="Action that should be performed on the space.\
                               Currently: create, exists, update_metadata, metadata_up_to_date, \
                               update_live_activity_groups_list, live_activity_groups_up_to_date",
                               metavar="ACTION")
        self.parser.add_option("--description",
                               dest="description",
                               default=None,
                               help="Description of the space",
                               metavar="DESCRIPTION")
        self.parser.add_option("--name",
                               dest="name",
                               default=None,
                               help="Name of the space",
                               metavar="NAME")
        self.parser.add_option("--live-activity-groups",
                               dest="live_activity_groups",
                               default=None,
                               help="Defines which Live Activity Groups should comprise this space in json format closed in single quotes like \
                                '[{\"live_activity_group_name\" : \"some_name\", \"live_activity_group_name\" : \"different_name\"}]'",
                               metavar="LIVEACTIVITTGROUPS")
        self.parser.add_option("--metadata",
                               dest="metadata",
                               default=None,
                               help="Metadata of the space in json firmat enclosed in single quotes:\
                               '[{\"key\" : \"value\"}]'",
                               metavar="METADATA")
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


class ManageSpace:
    def __init__(self, options, parser):
        if not options:
            exit(1)
        self.parser = parser
        self.options = options
        self.config_path = self.options.config
        self._init_config()

        self.master = interactivespaces.Master(self.host, self.port)
        self.query = {'space_name': self.options.name,
                      'space_description' : '' if self.options.description == None else self.options.description,
                      'live_activity_groups' : json.loads(self.options.live_activity_groups) if self.options.live_activity_groups else None,
                      'metadata' : json.loads(self.options.metadata) if self.options.metadata else None
                     }

    def exists(self):
        if self.options.name:
            pass
        else:
            raise Exception("You must provide space name")
            exit(1)
        try:
            space = self.master.get_space(self.query)
        except interactivespaces.SpaceNotFoundException:
            print 'False'
            exit(0)
        if type(space) == interactivespaces.Space:
            print 'True'
            exit(0)
        else:
            print 'False'
            exit(0)

    def create(self):
        if (not self.options.name
            or not self.options.live_activity_groups):
            self.parser.print_help()
            print 'Live Activity Group live and space name must be provided'
            exit(1)
        if self.master.new_space(self.query):
            print 'True'
            exit(0)
        else:
            raise Exception("Could not create live activity group")
            exit(1)

    def metadata_up_to_date(self):
        if self.options.metadata == None or self.options.name == None:
            self.parser.print_help()
            exit(1)
        supplied_metadata = json.loads(self.options.metadata)
        try:
            space = self.master.get_space(self.query)
            metadata = space.metadata()
        except interactivespaces.SpaceNotFoundException, e:
            print 'False'
            exit(1)
        if supplied_metadata == metadata:
            print 'True'
            exit(0)
        else:
            print 'False'
            exit(0)

    def update_metadata(self):
        if self.options.metadata == None or self.options.name == None:
            self.parser.print_help()
            exit(1)
        supplied_metadata = json.loads(self.options.metadata)
        space = self.master.get_space(self.query)
        if space.set_metadata(supplied_metadata):
            print 'True'
            exit(0)
        else:
            print 'False'
            exit(1)

    def live_activity_groups_up_to_date(self):
        if (not self.options.live_activity_groups) or (not self.options.name):
            self.parser.print_help()
            exit(1)
        supplied_live_activity_groups = json.loads(self.options.live_activity_groups)
        try:
            space = self.master.get_space(self.query)
            space_live_activity_groups = space.live_activity_groups()
        except interactivespaces.SpaceNotFoundException, e:
            print 'False'
            exit(1)

        space_live_activity_groups = self._build_live_activity_groups_list(space_live_activity_groups)

        if self._compare_live_activity_groups_lists(supplied_live_activity_groups, space_live_activity_groups):
            print 'True'
            exit(0)
        else:
            print 'False'
            exit(0)

    def _compare_live_activity_groups_lists(self, supplied_live_activity_groups, space_live_activity_groups):
        try:
            print "Supplied LAG: %s" % supplied_live_activity_groups
            print "Space LAGs: %s" % space_live_activity_groups

            map(lambda x: space_live_activity_groups.pop(
                    space_live_activity_groups.index(x)), supplied_live_activity_groups)
            if len(space_live_activity_groups) == 0:
                print 'True'
                exit(0)
            else:
                print 'False'
                exit(0)
        except Exception, e:
            print 'False'
            exit(0)

    def _build_live_activity_groups_list(self, live_activity_groups):
        live_activity_groups_list = []
        for lag in live_activity_groups:
            live_activity_groups_list.append({"live_activity_group_name" : lag['name']})
        return live_activity_groups_list

    def update_live_activity_groups_list(self):
        if not self.options.live_activity_groups or not self.options.name:
            self.parser.print_help()
            exit(1)
        supplied_live_activity_groups = json.loads(self.options.live_activity_groups)
        supplied_live_activity_groups_ids = self.master._translate_live_activity_groups_names_to_ids(supplied_live_activity_groups)
        space = self.master.get_space(self.query)
        if space.set_live_activity_groups(supplied_live_activity_groups_ids):
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
        elif self.options.action == 'update_live_activity_groups_list':
            self.update_live_activity_groups_list()
        elif self.options.action == 'live_activity_groups_up_to_date':
            self.live_activity_groups_up_to_date()
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
    mlag = ManageSpace(options, parser)
    mlag.run()
