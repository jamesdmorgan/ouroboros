from .fakes import with_fake_http
import httpretty
from expects import expect
from .matchers import have_json


class when_creating_a_new_stream(with_fake_http):

    def given_a_client(self):
        self.start_mocking_http()
        self.expect_call('/streams/my-stream/metadata', httpretty.POST)

    def because_we_create_a_new_stream(self):
        self.client.streams.create('my-stream', eventid="foo")

    def it_should_post_metadata(self):
        expect(httpretty.last_request()).to(have_json([{
            "eventId": "foo",
            "eventType": "$user-updated"
        }]))


class when_creating_a_stream_with_some_acls(with_fake_http):

    def given_a_client(self):
        self.start_mocking_http()
        self.expect_call('/streams/my-stream/metadata', httpretty.POST)

    def because_we_create_a_new_stream(self):
        self.client.streams.create('my-stream',
                                   eventid="foo",
                                   read=['devs', 'ops', '$admins'],
                                   write=['ops', '$admins'],
                                   delete=['$admins'],
                                   metadata_read=['$all'],
                                   metadata_write=['$admins']
                                   )

    def it_should_post_metadata(self):
        expect(httpretty.last_request()).to(have_json([{
            "eventId": "foo",
            "eventType": "$user-updated",
            "$acl": {
                "$r": ['devs', 'ops', '$admins'],
                "$w": ['ops', '$admins'],
                "$d": ['$admins'],
                "$mr": ['$all'],
                "$mw": ['$admins']
            }
        }]))
