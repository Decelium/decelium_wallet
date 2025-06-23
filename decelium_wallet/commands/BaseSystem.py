import io
import json
from typing import Dict, List, Optional, Generator, Any
from decelium_wallet.commands.BaseService import BaseService
from decelium_wallet.commands.BaseData import BaseData,FloatRange
from decelium_wallet.commands.DeceliumKernel import DeceliumKernel

class BaseSystem(BaseService):
    def StartCoroutine(self,routine: Generator) -> "DeceliumKernel.CoroutineHandle":
        return DeceliumKernel.StartCoroutine(routine)
    def WaitForCoroutine(self,handle: "DeceliumKernel.CoroutineHandle") -> Generator:
        return DeceliumKernel.WaitForCoroutine(handle)
    
    def WaitForCoroutineBlocking(self, handle: "DeceliumKernel.CoroutineHandle", timeout_seconds: float = 5.0):
        return DeceliumKernel.WaitForCoroutineBlocking(handle,timeout_seconds)
    class GenericBehaviour:
        def __init__(self, system: "BaseSystem"):
            self.system = system
            
            
        def on_enter(self): pass
        def on_exit(self): pass
        def activate(self, command_execution:BaseData) -> Generator: yield
        def deactivate(self, command_execution:BaseData) -> Generator: yield
        def execute(self, command_execution:BaseData) -> Generator: yield
        def state_update(self, time_delta: float) -> Generator: yield

    def __init__(self, data=None):
        self._attached_states: Dict[str, BaseSystem.GenericBehaviour] = {}
        self._current_state: Optional[str] = None

        # TODO Revisit parent / child management and the general approach to taxonomy
        #self._parent_system: Optional["BaseSystem"] = None
        #self._subsystems: List["BaseSystem"] = []
        # self._levels: Dict[str, FloatRange] = self.define_levels() NOT USING LEVELS FOR NOW

        self._system_properties: BaseData = self.define_system_properties()
        # self._group_properties: BaseData = self.define_group_properties() TEST LATER
        self.define_states()
        DeceliumKernel.register(self)

    # ---------- CORE EXTENSION POINTS ----------

    def define_states(self): pass # Should assing any states into self._attached_states: Dict[str, BaseSystem.GenericBehaviour] = {}
    # def define_levels(self) -> Dict[str, FloatRange]: return {} IGNORING LEVELS FOR NOW
    def define_system_properties(self) -> BaseData: return BaseData({})
    # def define_group_properties(self) -> BaseData: return BaseData({}) IGNORING GROUP AGGREGATION FOR NOW. DONT LOVE THE PATTERN.
    def awake(self): pass
    def do_start(self): pass
    def get_title(self): return "Override BaseSystem.get_title()"
    def get_short_description_text(self): return "unimplemented"
    def on_global_enter(self, state_id: str): pass
    def on_global_exit(self, state_id: str): pass


    # ---------- STATE MANAGEMENT ----------
    def get_behaviour_id(self):
        return self._current_state
    def set_behaviour(self, state_id: str):
        if state_id == self._current_state:
            return
        if self._current_state:
            b = self._attached_states.get(self._current_state)
            if b: b.on_exit()
            self.on_global_exit(self._current_state)

        self._current_state = state_id
        b = self._attached_states.get(state_id)
        if b:
            self.on_global_enter(state_id)
            b.on_enter()

    def get_behaviour_instance(self, state_id: str) -> Optional["BaseSystem.GenericBehaviour"]:
        return self._attached_states.get(state_id)

    def get_valid_states(self) -> List[str]:
        return list(self._attached_states.keys())

    def activate(self, exec_context=None) -> Generator:
        b = self.get_behaviour_instance(self._current_state)
        if b: yield from b.activate(exec_context)

    def deactivate(self, exec_context=None) -> Generator:
        b = self.get_behaviour_instance(self._current_state)
        if b: yield from b.deactivate(exec_context)

    def execute(self, exec_context=None) -> Generator:
        b = self.get_behaviour_instance(self._current_state)
        if b:
            yield from b.execute(exec_context)
            if exec_context and hasattr(exec_context, "on_finish"):
                exec_context.on_finish(exec_context)
        yield None
        

    def update(self, time_delta: float) -> Generator:
        b = self.get_behaviour_instance(self._current_state)
        if b: yield from b.state_update(time_delta)
    '''
    # ---------- PARENT AND HIERARCHY ----------

    def set_parent_system(self, parent: "BaseSystem"):
        self._parent_system = parent

    def get_parent_system(self) -> Optional["BaseSystem"]:
        return self._parent_system

    def add_subsystem(self, subsystem: "BaseSystem"):
        subsystem.set_parent_system(self)
        self._subsystems.append(subsystem)

    def get_subsystems(self) -> List["BaseSystem"]:
        return self._subsystems

    # ---------- LEVEL SYSTEM ----------

    def get_level(self, name: str) -> Optional[FloatRange]:
        return self._levels.get(name)

    def set_level(self, name: str, value: float):
        if name not in self._levels:
            self._levels[name] = FloatRange(0, value, value)
        else:
            self._levels[name].Set(value)

    def add_level(self, name: str, amount: float):
        level = self.get_level(name)
        if level:
            level.Set(level.index + amount)

    def subtract_level(self, name: str, amount: float):
        level = self.get_level(name)
        if level:
            level.Set(level.index - amount)

    def get_level_names(self) -> List[str]:
        return list(self._levels.keys())
    '''
    # ---------- PROPERTY METHODS ----------

    def contains_property(self, pid: str, group_id: str = None) -> bool:
        return pid in self._system_properties

    def get_property(self, pid: str, group_id: str = None) -> float:
        return self._system_properties.get(pid,None)

    def set_property(self, pid: str, group_id: str = None, val=None) -> bool:
        self._system_properties[pid] = val
        return True

    def set_default_property(self, pid: str, group_id: str = None, val=None) -> bool:
        if pid not in self._system_properties:
            return self.set_property(pid, group_id, val)
        return False
