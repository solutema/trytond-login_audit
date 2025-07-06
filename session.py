from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from datetime import timedelta, datetime, time, date
from dateutil.relativedelta import relativedelta
from trytond.model import ModelSQL, ModelView, fields
from trytond.i18n import gettext
import pytz

def get_client_ip():
    """
    Intenta detectar la IP del cliente desde múltiples fuentes.
    Compatible con WSGI, proteus, consola, y RPC.
    """
    context = Transaction().context

    # 1. IP desde WSGI (middleware que puso remote_addr)
    ip = context.get('remote_addr')

    # 2. IP desde contexto del RPC manual
    if not ip:
        ip = context.get('ip') or context.get('client_ip')

    # 3. Fallback: 127.0.0.1 (por consola o pruebas)
    return ip or '127.0.0.1'

class Session(metaclass=PoolMeta):
    __name__ = 'ir.session'

    @classmethod
    def create(cls, vlist):
        sessions = super().create(vlist)

        SessionLog = Pool().get('ir.session.log')
        logs = []

        for session in sessions:
            login_datetime = datetime.utcnow()
            ip = get_client_ip()

            user_login = user_name = None
            if session.create_uid:
                user_login = session.create_uid.login
                user_name = session.create_uid.name

            logs.append({
                'session_key': session.key,
                'user_login': user_login,
                'user_name': user_name,
                'login_datetime': login_datetime,
                'ip_address': ip,
            })

        SessionLog.create(logs)
        return sessions

    @classmethod
    def remove(cls, key, domain=None):
        domain = [('key', '=', key), domain or []]
        sessions = cls.search(domain)
        if not sessions:
            return
        session, = sessions

        now = datetime.utcnow()

        SessionLog = Pool().get('ir.session.log')
        logs = SessionLog.search([
            ('session_key', '=', session.key),
            ('logout_datetime', '=', None),
        ], limit=1)

        if logs:
            log = logs[0]
            login_datetime = log.login_datetime or now

            delta = relativedelta(now, login_datetime)
            log.logout_datetime = now
            log.duration = f"{delta.hours}h {delta.minutes}m {delta.seconds}s"
            log.save()

        return session.create_uid.login


class SessionLog(ModelSQL, ModelView):
    "Session Log"
    __name__ = 'ir.session.log'

    session_key = fields.Char("Session Key", readonly=True)
    user_login = fields.Char("User", readonly=True)
    user_name = fields.Char("Name", readonly=True)
    login_datetime = fields.DateTime("Login DateTime", readonly=True)
    logout_datetime = fields.DateTime("Logout DateTime", readonly=True)
    duration = fields.Char("Duration", readonly=True)
    ip_address = fields.Char("IP Address", readonly=True)

    # Campos derivados (fecha + hora en 12h)
    login_date = fields.Function(fields.Date("Login Date"), 'get_login_date')
    login_time = fields.Function(fields.Time("Login Time", format='%I:%M %p'), 'get_login_time')
    logout_date = fields.Function(fields.Date("Logout Date"), 'get_logout_date')
    logout_time = fields.Function(fields.Time("Logout Time", format='%I:%M %p'), 'get_logout_time')

    def get_login_date(self, name):
        return self.login_datetime.date() if self.login_datetime else None

    def get_login_time(self, name):
        if self.login_datetime:
            tz = pytz.timezone('America/Santo_Domingo')
            dt = self.login_datetime.replace(tzinfo=pytz.utc).astimezone(tz)
            return dt.time()
        return None

    def get_logout_date(self, name):
        return self.logout_datetime.date() if self.logout_datetime else None

    def get_logout_time(self, name):
        if self.logout_datetime:
            tz = pytz.timezone('America/Santo_Domingo')
            dt = self.logout_datetime.replace(tzinfo=pytz.utc).astimezone(tz)
            return dt.time()
        return None
