import sys, os
sys.path.append(os.curdir)
import interactivespaces
import logging
from termcolor import colored


class TestFactory:
    def __init__(self):
        self.activity_name = "Message Tester"
        self.space_controller_name = "Integration Test Space Controller"
        self.live_activity_name = "Integration Test Live Activity"
        self.live_activity_group = "Integration Test Live Activity Group"
        self.space_name = "Integration Test Space"

        self.activity = {
                "activity_name": self.activity_name,
                "activity_version": "0.0.1",
                "zip_file_handler": open('tests/integration/activities/com.endpoint.messageTester-0.0.1.zip', 'r')
                }

        self.space_controller = {
                "space_controller_name": self.space_controller_name,
                "space_controller_description": "Integration test description of space controller",
                "space_controller_host_id": "integration_test_host_id"
                }

        self.live_activity = {
                "activity_name": self.activity_name,
                "live_activity_name": self.live_activity_name,
                "live_activity_description": "Description of integration test live activity",
                "space_controller_name": self.space_controller_name
                }

        self.live_activity_group = {
                "live_activity_group_name": self.live_activity_group_name,
                "live_activity_group_description": "Integration test live activity group description",
                "live_activities": [self.live_activity]
                }

        self.space = {
                "space_name": self.space_name,
                "space_description": "Integration test space description",
                "live_activity_groups": [self.live_activity_group]
                }

class TestScenario:
    def __init__(self):
        self.factory = TestFactory()
        self.master = interactivespaces.Master()

    def run_test(self):
        self._create_objects()
        if self._make_asserts():
            print colored("OK", "green")
            sys.exit(0)
        else:
            print colored("Fail", "red")
            sys.exit(1)

    def _create_objects(self):
        print colored("Creating activity %s" % self.factory.activity, "white")
        self.master.new_activity(self.factory.activity)

        print colored("Creating space_controller %s" % self.factory.space_controller, "white")
        self.master.new_space_controller(self.factory.space_controller)

        print colored("Creating live activity %s" % self.factory.live_activity, "white")
        self.master.new_live_activity(self.factory.live_activity)

        print colored("Creating live activity group %s" % self.factory.live_activity_group, "white")
        self.master.new_live_activity_group(self.factory.live_activity_group)

        print colored("Creating space %s" % self.factory.live_activity_group, "white")
        self.master.new_space(self.factory.live_activity_group)

     def _make_asserts(self)
         activity = self.master.get_activity(self.factory.activity)
         live_activity = self.master.get_live_activity(self.factory.live_activity)

