"""
Audit Logger Class
"""
import uuid
import sqlalchemy as db
from flask import current_app
from .ConnectionString import ConnectionString


class AuditLogger:
    def __init__(self):
        self.engine = db.create_engine(ConnectionString("wgdashboard_log"))
        self.metadata = db.MetaData()
        self.auditLogTable = db.Table(
            "AuditLog",
            self.metadata,
            db.Column("LogID", db.String(255), nullable=False, primary_key=True),
            db.Column(
                "LogDate",
                (db.DATETIME if "sqlite:///" in ConnectionString("wgdashboard") else db.TIMESTAMP),
                server_default=db.func.now(),
            ),
            db.Column("Actor", db.String(255)),
            db.Column("IP", db.String(255)),
            db.Column("Method", db.String(16)),
            db.Column("Path", db.String(255)),
            db.Column("StatusCode", db.Integer),
            db.Column("Result", db.String(32)),
            db.Column("Message", db.Text),
            extend_existing=True,
        )
        self.metadata.create_all(self.engine)

    def log(self, Actor: str = "", IP: str = "", Method: str = "", Path: str = "",
            StatusCode: int = 200, Result: str = "", Message: str = "") -> bool:
        try:
            with self.engine.begin() as conn:
                conn.execute(
                    self.auditLogTable.insert().values(
                        LogID=str(uuid.uuid4()),
                        Actor=Actor,
                        IP=IP,
                        Method=Method,
                        Path=Path,
                        StatusCode=StatusCode,
                        Result=Result,
                        Message=Message
                    )
                )
            return True
        except Exception as e:
            current_app.logger.error("Audit Log Error", e)
            return False

    def get_logs(self, limit: int = 200):
        try:
            with self.engine.begin() as conn:
                result = conn.execute(
                    db.select(self.auditLogTable).order_by(self.auditLogTable.c.LogDate.desc()).limit(limit)
                )
                return [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            current_app.logger.error("Audit Log Fetch Error", e)
            return []
