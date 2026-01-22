from core.clients import ClientService
from core.services import ServiceManager
from core.scheduler import Scheduler


class AppState:
    client_service = ClientService()
    service_manager = ServiceManager()
    scheduler = Scheduler()
