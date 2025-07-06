from trytond.pool import Pool
from . import session

def register():
    Pool.register(
        session.Session,
        session.SessionLog,
        module='login_audit', type_='model')
