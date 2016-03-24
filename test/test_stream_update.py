from ouroboros.client import Acl, NotFoundException
from expects import expect, be_a
import httpretty
from .fakes import with_fake_http
from .matchers import have_json


class when_adding_an_acl_to_an_existing_stream(with_fake_http):

    def given_an_existing_stream_with_no_metadata(self):
        self.start_mocking_http()
        self.fake_response('/streams/my-stream/metadata', status=200, body='{}')
        self.expect_call('/streams/my-stream/metadata', httpretty.POST)

    def because_we_set_the_acl(self):
        self.client.streams.set_acl('my-stream',
                                    Acl(write=['ops'], read=['devs', 'ops', 'qa']),
                                    eventid="foo"
                                    )

    def it_should_post_the_correct_acl(self):
        expect(httpretty.last_request()).to(have_json([{
            "eventId": "foo",
            "eventType": "settings",
            "data": {
                "$acl": {
                    "$r": ["devs", "ops", "qa"],
                    "$w": ["ops"]
                }
            }
        }]))


class when_updating_the_acl_of_a_stream(with_fake_http):

   def given_a_stream_with_an_acl(self):
       self.start_mocking_http()
       self.expect_call('/streams/my-stream/metadata', httpretty.POST)
       self.fake_response('/streams/my-stream/metadata', status=200,
                          body = """
                          {
                             "$acl" : {
                                "$w"  : "greg",
                                "$r"  : ["greg", "john"],
                                "$d"  : "$admins",
                                "$mw" : "$admins",
                                "$mr" : "$admins"
                             }
                          }""")

   def because_we_update_the_acl(self):
        self.client.streams.set_acl('my-stream',
                                    Acl(read=['greg'], write=[]),
                                    eventid="foo")

   def it_should_post_the_correct_body(self):
        expect(httpretty.last_request()).to(have_json([{
            "eventId": "foo",
            "eventType": "settings",
            "data": {
                "$acl": {
                    "$w": [],
                    "$r": ["greg"]
                }
            }
        }]))



class when_updating_the_acl_of_a_nonexistent_stream(with_fake_http):

    def given_the_absence_of_a_stream(self):
       self.start_mocking_http()
       self.expect_call('/streams/my-stream/metadata', httpretty.POST)
       self.fake_response('/streams/missing-stream/metadata', status=404)

    def because_we_try_to_update_the_stream(self):
        try:
            self.client.streams.set_acl('missing-stream', Acl())
        except Exception as e:
            self.exception = e

    def it_should_raise_StreamNotFound(self):
        expect(self.exception).to(be_a(NotFoundException))


class when_granting_permissions_to_a_stream(with_fake_http):

    def given_a_stream_with_an_acl(self):
       self.start_mocking_http()
       self.expect_call('/streams/my-stream/metadata', httpretty.POST)
       self.fake_response('/streams/my-stream/metadata', status=200,
                          body = """
                          {
                             "$acl" : {
                                "$w"  : "greg",
                                "$r"  : ["greg", "john"],
                                "$d"  : "$admins",
                                "$mw" : "$admins",
                                "$mr" : "$admins"
                             }
                          }""")

    def because_we_grant_permissions(self):
        self.client.streams.grant('my-stream',Acl(
                                  read=['fred'],
                                  write=['fred'],
                                  delete=['fred'],
                                  metadata_read=['fred']),
                                  eventid='foo')


    def it_should_post_the_correct_body(self):
        expect(httpretty.last_request()).to(have_json([{
            "eventId": "foo",
            "eventType": "settings",
            "data": {
                "$acl": {
                    "$w": ['fred', 'greg'],
                    "$r": ['fred', "greg", 'john'],
                    "$d": ["$admins", 'fred'],
                    "$mw": ["$admins"],
                    "$mr": ["$admins", 'fred']
                }
            }
        }]))


class when_revoking_permissions_from_a_stream(with_fake_http):

    def given_a_stream_with_an_acl(self):
       self.start_mocking_http()
       self.expect_call('/streams/my-stream/metadata', httpretty.POST)
       self.fake_response('/streams/my-stream/metadata', status=200,
                          body = """
                          {
                             "$acl" : {
                                "$w"  : "greg",
                                "$r"  : ["greg", "john"],
                                "$d"  : "$admins",
                                "$mw" : "$admins",
                                "$mr" : "$admins"
                             }
                          }""")

    def because_we_grant_permissions(self):
        self.client.streams.revoke('my-stream',Acl(
                                  read=['greg'],
                                  write=['greg']),
                                  eventid='foo')


    def it_should_post_the_correct_body(self):
        expect(httpretty.last_request()).to(have_json([{
            "eventId": "foo",
            "eventType": "settings",
            "data": {
                "$acl": {
                    "$w": [],
                    "$r": ['john'],
                    "$d": ["$admins"],
                    "$mw": ["$admins"],
                    "$mr": ["$admins"]
                }
            }
        }]))
