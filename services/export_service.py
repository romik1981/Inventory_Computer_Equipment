import csv
import os
from datetime import datetime
from config import Config


class ExportService:
    @staticmethod
    def export_to_csv(data, headers, filename_prefix="export"):
        """
        Экспортирует данные в CSV-файл
        :param data: Список словарей или кортежей
        :param headers: Заголовки столбцов
        :param filename_prefix: Префикс имени файла
        :return: Путь к файлу
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = os.path.join(Config.BACKUP_DIR, filename)

        os.makedirs(Config.BACKUP_DIR, exist_ok=True)

        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in data:
                if isinstance(row, dict):
                    writer.writerow([row.get(h, "") for h in headers])
                else:
                    writer.writerow(row)

        return filepath

    @staticmethod
    def export_printers():
        from models.printer import Printer
        printers = Printer.get_all(active_only=True)
        headers = ["ID", "Этаж", "Отдел", "Модель", "Картридж", "Ресурс стр.", "Цена", "Примечание"]
        data = [
            (
                p["id"],
                p["floor"],
                p["dept"],
                p["model"],
                p["cartridge"],
                p["monthly_rate"],
                p["price"],
                p["note"]
            )
            for p in printers
        ]
        return ExportService.export_to_csv(data, headers, "printers")

    @staticmethod
    def export_records():
        from models.record import Record
        records = Record.get_all_with_printers()
        headers = ["Дата", "Модель принтера", "Отдел", "Тип картриджа", "Израсходовано тонера (г)", "Напечатано страниц"]
        data = [
            (
                r["date"],
                r["printer_model"],
                r["department"],
                r["cartridge_type"],
                r["toner_used"],
                r["pages_printed"]
            )
            for r in records
        ]
        return ExportService.export_to_csv(data, headers, "records")

    @staticmethod
    def export_stock():
        from models.stock import Stock
        items = Stock.get_all()
        headers = ["Наименование", "Категория", "Количество", "Цена за ед.", "Общая цена", "Примечание"]
        data = [
            (
                i["item_name"],
                i["category"],
                i["quantity"],
                i["unit_price"],
                i["total_price"],
                i["note"]
            )
            for i in items
        ]
        return ExportService.export_to_csv(data, headers, "stock")
