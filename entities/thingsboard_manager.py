import logging

from simplejson import load, dump, JSONDecodeError
from tb_rest_client.models.models_ce import Device
from tb_rest_client.rest import ApiException
from tb_rest_client.rest_client_pe import RestClientPE


class ThingsBoardManager:
    def __init__(self, tb_url, username, password):
        self.client = RestClientPE(base_url=tb_url)
        self.client.login(username=username, password=password)
        self.devices = self._load_devices()

    def _load_devices(self):
        """Load devices from devices.json file."""
        try:
            with open('devices.json', 'r') as file:
                return load(file)
        except (FileNotFoundError, JSONDecodeError):
            logging.info("The devices.json file was not found or is empty. Starting with an empty list.")
            return {}

    def _save_devices(self):
        """Save devices to devices.json file."""
        try:
            with open('data/devices.json', 'w') as file:
                dump(self.devices, file, indent=4)
            logging.info("Devices successfully saved to file.")
        except Exception as e:
            logging.error(f"Error saving devices: {e}")

    def get_or_create_device(self, device_name, profile_id):
        """Retrieve or create a device in ThingsBoard."""
        if device_name in self.devices:
            logging.info(f"Device {device_name} found in file.")
            if self.device_exists(self.devices[device_name]['id']):
                return self.devices[device_name]
            else:
                logging.warning(f"Device {device_name} was deleted. Creating a new one.")
        return self.create_device(device_name, profile_id)

    def create_device(self, device_name, profile_id):
        """Create a new device in ThingsBoard."""
        try:
            device = Device(name=device_name)
            created_device = self.client.save_device(device)
            device_token = self.client.get_device_credentials_by_device_id(created_device.id.id).credentials_id
            logging.info(f"Device {device_name} created with ID {created_device.id.id} and token {device_token}.")
            self.devices[device_name] = {'id': created_device.id.id, 'token': device_token}
            self._save_devices()
            return {'id': created_device.id.id, 'token': device_token}
        except ApiException as e:
            logging.error(f"Error creating device {device_name}: {e}")
            return None

    def device_exists(self, device_id):
        """Check if the device exists in ThingsBoard."""
        try:
            self.client.get_device_by_id(device_id)
            return True
        except ApiException:
            return False

    def send_telemetry(self, device_token, telemetry):
        """Send telemetry to the device."""
        try:
            # Use the post_telemetry method to send telemetry
            self.client.post_telemetry(device_token, telemetry)
            logging.info(f"Telemetry successfully sent for token {device_token}.")
        except ApiException as e:
            logging.error(f"Error sending telemetry: {e}")

    def get_profile_by_name(self, profile_name):
        """Retrieve a device profile by name."""
        try:
            profiles = self.client.get_device_profiles(page_size=100, page=0)
            for profile in profiles.data:
                if profile.name == profile_name:
                    return profile.id.id
            logging.error(f"Profile with name '{profile_name}' not found.")
            return None
        except ApiException as e:
            logging.error(f"Error retrieving profile {profile_name}: {e}")
            return None
