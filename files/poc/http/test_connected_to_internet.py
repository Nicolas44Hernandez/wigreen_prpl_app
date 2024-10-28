import http.client as httplib
import ssl

host = "google.com"


def is_connected_to_internet() -> bool:
    """Check internet connection"""
    context = ssl._create_unverified_context()
    conn = httplib.HTTPSConnection(host, timeout=5, context=context)
    try:
        conn.request("HEAD", "/")
        print("connected!")
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        conn.close()


print(f"Trying to connect to host:{host}")
is_connected_to_internet()
