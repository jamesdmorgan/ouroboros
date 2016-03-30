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
        self.client.user_acl.set_acl(Acl(
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


class when_creating_the_system_default_acl(with_fake_http):

    def given_that_there_is_no_default_acl(self):
        self.start_mocking_http()
        self.fake_response('/streams/$settings', status=404)
        self.expect_call('/streams/$settings', httpretty.POST)

    def because_we_call_set_acl(self):
        self.client.system_acl.set_acl(Acl(
            read=['fred'],
            write=['fred']
        ), eventid="foo")

    def it_should_post_the_correct_body(self):
        expect(httpretty.last_request()).to(have_json([
        {
            "eventId": "foo",
            "eventType": "settings",
            "data":
            {
                "$userStreamAcl": {
                    "$r": ["$all"],
                    "$w": ["$all"],
                    "$d": ["$all"],
                    "$mr": ["$all"],
                    "$mw": ["$all"]
                },
                "$systemStreamAcl": {
                    "$r": ["fred"],
                    "$w": ["fred"],
                    "$d": [],
                    "$mr":[],
                    "$mw": []
                }
            }
        }]))


class when_granting_additional_permissions_on_the_user_default_acl(with_fake_http):

    def given_a_default_acl(self):
        self.start_mocking_http()
        self.fake_response('/streams/$settings', file='settings-stream.js')
        self.fake_response('/streams/$settings/6', file='settings.json')
        self.expect_call('/streams/$settings', httpretty.POST)

    def because_we_grant_additional_permissions(self):
        self.client.user_acl.grant(Acl(
            read=['giddy', 'kevin']
        ), eventid='foo')

    def it_should_post_the_correct_body(self):
        expect(httpretty.last_request()).to(have_json([
        {
            "eventId": "foo",
            "eventType": "settings",
            "data":
            {
                "$userStreamAcl": {
                    "$r": ["$all", "giddy", "kevin"],
                    "$w": ["ouro"],
                    "$d": ["ouro"],
                    "$mr": ["ouro"],
                    "$mw": ["ouro"]
                },
                "$systemStreamAcl": {
                    "$r": ["$admins", "ouro"],
                    "$w": ["$admins"],
                    "$d": ["$admins"],
                    "$mr":["$admins"],
                    "$mw": ["$admins"]
                }
            }
        }]))


class when_revoking_permissions_from_the_user_acl(with_fake_http):

    def given_a_default_acl(self):
        self.start_mocking_http()
        self.fake_response('/streams/$settings', file='settings-stream.js')
        self.fake_response('/streams/$settings/6', file='settings.json')
        self.expect_call('/streams/$settings', httpretty.POST)

    def because_we_revoke_write_permissions(self):
        self.client.user_acl.revoke(Acl(
            write=['ouro']
        ), eventid='foo')

    def it_should_post_the_correct_body(self):
        expect(httpretty.last_request()).to(have_json([
        {
            "eventId": "foo",
            "eventType": "settings",
            "data":
            {
                "$userStreamAcl": {
                    "$r": ["$all"],
                    "$w": [],
                    "$d": ["ouro"],
                    "$mr": ["ouro"],
                    "$mw": ["ouro"]
                },
                "$systemStreamAcl": {
                    "$r": ["$admins", "ouro"],
                    "$w": ["$admins"],
                    "$d": ["$admins"],
                    "$mr":["$admins"],
                    "$mw": ["$admins"]
                }
            }
        }]))


class when_granting_additional_permissions_on_the_system_default_acl(with_fake_http):

    def given_a_default_acl(self):
        self.start_mocking_http()
        self.fake_response('/streams/$settings', file='settings-stream.js')
        self.fake_response('/streams/$settings/6', file='settings.json')
        self.expect_call('/streams/$settings', httpretty.POST)

    def because_we_grant_additional_permissions(self):
        self.client.system_acl.grant(Acl(
            write=['giddy', 'kevin']
        ), eventid='foo')

    def it_should_post_the_correct_body(self):
        expect(httpretty.last_request()).to(have_json([
        {
            "eventId": "foo",
            "eventType": "settings",
            "data":
            {
                "$userStreamAcl": {
                    "$r": ["$all"],
                    "$w": ["ouro"],
                    "$d": ["ouro"],
                    "$mr": ["ouro"],
                    "$mw": ["ouro"]
                },
                "$systemStreamAcl": {
                    "$r": ["$admins", "ouro"],
                    "$w": ["$admins", "giddy", "kevin"],
                    "$d": ["$admins"],
                    "$mr":["$admins"],
                    "$mw": ["$admins"]
                }
            }
        }]))


class when_revoking_permissions_from_the_system_acl(with_fake_http):

    def given_a_default_acl(self):
        self.start_mocking_http()
        self.fake_response('/streams/$settings', file='settings-stream.js')
        self.fake_response('/streams/$settings/6', file='settings.json')
        self.expect_call('/streams/$settings', httpretty.POST)

    def because_we_revoke_write_permissions(self):
        self.client.system_acl.revoke(Acl(
            read=['ouro']
        ), eventid='foo')

    def it_should_post_the_correct_body(self):
        expect(httpretty.last_request()).to(have_json([
        {
            "eventId": "foo",
            "eventType": "settings",
            "data":
            {
                "$userStreamAcl": {
                    "$r": ["$all"],
                    "$w": ["ouro"],
                    "$d": ["ouro"],
                    "$mr": ["ouro"],
                    "$mw": ["ouro"]
                },
                "$systemStreamAcl": {
                    "$r": ["$admins"],
                    "$w": ["$admins"],
                    "$d": ["$admins"],
                    "$mr":["$admins"],
                    "$mw": ["$admins"]
                }
            }
        }]))



