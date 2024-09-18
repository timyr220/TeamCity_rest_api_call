import logging

class DeviceManager:
    def __init__(self, tb_manager):
        self.tb_manager = tb_manager

    def get_or_create_device(self, device_name, profile_id):
        """Receive or create a device."""
        return self.tb_manager.get_or_create_device(device_name, profile_id)
