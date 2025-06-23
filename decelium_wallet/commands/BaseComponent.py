import unittest
import time
from typing import Dict, Optional, Any, Callable
from typing import Dict, Optional, Union, Callable
from decelium_wallet.commands.BaseData import BaseData
from decelium_wallet.commands.BaseService import BaseService
from decelium_wallet.commands.DeceliumKernel import DeceliumKernel

class BaseComponent(BaseData):
    class Behaviour(BaseService):
        def __init__(self, component: "BaseComponent"):
            self.component = component

        def on_enter(self): pass
        def on_exit(self): pass
        def activate(self, command: BaseData): pass
        def deactivate(self, command: BaseData): pass
        def execute(self, command: BaseData): pass
        def update(self, time_delta: float): pass    

        @classmethod
        def get_command_map(cls):
            return {
                "on_enter":   {"required_args": [],           "method": cls.on_enter},
                "on_exit":    {"required_args": [],           "method": cls.on_exit},
                "activate":   {"required_args": ["command"],  "method": cls.activate},
                "deactivate": {"required_args": ["command"],  "method": cls.deactivate},
                "execute":    {"required_args": ["command"],  "method": cls.execute},
                "update":     {"required_args": ["time_delta"], "method": cls.update},
            }

    class ComponentRegistry(BaseData):
        @classmethod
        def get_keys(cls): return {'*': BaseComponent.Behaviour}, {}

    def __init__(self, in_dict=None,trim=False):
        super().__init__(in_dict=in_dict or {},trim=trim)
        self._attached_behaviours: Dict[str,  BaseComponent.Behaviour] = BaseComponent.ComponentRegistry({})
        self._current_state: Optional[str] = None
        self._last_update_time = time.time()
        self.define_states()
        DeceliumKernel.register(self)

        #self.awake()

    def define_states(self): pass
    def on_enter(self,state_id): pass
    def on_exit(self,state_id): pass

    def awake(self):
        self._last_update_time = time.time()

    def get_behaviour(self):
        return self._current_state

    def set_behaviour(self, state_id: str):
        if state_id == self._current_state:
            return
        if self._current_state:
            if (self._current_state in self._attached_behaviours and isinstance(self._attached_behaviours[self._current_state], BaseComponent.Behaviour)):
                self._attached_behaviours[self._current_state].on_exit()
            self.on_exit(self._current_state)
        self._current_state = state_id
        if (self._current_state in self._attached_behaviours and isinstance(self._attached_behaviours[self._current_state], BaseComponent.Behaviour)):
            self._attached_behaviours[state_id].on_enter()
        self.on_enter(self._current_state)

    def __getattr__(self, name: str):
        #print(f"searching {name}")
        behaviour = self._attached_behaviours.get(self._current_state)
        if behaviour:
            print(behaviour)
            print(name)
            return lambda *args, **kwargs: behaviour.run(__command=[name], **{'self':behaviour,**kwargs})


    def update(self,timeDelta:float):
        behaviour = self._attached_behaviours.get(self._current_state)
        if behaviour:
            print(f"--- in update {self._current_state}")
            behaviour.update(timeDelta)


    
