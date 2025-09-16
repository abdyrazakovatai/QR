# db.py
import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()  # локально подгрузит .env, на Render не нужен

class QRStatsDB:
    def __init__(self, db_url=None, qr_count=7):
        self.db_url = db_url or os.environ["DATABASE_URL"]
        self.qr_count = qr_count
        self._connect()
        self._init_db()
        self._init_default_qrs()

    def _connect(self):
        self.conn = psycopg2.connect(self.db_url)
        # будем возвращать dict вместо tuple
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def _init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS qr_stats (
                qr_id TEXT PRIMARY KEY,
                count INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def _init_default_qrs(self):
        """Заполняем таблицу дефолтными qr1..qrN, если их нет"""
        for i in range(1, self.qr_count + 1):
            qr_id = f"qr{i}"
            self.cursor.execute(
                "INSERT INTO qr_stats (qr_id, count) VALUES (%s, 0) ON CONFLICT DO NOTHING",
                (qr_id,)
            )
        self.conn.commit()

    def increment(self, qr_id: str):
        """Увеличить счётчик для qr_id"""
        self.cursor.execute(
            "UPDATE qr_stats SET count = count + 1 WHERE qr_id = %s RETURNING count",
            (qr_id,)
        )
        row = self.cursor.fetchone()
        if row:
            self.conn.commit()
            return row[0]
        return None

    def get_all(self) -> dict:
        """Вернуть все счётчики в виде словаря"""
        self.cursor.execute("SELECT qr_id, count FROM qr_stats ORDER BY qr_id")
        rows = self.cursor.fetchall()
        return {row["qr_id"]: row["count"] for row in rows}

    def reset(self, qr_id: str):
        """Сбросить счётчик конкретного QR"""
        self.cursor.execute(
            "UPDATE qr_stats SET count = 0 WHERE qr_id = %s RETURNING count",
            (qr_id,)
        )
        row = self.cursor.fetchone()
        if row:
            self.conn.commit()
            return row[0]
        return None