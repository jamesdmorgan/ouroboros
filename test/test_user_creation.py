import httpretty
from expects import expect
from .fakes import with_fake_http
from ouroboros.client import Client
from .matchers import have_posted_to, have_json
import re


class when_creating_a_new_user(with_fake_http):

    def because_we_create_a_new_user(self):
        self.start_mocking_http()
        self.expect_call('/users/', httpretty.POST)
        self.client.users.create("bob", "password")

    def it_should_have_the_correct_request_body(self):
        expect(httpretty.last_request()).to(
            have_json({
                "loginName": "bob",
                "fullName": "bob",
                "password": "password",
                "groups": []
            }))


class when_creating_a_user_with_all_optional_info(with_fake_http):

    def because_we_create_a_user(self):
        self.start_mocking_http()
        self.expect_call('/users/', httpretty.POST)
        self.client.users.create("foo", "bar",
                                 fullname="Ramrod McTavish",
                                 groups=["devs"])

    def it_should_have_the_correct_request_body(self):
        expect(httpretty.last_request()).to(
            have_json({
                "loginName": "foo",
                "fullName": "Ramrod McTavish",
                "password": "bar",
                "groups": ["devs"]}))
