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
        os.environ["WORKER_MODE"] = "true"
        os.environ["IDLE_TIMEOUT"] = "15"

        cfg = _load_config()
        self.assertEqual(cfg["thread"], 8)
        self.assertFalse(cfg["headless"])
        self.assertEqual(cfg["port"], 9000)
        self.assertTrue(cfg["proxy_support"])
        self.assertTrue(cfg["worker_mode"])
        self.assertEqual(cfg["idle_timeout"], 15)

        server = ClearanceAPIServer(
            headless=cfg["headless"],
            thread=cfg["thread"],
            page_count=cfg["page_count"],
            proxy_support=cfg["proxy_support"],
            worker_mode=cfg["worker_mode"],
            idle_timeout=cfg["idle_timeout"],
        )
        server._load_proxies()
        self.assertEqual(server.proxies, ["http://1.1.1.1:8080", "socks5://2.2.2.2:1080"])
        self.assertTrue(server.worker_mode)
        self.assertEqual(server.idle_timeout, 15)

    def test_worker_mode_task_tracking_and_idle_shutdown(self):
        import asyncio

        async def run_test():
            server = ClearanceAPIServer(
                headless=True,
                thread=1,
                page_count=1,
                proxy_support=False,
                worker_mode=True,
                idle_timeout=1,
            )

            # Check startup in worker_mode defers browser creation
            await server._startup()
            self.assertIsNone(server.browser)

            # Mock initialization without starting real browser
            async def fake_init():
                class FakeBrowser:
                    def is_connected(self):
                        return True
                    async def close(self):
                        pass
                server.browser = FakeBrowser()

            server._initialize_browser = fake_init

            # Ensure browser ready
            await server._ensure_browser_ready()
            self.assertIsNotNone(server.browser)

            # Test increment/decrement active tasks
            server._increment_active_tasks()
            self.assertEqual(server._active_tasks, 1)

            server._decrement_active_tasks()
            self.assertEqual(server._active_tasks, 0)
            self.assertIsNotNone(server._idle_task)

            # Wait for idle shutdown to trigger
            await asyncio.sleep(1.2)
            self.assertIsNone(server.browser)

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
