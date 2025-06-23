from BaseComponent import BaseComponent
from BaseData import BaseData
import time
import unittest

class SimpleCommand(BaseData):
    f_command = "command"
    f_state = "state"
    @classmethod
    def cmd_change_behaviour(cls,dest_state):
        return cls({cls.f_command: "change_to",cls.f_state:dest_state})      
                
    def get_keys(self):
        return {
            self.f_command: str,
            self.f_state: str
        }, {}


class TestSimpleStateMachineComponent(BaseComponent):
    f_value,b_pending,b_running,b_paused = "value", "pending","running", "paused"

    def awake(self):
        super().awake()
        self.set_behaviour( self.b_pending)        
        self[self.f_value] = 0.0

    def on_exit(self, state_id):
        if state_id == self.b_pending:
            self[self.f_value] = 0.0

    def execute(self, command: SimpleCommand):
        if command[command.f_command] == "change_to":
            self.set_behaviour(command[command.f_state])

    def update(self, time_delta: float):
        if self._current_state == self.b_running:
            self[self.f_value] += 5.0 * time_delta

# --- Component Definition ---
class TestCompleteStateMachineComponent(BaseComponent):
    f_value = "value"
    
    b_pending = "pending"
    b_running = "running"
    b_paused = "paused"
    def define_states(self):
        print("Attached behaviour")
        self._attached_behaviours = {
            self.b_pending: self.Pending(self),
            self.b_running: self.Running(self),
            self.b_paused: self.Paused(self),
        }
        
    def awake(self):
        self.set_behaviour( self.b_pending)
        return super().awake()
    
        
    def execute(self, command: BaseData): # Vanity methods can bypass __attr__ routing
        behaviour = self._attached_behaviours.get(self._current_state)
        if behaviour:
            behaviour.execute(command)            
    
    class Pending(BaseComponent.Behaviour):
        def execute(self, command: "SimpleCommand"):
            print("PENDING EXEC")
            if command[command.f_command] == "change_to":
                self.component.set_behaviour(command[command.f_state])

        def on_exit(self):
            print("ON EXIT EXEC")
            self.component[TestCompleteStateMachineComponent.f_value] =  0.0

    class Running(BaseComponent.Behaviour):
        def execute(self, command: BaseData):
            if command[command.f_command] == "change_to":
                self.component.set_behaviour(command[command.f_state])

        def update(self, time_delta: float):
            val_key = TestCompleteStateMachineComponent.f_value
            val = self.component[val_key]
            self.component[val_key] = val + 5.0 * time_delta

    class Paused(BaseComponent.Behaviour):
        def execute(self, command: BaseData):
            if command[command.f_command]  == "change_to":
                self.component.set_behaviour(command[command.f_state])


class TestBaseComponent(unittest.TestCase):
    def test_state_transition_and_value_tracking(self):
        for CL in [TestSimpleStateMachineComponent,TestCompleteStateMachineComponent]:
            comp = CL()
            val_key = CL.f_value

            # Initial state
            self.assertEqual(comp.get_behaviour(), comp.b_pending)

            # Change to running
            comp.execute(command=SimpleCommand.cmd_change_behaviour(comp.b_running))

            print(f"START running value: {comp[comp.f_value]}")
            self.assertEqual(comp.get_behaviour(), comp.b_running)

            # Accumulate value while running (short loop for verification)
            for i in range(10):
                time.sleep(0.2)
                val = comp[comp.f_value]
                print(f"[{i+1}] Accumulated running value: {val}")
            val = comp[val_key]
            self.assertTrue(1.0 <= val <= 50.0)

            # Change to paused
            comp.execute(command=SimpleCommand.cmd_change_behaviour(comp.b_paused))
            self.assertEqual(comp.get_behaviour(), comp.b_paused)
            print(f"Accumulated running value: {comp[comp.f_value]}")
            # Value should no longer change
            val_before = comp[val_key]
            time.sleep(1)
            val_after = comp[val_key]
            self.assertAlmostEqual(val_before, val_after, delta=0.01)
            print(f"Accumulated running value: {comp[comp.f_value]}")
if __name__ == "__main__":
    unittest.main()