import logging
import threading
import time
from config_loader import ConfigLoader
from entities.teamcity_agent import TeamCityAgent
from entities.thingsboard_manager import ThingsBoardManager
from services.device_manager import DeviceManager
from services.telemetry_service import TelemetryService

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[
    logging.FileHandler("logs/main.log"), logging.StreamHandler()])

# Load configuration
teamcity_config = ConfigLoader.load_config('config/teamcity_agents.json')
tb_config = ConfigLoader.load_config('config/thingsboard.json')

TEAMCITY_URL = teamcity_config['url']
POLL_INTERVAL = teamcity_config['poll_interval']
THINGSBOARD_URL = tb_config['url']
THINGSBOARD_USERNAME = tb_config['username']
THINGSBOARD_PASSWORD = tb_config['password']


def monitor_teamcity(teamcity_agent, telemetry_service, profile_id):
    """Monitor TeamCity agents and send telemetry to ThingsBoard."""
    while True:
        agents = teamcity_agent.get_agents()

        # Ensure all devices are created before sending telemetry
        if telemetry_service.ensure_all_devices_created(agents, profile_id):
            logging.info("All devices created, starting telemetry transmission.")
            for agent in agents:
                telemetry_service.send_status_telemetry(agent, profile_id)
        else:
            logging.error("Not all devices were created, retrying after the interval.")

        # Pause before the next agent poll
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    # Initialize objects for working with TeamCity and ThingsBoard
    teamcity_agent = TeamCityAgent(TEAMCITY_URL)
    tb_manager = ThingsBoardManager(THINGSBOARD_URL, THINGSBOARD_USERNAME, THINGSBOARD_PASSWORD)
    device_manager = DeviceManager(tb_manager)
    telemetry_service = TelemetryService(tb_manager, device_manager)

    # Retrieve the "Agents" profile in ThingsBoard
    profile_id = tb_manager.get_profile_by_name(tb_config['profile_name'])
    if profile_id:
        logging.info(f"Profile '{tb_config['profile_name']}' found with ID {profile_id}.")
    else:
        logging.error(f"Failed to find profile '{tb_config['profile_name']}'. Exiting the program.")
        exit(1)

    # Start monitoring TeamCity agents
    monitor_thread = threading.Thread(target=monitor_teamcity,
                                      args=(teamcity_agent, telemetry_service, profile_id))
    monitor_thread.daemon = True  # Make the thread a daemon to exit with the program
    monitor_thread.start()

    # Infinite loop to keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Program terminated by user.")
