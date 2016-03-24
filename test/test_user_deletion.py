from .fakes import with_fake_http
import httpretty
from expects import expect, be_a
from .matchers import have_posted_to

from ouroboros.client import NotFoundException

class when_deleting_a_user(with_fake_http):

    def given_a_user(self):
        self.start_mocking_http()
        self.expect_call('/users/foo', httpretty.DELETE)
        self.fake_response("/users/foo", file="user-foo.json")

    def because_we_delete_a_user(self):
        self.client.users.delete("foo")

    def it_should_delete_the_user(self):
        expect(httpretty.last_request()).to(
            have_posted_to("/users/foo", method=httpretty.DELETE))


class  when_we_try_to_delete_a_non_existent_user(with_fake_http):

    def given_a_client(self):
        self.start_mocking_http()
        self.fake_response('/users/foo', status=404)

    def because_we_delete_the_user(self):
        try:
            self.client.users.delete('foo')
        except Exception as e:
            self.exception = e

    def it_should_raise_user_not_found(self):
        expect(self.exception).to(be_a(NotFoundException))
