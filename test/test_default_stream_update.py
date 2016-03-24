from .matchers import have_json
from .fakes import with_fake_http
from expects import expect
import httpretty
from ouroboros.client import Acl


class when_creating_the_user_default_acl(with_fake_http):

    def given_that_there_is_no_default_acl(self):
        self.start_mocking_http()
        self.fake_response('/streams/$settings', status=404)
        self.expect_call('/streams/$settings', httpretty.POST)

    def because_we_call_set_acl(self):
        self.client.streams.set_default_user_acl(Acl(
            read=['bob']
        ), eventid="foo")

    def it_should_post_the_correct_body(self):
        expect(httpretty.last_request()).to(have_json([
        {
            "eventId": "foo",
            "eventType": "settings",
            "data":
            {
                "$userStreamAcl": {
                    "$r": ["bob"],
                    "$w": [],
                    "$d": [],
                    "$mr": [],
                    "$mw": []
                },
                "$systemStreamAcl": {
                    "$r": ["$admins"],
                    "$w": ["$admins"],
                    "$d": ["$admins"],
                    "$mr":[ "$admins"],
                    "$mw": ["$admins"]
                }
            }
        }]))
