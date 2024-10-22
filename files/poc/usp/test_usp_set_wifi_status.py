import pamx
import json
import time

BASE_PATH = "Device.WiFi.Radio.1."
FIELD_GET = "Status"
FIELD_SET = "Enable"


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
        return self.connection.set(path, params)

    def add_object(self, path, params: dict):
        """Add USP Object"""
        print(f"AMX USP Add object: {path}  params: {params}")
        return self.connection.add(path, json.loads(params))

    def del_object(self, path: str):
        """Delete USP Object"""
        print(f"AMX USP Delete object: {path}")
        return self.connection.delete(path)


if __name__ == "__main__":
    new_status = "0"
    # Create interface
    usp_client = AmxUspClient()
    print(f"FIELD: {BASE_PATH}")
    for i in range(5):
        print(f"----------------------Iteration {i}---------------------")
        # Read field
        data = usp_client.read_object(path=f"{BASE_PATH}{FIELD_GET}")
        print(f"DATA READ: {data}")
        current_status = data[0][list(data[0].keys())[0]]["Status"]
        new_status = "0" if "Up" in current_status else "1"
        ret = usp_client.set_object(path=BASE_PATH, params={FIELD_SET: new_status})
        print(f"ret: {ret}   - type(ret): {type(ret)}")
        time.sleep(10)
