
import os
import json
import importlib.util
from contextlib import contextmanager

from decelium_wallet.commands.BaseService import BaseService  # adjust import
from decelium_wallet.commands.BaseData import BaseData  # adjust import

class PythonCommand(BaseData):
    """
    Schema for the 'invoke' command arguments, validated by BaseData.do_validation.
    """
    class_path: str
    cwd: str
    class_name: str
    class_data: dict      # JSON parsed into dict
    method_name: str
    method_args: dict     # JSON parsed into dict

    def do_validation(self, key, value):
        # Validate and convert each field
        if key == 'class_path':
            if not os.path.isfile(value):
                self.do_raise(f"Invalid class_path:"+ str( value)+f" str:{type(value)} --  file:{not os.path.isfile(value)}")
            return value, ''

        if key == 'cwd':
            if not isinstance(value, str) or (value and not os.path.isdir(value)):
                self.do_raise(f"Invalid cwd:", value)
            return value, ''

        if key in ('class_name', 'method_name'):
            if not isinstance(value, str) or not value:
                self.do_raise(f"{key} must be a non-empty string.")
            return value, ''

        if key == 'class_data':
            # Expect a JSON string or dict
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                except json.JSONDecodeError as e:
                    self.do_raise(f"Invalid JSON for class_data: {e}")
                return parsed, ''
            if not isinstance(value, dict):
                self.do_raise(f"class_data must be JSON or dict.")
            return value, ''

        if key == 'method_args':
            # Expect a JSON string or dict
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                except json.JSONDecodeError as e:
                    self.do_raise(f"Invalid JSON for method_args: {e}")
                return parsed, ''
            if not isinstance(value, dict):
                self.do_raise(f"method_args must be JSON or dict.")
            return value, ''

        # Fallback to BaseData default validation
        return super().do_validation(key, value)

class BaseDataService(BaseService):
    @classmethod
    def get_command_map(cls):
        # Dynamically derive required args from PythonCommand schema
        return {
            'invoke': {
                'required_args': list(PythonCommand.__annotations__.keys()),
                'method': cls.static_invoke
            }
        }

    @staticmethod
    @contextmanager
    def _cwd(path: str):
        original = os.getcwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(original)

    @staticmethod
    def _load_module(path: str, cwd: str):
        if cwd:
            workdir = cwd
        else:
            workdir = os.getcwd()
        with BaseDataService._cwd(workdir):
            spec = importlib.util.spec_from_file_location("_mod", path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot import module from {path}")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    @staticmethod
    def static_invoke(**kwargs) -> str:
        """
        Use PythonCommand to validate invoke arguments, instantiate the class,
        invoke its method, and return JSON result.
        """
        # Validate & parse via BaseData
        invoke = PythonCommand(**kwargs)

        # Load module & get class
        module = BaseDataService._load_module(invoke.class_path, invoke.cwd)
        if not hasattr(module, invoke.class_name):
            raise AttributeError(f"Class '{invoke.class_name}' not found in module '{invoke.class_path}'")
        klass = getattr(module, invoke.class_name)

        # Instantiate the target class
        instance = klass(invoke.class_data)

        # Invoke the target method
        if not hasattr(instance, invoke.method_name):
            raise AttributeError(f"Method '{invoke.method_name}' not on '{invoke.class_name}'")
        method = getattr(instance, invoke.method_name)
        if not callable(method):
            raise TypeError(f"'{invoke.method_name}' of '{invoke.class_name}' is not callable")
        result = method(**invoke.method_args)

        # Serialize updated state
        state = instance.to_safe_dict() if hasattr(instance, 'to_safe_dict') else dict(instance)

        # Return combined output
        return json.dumps({ 'result': result, 'data': state })

if __name__ == "__main__":
    BaseDataService.run_cli()