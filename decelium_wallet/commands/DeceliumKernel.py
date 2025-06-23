
from typing import List
import time, types
import threading
from typing import Dict, List, Optional, Generator, Any
import time, threading, types
from typing import Generator, Any, List
import types
class DeceliumKernel:
    class CoroutineHandle:
        def __init__(self, generator):
            self.generator = generator
            self.done = False
    _awoken: Dict[int, bool] = {}  # Tracks if each system has been awakened
    systems: List[Any] = []
    _awakened: bool = False
    _running: bool = True
    _thread = None
    _lock = threading.Lock()
    _coroutines: List[Generator] = []  # coroutine queue

    @classmethod
    def register(cls, system: Any):
        cls.systems.append(system)
        if not cls._awoken.get(id(system)):
            system.awake()
            cls._awoken[id(system)] = True


    @classmethod
    def start(cls):
        cls._running = True
        cls.__run()

    @classmethod
    def stop(cls):
        cls._running = False
        cls.systems.clear()
        cls._coroutines.clear()

    @classmethod
    def run(cls, time_step: float = 0.5):
        cls.__run(time_step)

    @classmethod
    def StartCoroutine(cls, routine: Generator) -> CoroutineHandle:
        assert type(routine) ==  types.GeneratorType        
        handle = cls.CoroutineHandle(routine)
        cls._coroutines.append(handle)
        return handle

    @classmethod
    def StopCoroutine(cls, handle: CoroutineHandle):
        assert type(handle) == DeceliumKernel.CoroutineHandle 
        cls._coroutines = [c for c in cls._coroutines if c != handle]

    def WaitForCoroutineBlocking(handle: "DeceliumKernel.CoroutineHandle", timeout_seconds: float = 5.0):
        start = time.time()
        while not handle.done:
            if time.time() - start > timeout_seconds:
                raise DeceliumKernel.Timeout("Coroutine wait timed out.")
            time.sleep(0.01)

    @classmethod
    def __run(cls, time_step: float = 0.5):
        if cls._thread and cls._thread.is_alive():
            return

        def _loop():
            if not cls._running:
                return

            while cls._running:
                for system in cls.systems:
                    try:
                        retVal = system.update(time_step)
                        if type(retVal) == types.GeneratorType:
                            DeceliumKernel.StartCoroutine(retVal)
                    except Exception as e:
                        import traceback as tb
                        print (tb.format_exc())
                        print(e)
                # Advance one step of each coroutine
                cls._coroutines = [
                    co for co in cls._coroutines
                    if DeceliumKernel._advance(co)
                ]

                time.sleep(time_step)

        cls._thread = threading.Thread(target=_loop, daemon=True)
        cls._thread.start()

    @staticmethod
    def _advance(co: "DeceliumKernel.CoroutineHandle") -> bool:
        try:
            next(co.generator) # // TypeError: 'CoroutineHandle' object is not an iterator
            return True
        except StopIteration:
            co.done = True
            return False
        
    @staticmethod
    def WaitForCoroutine(handle: "DeceliumKernel.CoroutineHandle") -> Generator:
        while not handle.done:
            yield        
        




DeceliumKernel.run()  # Safe to call more than once        
