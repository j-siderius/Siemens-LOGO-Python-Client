# Siemens LOGO PLC controller Python interface
# Using unofficial API calls to LOGO Web Interface
# Adapted to Python from https://github.com/jankeymeulen/siemens-logo-rest

import re
import zlib
import random
import requests
import xml.etree.ElementTree as ET


class LOGO:
    """
    A class to interface with the Siemens LOGO PLC controller using its unofficial API.

    This class allows for the retrieval and setting of variables on the LOGO PLC.
    It handles the authentication process and manages the communication with the LOGO Web Interface.
    """

    variableTypes = {
        "VM": 132,   # Variable Memory
        "I": 129,    # Inputs
        "NetI": 16,  # Network Inputs
        "Q": 130,    # Outputs
        "NetQ": 17,  # Network Outputs
        "M": 131,    # Memory
        "AI": 18,    # Analog Inputs
        "NetAI": 21, # Network Analog Inputs
        "AQ": 19,    # Analog Outputs
        "NetAQ": 22, # Network Analog Outputs
        "AM": 20     # Analog Memory
    }

    def __init__(self, ip_address: str, webuser_password: str = 'webuser'):
        """
        Initializes the LOGO connection and calculates the security key to access API calls.

        :param ip_address: str
            The IP address of the Siemens LOGO Web Interface, which can be set using the LOGO menu or SoftComfort software.

        :param webuser_password: str
            The configured password for the WebUser account of the Siemens LOGO Web Interface.
            Defaults to 'webuser'.
        """
        self.url = f'http://{ip_address}/AJAX'

        # Generate random values for the security challenge
        a1 = random.randint(0, 2 ** 32 - 1)
        a2 = random.randint(0, 2 ** 32 - 1)
        b1 = random.randint(0, 2 ** 32 - 1)
        b2 = random.randint(0, 2 ** 32 - 1)

        headers = {'Security-Hint': 'p'}
        body = f'UAMCHAL:3,4,{a1},{a2},{b1},{b2}'

        # Send initial challenge request to LOGO
        response = requests.post(self.url, headers=headers, data=body)

        ret = response.text.split(",")
        if len(ret) == 3 and ret[0] == "700":
            login_security_hint = ret[1]
            server_challenge = int(ret[2])  # Convert to uint32

            # Create password token for login
            pw_token = (webuser_password + '+' + str(server_challenge)).encode('utf-8')[:32].decode('utf-8', 'ignore')

            # Calculate CRC32 of the password token
            crc32_pw_token = zlib.crc32(pw_token.encode('utf-8')) & 0xFFFFFFFF  # Ensure it's uint32
            login_pw_token = crc32_pw_token ^ server_challenge

            # Calculate the server challenge for login
            login_server_challenge = a1 ^ a2 ^ b1 ^ b2 ^ server_challenge

            headers = {'Security-Hint': login_security_hint}
            body = f'UAMLOGIN:Web User,{login_pw_token},{login_server_challenge}'

            # Send login request to LOGO
            response = requests.post(self.url, headers=headers, data=body)

            ret = response.text.split(",")
            if len(ret) == 2 and ret[0] == "700":
                self.security_code = ret[1]  # Store the security code for future requests
            else:
                print(
                    f'LOGOError: Webserver did not return expected status code 700, but instead returned status code {ret[0]}')
        else:
            print(
                f'LOGOError: Webserver did not return expected status code 700, but instead returned status code {ret[0]}')

    def getVariable(self, variable: str) -> str:
        """
        Retrieves the value of a specified variable from the LOGO PLC.

        :param variable: str
            The variable to retrieve, formatted as 'TypeAddress' (e.g., 'VM0', 'I1').

        :return: str
            The value of the specified variable, or None if the variable type is unsupported.
        """
        variableType, variableAddress = re.split(r'(?=\d)', variable)
        if variableType in self.variableTypes.keys():
            response = requests.post(self.url,
                                     headers={'Security-Hint': self.security_code},
                                     data=f'GETVARS:v1,{self.variableTypes[variableType]},0,{variableAddress},1,1')
            # Parse the XML response to extract the variable value
            return ET.fromstring(response.text).find('r').get('v')
        else:
            print(f'VariableError: variable variableType "{variableType}" is not supported.')
            return None  # Return None if the variable type is unsupported

    def setVariable(self, variable: str, value: str) -> None:
        """
        Sets the value of a specified variable on the LOGO PLC.

        :param variable: str
            The variable to set, formatted as 'TypeAddress' (e.g., 'VM0', 'Q1').

        :param value: str
            The value to assign to the specified variable.
        """
        variableType, variableAddress = re.split(r'(?=\d)', variable)
        if variableType in self.variableTypes.keys():
            # Send the command to set the variable value
            requests.post(self.url,
                          headers={'Security-Hint': self.security_code},
                          data=f'SETVARS:v0,{self.variableTypes[variableType]},0,{variableAddress},1,1,{value}')
        else:
            print(f'VariableError: variable variableType "{variableType}" is not supported.')


if __name__ == "__main__":
    # Example usage of LOGO class
    logo = LOGO('192.168.1.10')  # Initialize the LOGO connection with the specified IP address

    # # Example command to set a variable
    # logo.setVariable("Q0", 1)  # Set output 0 to high

    # # Example command to get a variable value
    # value = logo.getVariable("VM0")
    # print(f'The value of VM0 is: {value}')

