import logging

class TelemetryService:
    def __init__(self, tb_manager, device_manager):
        self.tb_manager = tb_manager
        self.device_manager = device_manager

    def ensure_all_devices_created(self, agents, profile_id):
        """Проверяем, что все устройства созданы."""
        for agent in agents:
            if not self.device_manager.get_or_create_device(agent['name'], profile_id):
                logging.error(f"Не удалось создать устройство для агента {agent['name']}.")
                return False
        return True

    def send_status_telemetry(self, agent, profile_id):
        """Отправляем статус телеметрии."""
        device = self.device_manager.get_or_create_device(agent['name'], profile_id)
        if device:
            telemetry = {'online': 1 if agent['connected'] else 0}
            self.tb_manager.send_telemetry(device['token'], telemetry)
        else:
            logging.error(f"Не удалось найти устройство для агента {agent['name']}.")
