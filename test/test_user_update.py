import json
from .fakes import with_fake_http
import httpretty
from expects import expect, equal
from .matchers import have_json

class when_adding_a_user_to_a_group(with_fake_http):

    def given_an_existing_user(self):
        self.start_mocking_http()
        self.fake_response('/users/foo', file='user-foo.json')
        self.expect_call('/users/foo', httpretty.PUT)

    def because_we_add_the_user_to_a_group(self):
        self.client.users.addgroup("foo", "new-group")

    def it_should_put_the_correct_body(self):
        expect(httpretty.last_request()).to(
            have_json({
                "fullName": "bar",
                "groups": ["new-group"]
            }))


class when_adding_a_duplicate_group(with_fake_http):

    def given_an_existing_user(self):
        self.start_mocking_http()
        self.fake_response('/users/admin', file='user-admin.json')
        self.expect_call('/users/admin', httpretty.PUT)

    def because_we_add_the_user_to_a_group(self):
        self.client.users.addgroup("admin", "$admins")

    def it_should_put_the_correct_body(self):
        expect(httpretty.last_request()).to(
            have_json({
                "fullName": "Event Store Administrator",
                "groups": ["$admins"]
            }))


class when_adding_multiple_groups(with_fake_http):

    def given_an_existing_user(self):
        self.start_mocking_http()
        self.fake_response('/users/admin', file='user-admin.json')
        self.expect_call('/users/admin', httpretty.PUT)

    def because_we_add_the_user_to_a_group(self):
        self.client.users.addgroup("admin", "$admins", "devs", "people")

    def it_should_put_the_correct_body(self):
        body = httpretty.last_request().body.decode('Utf-8')
        posted_groups = json.loads(body)["groups"]

        expect(set(["$admins", "devs", "people"])).to(equal(
            set(posted_groups)))


class when_updating_the_name(with_fake_http):

    def given_an_existing_user(self):
        self.start_mocking_http()
        self.fake_response('/users/admin', file='user-admin.json')
        self.expect_call('/users/admin', httpretty.PUT)

    def because_we_add_the_user_to_a_group(self):
        self.client.users.rename("admin", "bob the mighty")

    def it_should_put_the_correct_body(self):
        expect(httpretty.last_request()).to(
            have_json({
                "fullName": "bob the mighty",
                "groups": ["$admins"]
            }))


class when_removing_a_user_from_a_group(with_fake_http):

    def given_an_existing_user(self):
        self.start_mocking_http()
        self.fake_response('/users/giddy', file='user-giddy.json')
        self.expect_call('/users/giddy', httpretty.PUT)

    def because_we_remove_a_group_from_the_user(self):
        self.client.users.removegroup('giddy', 'ops', 'cheeses')

    def it_should_put_the_correct_body(self):
        body = httpretty.last_request().body.decode('Utf-8')
        posted_groups = json.loads(body)["groups"]

        expect(set(["devs"])).to(equal(
            set(posted_groups)))


class when_changing_a_user_password(with_fake_http):

    def given_an_existing_user(self):
        self.start_mocking_http()
        self.fake_response('/users/giddy', file='user-giddy.json')
        self.expect_call('/users/giddy/command/reset-password', httpretty.POST)

    def because_we_change_the_password(self):
        self.client.users.setpassword('giddy', 'k1ng0fl1thuan14')

    def it_should_have_posted_the_correct_body(self):
        expect(httpretty.last_request()).to(have_json({
            'newPassword': 'k1ng0fl1thuan14'
        }))
