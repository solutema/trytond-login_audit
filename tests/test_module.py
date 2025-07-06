
from trytond.tests.test_tryton import ModuleTestCase


class LoginAuditTestCase(ModuleTestCase):
    "Test Login Audit module"
    module = 'login_audit'


del ModuleTestCase
