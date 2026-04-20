from models.toner import Toner
from models.printer import Printer


class CompatibilityService:
    @staticmethod
    def is_compatible(toner_id, printer_id):
        """
        Проверяет, совместим ли тонер с принтером
        """
        with Toner.get_by_id(toner_id) as toner, Printer.get_by_id(printer_id) as printer:
            if not toner or not printer:
                return False
            # Простое сравнение: cartridge (принтера) должен быть в compatible_printers (тонера)
            return printer["cartridge"] in toner["compatible_printers"]

    @staticmethod
    def get_compatible_printers(toner_id):
        """
        Возвращает список принтеров, совместимых с тонером
        """
        toner = Toner.get_by_id(toner_id)
        if not toner:
            return []

        compatible_cartridges = [c.strip() for c in toner["compatible_printers"].split(",")]
        all_printers = Printer.get_all(active_only=True)
        return [p for p in all_printers if p["cartridge"] in compatible_cartridges]

    @staticmethod
    def get_compatible_toners(printer_id):
        """
        Возвращает список тонеров, совместимых с принтером
        """
        printer = Printer.get_by_id(printer_id)
        if not printer:
            return []

        cartridge_model = printer["cartridge"]
        all_toners = Toner.get_all()
        compatible = []
        for toner in all_toners:
            comp_list = [c.strip() for c in toner["compatible_printers"].split(",")]
            if cartridge_model in comp_list:
                compatible.append(toner)
        return compatible
