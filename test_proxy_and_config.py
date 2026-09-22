import os
import unittest
from api_server import ClearanceAPIServer, _load_config

class TestProxyAndConfig(unittest.TestCase):
    def test_normalize_proxy(self):
        self.assertEqual(ClearanceAPIServer.normalize_proxy("1.2.3.4:8080"), "http://1.2.3.4:8080")
        self.assertEqual(ClearanceAPIServer.normalize_proxy("user:pass@1.2.3.4:8080"), "http://user:pass@1.2.3.4:8080")
        self.assertEqual(ClearanceAPIServer.normalize_proxy("socks5://user:pass@1.2.3.4:1080"), "socks5://user:pass@1.2.3.4:1080")
        self.assertEqual(ClearanceAPIServer.normalize_proxy("http://1.2.3.4:8080"), "http://1.2.3.4:8080")
        self.assertEqual(ClearanceAPIServer.normalize_proxy("   'http://1.2.3.4:8080'  "), "http://1.2.3.4:8080")
        self.assertIsNone(ClearanceAPIServer.normalize_proxy("# comment"))
        self.assertIsNone(ClearanceAPIServer.normalize_proxy(""))
        self.assertIsNone(ClearanceAPIServer.normalize_proxy(None))

    def test_load_config_env_override(self):
        os.environ["THREAD"] = "8"
        os.environ["HEADLESS"] = "false"
        os.environ["PORT"] = "9000"
        os.environ["PROXIES"] = "1.1.1.1:8080, socks5://2.2.2.2:1080"

        cfg = _load_config()
        self.assertEqual(cfg["thread"], 8)
        self.assertFalse(cfg["headless"])
        self.assertEqual(cfg["port"], 9000)
        self.assertTrue(cfg["proxy_support"])

        server = ClearanceAPIServer(
            headless=cfg["headless"],
            thread=cfg["thread"],
            page_count=cfg["page_count"],
            proxy_support=cfg["proxy_support"],
        )
        server._load_proxies()
        self.assertEqual(server.proxies, ["http://1.1.1.1:8080", "socks5://2.2.2.2:1080"])

if __name__ == "__main__":
    unittest.main()
