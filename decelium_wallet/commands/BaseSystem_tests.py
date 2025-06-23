import unittest
import time, types
from decelium_wallet.commands.BaseData import BaseData
from decelium_wallet.commands.BaseSystem import BaseSystem
from typing import Dict, List, Optional, Generator, Any

class TestStateMachineSystem(BaseSystem):

    class Pending(BaseSystem.GenericBehaviour):
        '''
        def on_enter(self): pass
        def on_exit(self): pass
        def activate(self, command_execution:BaseData) -> Generator: yield
        def deactivate(self, command_execution:BaseData) -> Generator: yield
        def execute(self, command_execution:BaseData) -> Generator: yield
        def state_update(self, time_delta: float) -> Generator: yield        
        '''
        def execute(self, command: BaseData):
            if command['command'] == 'status':
                yield None
            elif command['command'] == 'change_to':
                self.system.set_behaviour(command['state'])
                yield None
        
        def on_exit(self):
            self.system.set_property("value", None, 0.0)

    class Running(BaseSystem.GenericBehaviour):
        def execute(self, command: BaseData):
            if command['command'] == 'status':
                yield None
            elif command['command'] == 'change_to':
                self.system.set_behaviour(command['state'])
                yield None

        def state_update(self, time_delta: float):
            val = self.system.get_property("value")
            self.system.set_property("value", None, val + 5.0*time_delta)
            yield None

    class Paused(BaseSystem.GenericBehaviour):
        def execute(self, command: BaseData):
            if command['command'] == 'status':
                yield None
            elif command['command'] == 'change_to':
                self.system.set_behaviour(command['state'])
                yield None

    def define_states(self):
        self._attached_states = {
            "pending": self.Pending(self),
            "running": self.Running(self),
            "paused": self.Paused(self),
        }
        self.set_behaviour("pending")


class TestBaseSystem(unittest.TestCase):
    def test_state_transition_and_value_tracking(self):
        system = TestStateMachineSystem()
        time.sleep(0.2)

        # Transition from pending -> running
        self.assertEqual(system.get_behaviour_id(), "pending")
        generator = system.execute(BaseData({"command": "change_to", "state": "running"}))
        assert type(generator) ==  types.GeneratorType
        handle = system.StartCoroutine(generator)
        time.sleep(1)
        self.assertEqual(system.get_behaviour_id(), "running")
        system.WaitForCoroutineBlocking(handle)
        time.sleep(3.2)

        # Check value during running

        handle = system.StartCoroutine(system.execute(BaseData({"command": "status"})))
        system.WaitForCoroutineBlocking(handle)

        val = system.get_property("value")
        self.assertTrue(1.0 <= val <= 50.0)

        # Transition to paused
        handle = system.StartCoroutine(system.execute(BaseData({"command": "change_to", "state": "paused"})))
        system.WaitForCoroutineBlocking(handle)
        self.assertEqual(system.get_behaviour_id(), "paused")

        time.sleep(2)
        handle = system.StartCoroutine(system.execute(BaseData({"command": "status"})))
        system.WaitForCoroutineBlocking(handle)
        val_before = system.get_property("value")
        time.sleep(1.2)
        handle = system.StartCoroutine(system.execute(BaseData({"command": "status"})))
        system.WaitForCoroutineBlocking(handle)
        val_after = system.get_property("value")

        self.assertAlmostEqual(val_before, val_after, delta=0.01)


if __name__ == '__main__':
    import dotenv
    dotenv.load_dotenv()
    unittest.main()
