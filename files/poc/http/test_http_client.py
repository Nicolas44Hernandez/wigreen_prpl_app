import http.client
import urllib.parse

# Define parameters
url = "192.168.102.12"
port = 3000
endpoint = "/status"
data = {
    "orquestrator_base_url": "orquestrator_base_url",
    "wifi_status": "True",
    "band_2GHz_status": "True",
    "band_5GHz_status": "True",
    "band_6GHz_status": "True",
    "use_situation": "PRESENCE_DAY_LOW_CONSUMPTION",
    "energy_limitations": "100%",
    "alimelo_busvoltage": "8",
    "alimelo_shuntvoltage": "8",
    "alimelo_loadvoltage": "8",
    "alimelo_current_mA": "88",
    "alimelo_power_mW": "8888",
    "alimelo_batLevel": "25",
    "alimelo_power_supplied": "True",
    "alimelo_is_powered_by_battery": "False",
    "alimelo_is_charging": "True",
    "po0_status": "True",
    "po0_powered": "True",
    "po1_status": "True",
    "po1_powered": "True",
    "po2_status": "True",
    "po2_powered": "True",
    "power_strip_relay1_status": "True",
    "power_strip_relay2_status": "True",
    "power_strip_relay3_status": "True",
    "power_strip_relay4_status": "True"
}
timeout = 10

# Encode the data
encoded_data = urllib.parse.urlencode(data)

# Create a connection
conn = http.client.HTTPConnection(url, port, timeout=timeout)

try:
    # Make the POST request
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }
    conn.request("POST", endpoint, body=encoded_data, headers=headers)

    # Get the response
    response = conn.getresponse()
    server_response = response.read()

    print(server_response.decode())  # Print the response
finally:
    conn.close()  # Close the connection
