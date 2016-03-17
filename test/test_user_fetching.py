from expects import expect, equal, be_false
from .fakes import with_fake_http


class when_fetching_an_existing_user(with_fake_http):

    def given_an_existing_user(self):
        self.start_mocking_http()
        self.fake_response("/users/foo", file="user-foo.json")

    def because_we_get_a_user(self):
        self.user = self.client.users.get('foo')

    def it_should_have_the_username(self):
        expect(self.user.login_name).to(equal('foo'))

    def it_should_have_the_full_name(self):
        expect(self.user.full_name).to(equal('bar'))

    def it_should_have_an_edit_uri(self):
        expect(self.user.links['edit']).to(equal(
            'http://fake-eventstore.com:12345/users/foo'))

    def it_should_have_a_delete_uri(self):
        expect(self.user.links['delete']).to(equal(
            'http://fake-eventstore.com:12345/users/foo'))

    def it_should_have_a_pw_reset_uri(self):
        expect(self.user.links['reset-password']).to(equal(
            'http://fake-eventstore.com:12345/users/foo/command/reset-password'))

    def it_should_have_a_disable_uri(self):
        expect(self.user.links['disable']).to(equal(
            'http://fake-eventstore.com:12345/users/foo/command/disable'))

    def it_should_have_a_change_pw_uri(self):
        expect(self.user.links['change-password']).to(equal(
            'http://fake-eventstore.com:12345/users/foo/command/change-password'))

    def it_should_not_be_disabled(self):
        expect(self.user.disabled).to(be_false)
