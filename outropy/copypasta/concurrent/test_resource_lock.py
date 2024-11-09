from test.async_test_case import AsyncTestCase

from outropy.copypasta.concurrent.resource_lock import resource_try_lock


class TestResourceLock(AsyncTestCase):
    async def test_try_lock(self) -> None:
        async with resource_try_lock("test_lock") as locked:
            self.assertTrue(locked)
            async with resource_try_lock("test_lock_2") as locked2:
                self.assertTrue(locked2)
            async with resource_try_lock("test_lock") as locked3:
                self.assertFalse(locked3)
        async with resource_try_lock("test_lock") as locked4:
            self.assertTrue(locked4)
