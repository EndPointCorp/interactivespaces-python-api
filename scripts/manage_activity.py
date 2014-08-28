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
                               help="Action that should be performed on the activity.\
                               Currently: upload or exists",
                               metavar="ACTION")
        self.parser.add_option("--version",
                               dest="version",
                               default=None,
                               help="Version of the activity",
                               metavar="VERSION")
        self.parser.add_option("--url",
                               dest="url",
                               default=None,
                               help="Url to an archive (currently only .zip)",
                               metavar="URL")
        self.parser.add_option("--name",
                               dest="name",
                               default=None,
                               help="Name of the activity",
                               metavar="NAME")
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


class ManageActivity:
    def __init__(self, options, parser):
        if not options:
            exit(1)
        self.parser = parser
        self.options = options
        self.config_path = self.options.config
        self._init_config()
        self.master = interactivespaces.Master(self.host, self.port)

    def exists(self):
        if self.options.name:
            query = {'activity_name': self.options.name,
                     'activity_version': self.options.version}
        else:
            raise Exception("You must provide activity's name")
        activity = self.master.get_activity(query)
        if type(activity) == interactivespaces.Activity:
            print 'True'
            exit(0)
        else:
            print 'False'
            exit(0)

    def upload(self):
        if not self.options.url:
            self.parser.print_help()
            print 'IS master url not provided in options'
            exit(1)
        zipfile = self._fetch_from_url()
        if self.master.new_activity({'zip_file_handler': zipfile}):
            zipfile.close()
            print 'True'
            exit(0)
        else:
            zipfile.close()
            raise Exception("Could not upload activity")

    def run(self):
        if self.options.action == 'upload':
            self.upload()
        elif self.options.action == 'exists':
            self.exists()
        else:
            self.parser.print_help()

    """ Private methods below """

    def _fetch_from_url(self):
        downloader = urllib.URLopener()
        activity_tmp_file = tempfile.NamedTemporaryFile(delete=False)
        downloader.retrieve(self.options.url,
                            activity_tmp_file.name)
        return activity_tmp_file

    def _init_config(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.config_path)
        self.host = self.config.get('master', 'host')
        self.port = self.config.get('master', 'port')

if __name__ == "__main__":
    options = Options(sys.argv).get_options()
    parser = Options(sys.argv).get_parser()
    ma = ManageActivity(options, parser)
    ma.run()
