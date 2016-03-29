from ouroboros.client import Acl
from expects import expect, equal

class when_comparing_two_empty_acls:

    def they_should_be_equal(self):
        expect(Acl.empty()).to(equal(Acl.empty()))
