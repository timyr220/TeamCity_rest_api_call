import logging
import xml.etree.ElementTree as ET

import requests

# TODO: Optimize import, to avoid extra imported function that not used in code


class TeamCityAgent:
    def __init__(self, url):
        self.url = url


    def get_agents(self):
        """Get the list of TeamCity agents and their statuses."""
        try:
            response = requests.get(self.url)
            logging.info(f"TeamCity response status code: {response.status_code}")
            logging.info(f"TeamCity response content: {response.text}")
            response.raise_for_status()

            # Parsing the XML response
            root = ET.fromstring(response.text)
            agents = []
            for agent in root.findall('agent'):
                agent_name = agent.attrib.get('name')
                agent_href = agent.attrib.get('href')

                # Make an additional request to obtain the agent's status
                agent_detail = self.get_agent_detail(agent_href)
                if agent_detail:
                    is_connected = agent_detail.get('connected', False)
                    logging.info(f"Agent {agent_name} status: {'Connected' if is_connected else 'Disconnected'}")
                    agents.append({'name': agent_name, 'connected': is_connected})
                else:
                    logging.warning(f"Failed to retrieve details for agent {agent_name}")
                    agents.append({'name': agent_name, 'connected': False})

            logging.info(f"Retrieved {len(agents)} agents.")
            return agents
        except requests.RequestException as e:
            logging.error(f"Error while fetching TeamCity agents: {e}")
            return []
        except ET.ParseError as e:
            logging.error(f"Error parsing XML response: {e}")
            return []


    def get_agent_detail(self, href):
        """Retrieve detailed information about the agent's status."""
        try:
            # Add base URL to relative path
            detail_url = f"https://builds.thingsboard.io{href}"
            response = requests.get(detail_url)
            logging.info(f"Requesting agent details by URL {detail_url}: status {response.status_code}")
            logging.info(f"Response content: {response.text}")  # Logging the response

            response.raise_for_status()

            # Parsing XML to get the status
            root = ET.fromstring(response.text)
            # Assuming the agent's status is in the 'connected' attribute
            is_connected = root.attrib.get('connected', 'false').lower() == 'true'
            return {'connected': is_connected}
        except requests.RequestException as e:
            logging.error(f"Error while fetching agent details from {href}: {e}")
            return None
