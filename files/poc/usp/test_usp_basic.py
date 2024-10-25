import pamx

FIELD = "Device.DeviceInfo.FriendlyName"

pamx.backend.load("/usr/bin/mods/usp/mod-amxb-usp.so")
pamx.backend.set_config({})
connection = pamx.bus.connect("usp:/var/run/usp/endpoint_agent_path")
data = connection.get(FIELD)
print(f"DATA: {data}")
