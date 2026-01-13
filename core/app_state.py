from core.clients import ClientService
from core.services import ServiceManager
from core.scheduler import Scheduler


class AppState:
    clients = ClientService()
    services = ServiceManager()
    scheduler = Scheduler()
