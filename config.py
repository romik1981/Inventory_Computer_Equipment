# config.py
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cartridge-secret-key-2026-change-me")
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data.db")
    BACKUP_DIR = os.path.join(os.path.dirname(__file__), "backups")
    MONTHS = ["Январь","Февраль","Март","Апрель","Май","Июнь",
              "Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"]
    MONTHS_SHORT = ["Янв","Фев","Мар","Апр","Май","Июн",
                    "Июл","Авг","Сен","Окт","Ноя","Дек"]
