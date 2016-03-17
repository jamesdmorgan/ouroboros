from .fakes import with_fake_http
import httpretty
from expects import expect
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
