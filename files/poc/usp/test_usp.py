import pamx
import json


FIELD = "Device.WiFi.Radio.1.Status"


class AmxUspClient:
    """Service class for AmxUsp interface"""

    def __init__(self):
        print("initializing the AmxUspClient")
        pamx.backend.load("/usr/bin/mods/usp/mod-amxb-usp.so")
        pamx.backend.set_config({})
        self.connection = pamx.bus.connect("usp:/var/run/usp/endpoint_agent_path")

    # Python AMX functions : get/set/add/delete
    def read_object(self, path: str):
        """Read USP Object"""
        print(f"AMX USP Read object: {path}")
        return self.connection.get(path)

    def set_object(self, path: str, params: dict):
        """Set USP Object"""
        print(f"AMX USP Set object: {path}  params: {params}")
        return self.connection.set(path, json.loads(params))

    def add_object(self, path, params: dict):
        """Add USP Object"""
        print(f"AMX USP Add object: {path}  params: {params}")
        return self.connection.add(path, json.loads(params))

    def del_object(self, path: str):
        """Delete USP Object"""
        print(f"AMX USP Delete object: {path}")
        return self.connection.delete(path)


if __name__ == "__main__":

    # Create interface
    usp_client = AmxUspClient()

    # retreive field
    data = usp_client.read_object(path=FIELD)
    print(f"FIELD: {FIELD}")
    print(f"DATA: {data}")
