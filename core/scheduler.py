from __future__ import annotations
from datetime import datetime, timedelta, date
from typing import Any

from data.db import get_connection


class Scheduler:
    def __init__(self):
        self.conn = get_connection()

    def is_time_available(self, start: datetime, end: datetime) -> bool:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM appointments
            WHERE NOT (end_time <= ? OR start_time >= ?)
        """, (start.isoformat(), end.isoformat()))
        return cur.fetchone()[0] == 0

    def book(
        self,
        client_id: int,
        service_id: int,
        start: datetime,
        paid: bool = False,
        payment_method: str = "",
        notes: str = "",
    ) -> int | None:
        cur = self.conn.cursor()

        cur.execute(
            "SELECT duration_minutes, buffer_minutes FROM services WHERE id=?",
            (service_id,),
        )
        row = cur.fetchone()
        if not row:
            return None

        duration, buffer_minutes = row
        end = start + timedelta(minutes=int(duration) + int(buffer_minutes))

        if not self.is_time_available(start, end):
            return None

        cur.execute("""
            INSERT INTO appointments
            (client_id, service_id, start_time, end_time, paid, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            client_id,
            service_id,
            start.isoformat(),
            end.isoformat(),
            1 if paid else 0,
            payment_method or "",
            notes or "",
        ))
        self.conn.commit()
        return cur.lastrowid

    def list_for_date(self, day: date) -> list[dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT
                a.id,
                a.start_time,
                a.end_time,
                a.paid,
                a.payment_method,
                a.notes,
                c.id,
                c.name,
                c.phone,
                s.id,
                s.name,
                s.price,
                s.duration_minutes,
                s.buffer_minutes
            FROM appointments a
            JOIN clients c ON c.id = a.client_id
            JOIN services s ON s.id = a.service_id
            WHERE date(a.start_time) = ?
            ORDER BY a.start_time ASC
        """, (day.isoformat(),))

        rows = []
        for r in cur.fetchall():
            rows.append({
                "appt_id": r[0],
                "start": r[1],
                "end": r[2],
                "paid": bool(r[3]),
                "payment_method": r[4] or "",
                "appt_notes": r[5] or "",
                "client_id": r[6],
                "client_name": r[7],
                "client_phone": r[8] or "",
                "service_id": r[9],
                "service_name": r[10],
                "service_price": float(r[11]),
                "service_duration": int(r[12]),
                "service_buffer": int(r[13]),
            })
        return rows

    def toggle_paid(self, appt_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("SELECT paid FROM appointments WHERE id=?", (appt_id,))
        row = cur.fetchone()
        if not row:
            return
        new_val = 0 if int(row[0]) == 1 else 1
        cur.execute("UPDATE appointments SET paid=? WHERE id=?", (new_val, appt_id))
        self.conn.commit()

    def delete(self, appt_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM appointments WHERE id=?", (appt_id,))
        self.conn.commit()
