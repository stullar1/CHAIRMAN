from data.db import get_connection
from data.models import Client


class ClientService:
    def __init__(self):
        self.conn = get_connection()

    def create(self, name, phone=""):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO clients (name, phone) VALUES (?, ?)", (name, phone))
        self.conn.commit()

    def all(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, phone, notes, no_show_count FROM clients")
        return [Client(*row) for row in cur.fetchall()]
