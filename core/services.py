from data.db import get_connection
from data.models import Service


class ServiceManager:
    def __init__(self):
        self.conn = get_connection()

    def create(self, name, price, duration, buffer=0):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO services VALUES (NULL, ?, ?, ?, ?)",
            (name, price, duration, buffer),
        )
        self.conn.commit()

    def all(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, price, duration_minutes, buffer_minutes FROM services")
        return [Service(*row) for row in cur.fetchall()]
