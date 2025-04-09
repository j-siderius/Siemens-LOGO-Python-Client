# Siemens LOGO Python Client
Small Python wrapper for communicating with the Siemens LOGO line of PL Controllers. The wrapper exposes the unofficial API that is normally used through the LOGO Web Interface.
It is possible to get (read) and set (change) the Variables, Inputs, Outputs and special memory addresses. Connection to the Siemens LOGO PLC happens over IP / Ethernet.

Uses and adapts the excellent research, documentation and example code from [Jankeymeulens' Siemens LOGO Rest repository](https://github.com/jankeymeulen/siemens-logo-rest).

## Installation and Notes
1. Clone the repository to desired location
2. Install dependencies (optionally in a virtual environment) using `pip install -r requirements.txt`

- The WebUser of the LOGO Web Interface needs to have a password set. This can be configured through the Siemens Soft Comfort LOGO programming software.
- The unofficial API is tested for (Analog) Inputs, (Analog) Outputs, Motor In/Outputs and Variable Memory types on a Siemens LOGO! 8.3 PLC. Other functions might be supported but remain untested.
- Outputs can only be set while a program is running on the Siemens LOGO PLC.
- If a program needs to be started from the Python script, a Network Input can be added to the LOGO program (e.g. VariableMemory address 0) which can be used to Enable the program. By running `setVariable("VM0", '1')`, the program can be started and by running `setVariable("VM0", '0')` the program can be 'stopped'. There is no direct implementation to RUN and STOP the program fully.

## API
**LOGO** (Init)

_ip_address_ (str): The IP address of the Siemens LOGO Web Interface.

_webuser_password_ (str):  The password for the WebUser account. Defaults to 'webuser'.

The LOGO class provides methods to interact with the Siemens LOGO PLC controller. It supports variable retrieval and setting through AJAX API calls.

**getVariable**

Retrieves the value of a specified variable from the LOGO PLC.

_variable_ (str): The variable to retrieve, formatted as 'TypeAddress' (e.g., 'VM0', 'I1').

_Returns_ (str): The value of the specified variable, or None if the variable type is unsupported.

**setVariable**

Sets the value of a specified variable on the LOGO PLC.

_variable_ (str): The variable to retrieve, formatted as 'TypeAddress' (e.g., 'VM0', 'Q1').

_value_ (str): The value to assign to the specified variable.

## Variable types

The following variable types are supported:
- VM: Variable Memory
- I: Inputs
- NetI: Network Inputs
- Q: Outputs
- NetQ: Network Outputs
- M: Motor Outputs
- AI: Analog Inputs
- NetAI: Network Analog Inputs
- AQ: Analog Outputs
- NetAQ: Network Analog Outputs
- AM: Analog Motor Outputs

## Example usage
```python
# Initialize the LOGO connection with the specified IP address
logo = LOGO('192.168.1.10')

# Set a variable
logo.setVariable("Q1", "1")

# Get a variable value
value = logo.getVariable("VM0")
print(f'The value of VM0 is: {value}')
```

## Required libraries
- requests
