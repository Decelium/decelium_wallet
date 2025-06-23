from functools import wraps
from types import FunctionType
from typing import get_origin, get_args, Any, Union, Callable

import json
import os
import re
import io

def auto_c(parameter_type):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            new_args = [
                parameter_type(arg) if isinstance(arg, dict) and parameter_type is not dict else arg
                for arg in args
            ]
            new_kwargs = {
                k: parameter_type(v) if isinstance(v, dict) and parameter_type is not dict else v
                for k, v in kwargs.items()
            }
            return func(*new_args, **new_kwargs)
        return wrapper 
    return decorator
# TODO - Remove duplicate code

class BaseDataMeta(type):
    def __new__(mcs, name, bases, namespace):
        for field in namespace.get('__annotations__', {}):
            namespace.setdefault(field, field)
        return super().__new__(mcs, name, bases, namespace)
from functools import lru_cache

class BaseField:
    def __new__(cls, value):
        return value


class BaseData(dict, metaclass=BaseDataMeta):
    @classmethod
    @lru_cache(maxsize=None)
    def get_annotations(cls):
        anns = {}
        for base in reversed(cls.__mro__):
            anns.update(getattr(base, "__annotations__", {}) or {})
        return anns    

    def get_all_keys(self):
        self._internal_defaults = {}
        """
        Merge annotation-based required keys with get_keys().
        Any annotated attribute is treated as a required field.
        If a key appears both in annotations and in get_keys(), raise an error.
        """
        anns = self.get_annotations()

        for key in anns:
            setattr(self, f"f_{key}", key)            
        req_add = {}
        opt_add = {}
        for k in anns:
            if type(anns[k]) == tuple:
                assert len(anns[k]) == 2
                opt_add[k] = anns[k][0]
                assert type(anns[k][0]) != str
                self._internal_defaults [k] = anns[k][1]
            else:
                req_add[k] = anns[k]
                assert type(anns[k]) != str
        for key, expected_type in req_add.items():
            assert type(expected_type) != str
        for key, expected_type in opt_add.items():
            assert type(expected_type) != str

        req, opt = self.get_keys()
        conflicts = set(anns) & (set(req) | set(opt))
        if conflicts:
            raise ValueError(f"Conflicting key definitions for: {conflicts}")
        merged_required = {**req_add, **req}
        merged_opt = {**opt_add, **opt}
        return merged_required, merged_opt


    def __setattr__(self, name, value):
        """
        If `name` is in annotations, attempt to set via BaseData dict interface
        by calling set_annotation. Otherwise, fall back to normal attribute set.
        """
        anns = getattr(self.__class__, "__annotations__", {}) or {}
        if name in anns:
            self.__setitem__(name, value)
            return
        super().__setattr__(name, value)

    @staticmethod
    def do_raise(description=None):
        if description == None:
            description = "Invalid corruption type"
        raise ValueError(description)    
    
    def get_all_defaults(self):
        #defaults = {'id': "aaa", 'name': 3,'age': 33}
        defaults = self._internal_defaults.copy()
        defaults.update(self.get_defaults())
        return defaults
    
    def get_defaults(self):
        #defaults = {'id': "aaa", 'name': 3,'age': 33}
        defaults = {}
        return defaults
    
    def get_keys(self):
        required = {}
        optional = {}
        #required = {'id': str, 'name': int}
        #optional = {'age': int, 'interests': dict}
        return required, optional
    
    def do_every_validation(self,key,value):
        return value,""
    
    def do_validation(self,key,value):

        return value,""
    
    def do_get_filtered(self,key,value):
        return value
  
    @classmethod
    def valid_type(cls,value: Any, annotation) -> bool:
        """
        Recursively check whether `value` conforms to the typing annotation.
        Supports:
        - Any
        - Union / Optional
        - list[T]
        - dict[K,V]
        - tuple[...] (including Tuple[T, ...])
        - plain classes
        """
        origin = get_origin(annotation)
        args   = get_args(annotation)

        # 1) Any always passes
        if annotation is Any:
            return True

        # 2) Union / Optional
        if origin is Union:
            #print("valid_type UNION")
            return any(cls.valid_type(value, arg) for arg in args)

        # 3) list
        if origin is list or annotation is list:
            if not isinstance(value, list):
                return False
            (elem_type,) = args or (Any,)
            return all(cls.valid_type(item, elem_type) for item in value)

        # 4) dict
        if origin is dict or annotation is dict:
            if not isinstance(value, dict):
                return False
            key_t, val_t = args if len(args) == 2 else (Any, Any)
            return all(
                cls.valid_type(k, key_t) and cls.valid_type(v, val_t)
                for k, v in value.items()
            )

        # 5) tuple
        if origin is tuple:
            if not isinstance(value, tuple):
                return False
            # variable-length Tuple[T, ...]
            if len(args) == 2 and args[1] is Ellipsis:
                return all(cls.valid_type(item, args[0]) for item in value)
            # fixed-length
            if len(args) != len(value):
                return False
            return all(cls.valid_type(item, t) for item, t in zip(value, args))

        if annotation is Callable or origin is Callable:
            return callable(value)

        # 6) plain class
        if isinstance(annotation, type):
            return isinstance(value, annotation)

        # fallback: reject
        return False

    '''
    def _is_valid_type(cls,value, expected_type):
        origin = get_origin(expected_type)
        args = get_args(expected_type)

        if expected_type is Any:
            return True

        # Handle Optional / Union
        if origin is Union:
            return any(cls._is_valid_type(value, arg) for arg in args)

        # Handle List[...] and list
        if origin is list or expected_type is list:
            if not isinstance(value, list):
                return False
            item_type = args[0] if args else Any
            return all(cls._is_valid_type(v, item_type) for v in value)

        # Handle Dict[...] and dict
        if origin is dict or expected_type is dict:
            if not isinstance(value, dict):
                return False
            key_type = args[0] if args else Any
            val_type = args[1] if len(args) > 1 else Any
            return all(cls._is_valid_type(k, key_type) and cls._is_valid_type(v, val_type) for k, v in value.items())

        # Handle Tuple[...] (optional)
        if origin is tuple:
            if not isinstance(value, tuple):
                return False
            if len(args) == 2 and args[1] is Ellipsis:  # Tuple[int, ...]
                return all(cls._is_valid_type(v, args[0]) for v in value)
            return len(args) == len(value) and all(cls._is_valid_type(v, t) for v, t in zip(value, args))

        # Fallback to regular isinstance for raw types
        if isinstance(expected_type, type):
            return isinstance(value, expected_type)

        return False
    '''
    def validate_and_convert(self, key, expected_type, init_dict):
        assert type(expected_type) != str, f" {expected_type} is actually a string?"
        if key == '*':
            return
        if not key in init_dict.keys():
            value = None
        else:
            value = init_dict[key]
        """Validates and converts a single key value based on its expected type."""
        
        if isinstance(expected_type, FunctionType):
            if expected_type.__code__.co_argcount == 1:
                value = expected_type(value)
            else:
                value = expected_type(self, value)            
        elif isinstance(expected_type, type) and (issubclass(expected_type, BaseData) and isinstance(value, dict)):
            value = expected_type(value)
                
        new_val, message = self.do_validation(key, value)
        # Check if you have an error message from being Null. None is allowed by default, unless the implementer returns a validation error text.
        if new_val is None:
            #print(key)
            #print(f"your last defaults {self.get_all_defaults() }")
            #print(f"current value {new_val}")
            if key in self.get_all_defaults() and new_val == self.get_all_defaults()[key]:
                pass # Allowed to be empty default value
            elif (expected_type == Any):
                pass # Allowed to be empty default value
            else:
                raise TypeError(f"do_validation did not pass for {type(self)} {key}:{expected_type} , {value} -- Are you forgetting {key}{init_dict}")
        if isinstance(expected_type, type) and (issubclass(expected_type, BaseData)):
            pass # Already passed deep validation above ^. below is for raw data
        elif (expected_type != Any and not isinstance(expected_type, FunctionType)):
            res = True
            try:
                #if new_val is not None and not isinstance(new_val, expected_type) and expected_type:
                #    res = False
                if new_val is not None and not self.valid_type(new_val, expected_type):
                    res = False                  
            except Exception as e:
                    import traceback as tb
                    print("\n\n\n BaseData Debug")
                    print(tb.format_exc())
                    print(new_val)
                    raise TypeError(f"b Expected type {expected_type} for key '{key}' CRASHED, got {type(new_val)} in  {type(self)}  -- {message}")
            if res==False:            
                print(self)
                print(new_val)
                raise TypeError(f"a Expected type {expected_type} for key '{key}', got {type(new_val)} in  {type(self)}   -- {message}")

        init_dict[key] = new_val
    

    def do_env_mapping(self, in_dict):
        if isinstance(in_dict, BaseData):
            return in_dict        
        def replace_env_match(match):
            env_var = match.group(1)
            value = os.getenv(env_var)
            if value is None:
                raise ValueError(f"Missing required environment variable: '{env_var}' for '{self.__class__.__name__}'")
                return match.group(0)
            return value

        def _replace_env_vars( s):

            pattern = re.compile(r'<<([A-Z_][A-Z0-9_]*)>>')
            # Replace all matches using the externally defined function.
            return pattern.sub(replace_env_match, s)

        if isinstance(in_dict, dict):
            new_dict = {}
            for key, value in in_dict.items():
                new_dict[key] = self.do_env_mapping(value)
            return new_dict
        elif isinstance(in_dict, list):
            new_list = []
            for item in in_dict:
                new_list.append(self.do_env_mapping(item))
            return new_list
        elif isinstance(in_dict, str):
            return _replace_env_vars(in_dict)
        else:
            # For non-dict, non-list, non-string types, return the value unchanged.
            return in_dict
    
    def clean(self):
        required, optional = self.get_all_keys()
        allowed_keys = set(required) | set(optional)
        cleaned_dict = {k: self[k] for k in allowed_keys if k in self}
        return self.__class__(cleaned_dict)


    def do_pre_process(self,in_dict):
        return in_dict

    def GetDirtyDict(self):
        # Can be used during init to see the unvalidated vars before they are baked. Rarely needed.
        return self.dirty_dict
    
    def __getattribute__(self, name):
        if name == "graph":
            print(f"SEARCHING FOR  {name}")
            print(f"ANNOTS {type(self)} {type(self).get_annotations()}")
        if name in type(self).get_annotations():
            try:
                if name == "graph":
                    print(f"SEARCHING FOR  2 {name}")
                return self[name]
            except KeyError:
                raise AttributeError(f"{name!r} not set")
        else:
            return super().__getattribute__(name)


    def __init__(self, in_dict=None,trim=False, **kwargs):
        for aname in self.get_annotations():
            if aname in self.__dict__:
                self.__dict__[aname] = "REMOVED"
   
            
        # if (self.__class__.__name__ == "ServiceMap" ):
        #     try:
        #         BaseData.call_cnt
        #     except:
        #         BaseData.call_cnt = 0 
        #     BaseData.call_cnt = self.call_cnt + 1
        #     print(f"\n\n\n\n\n====================================> IN BASE CLASS {BaseData.call_cnt}--  {self.__class__.__name__}, {in_dict}")
        #     #raise Exception("FAILED")
        if in_dict == None:
            in_dict = {} # Will contain a null
        if kwargs and len(kwargs)> 0:
            #print(f"HAS KW ARGS==> ")
            for k in kwargs:
                in_dict[k] = kwargs[k]
        #else:
        #    print(f"NO KW ARGS==> ")
        assert isinstance(in_dict,dict), f"must use with dict value for in_dict. This is a Dict constructor. Got the following : {in_dict}"
        if isinstance(in_dict,type(self)):
            super().__init__(in_dict)      
            return
        self.dirty_dict =  in_dict.copy()
        # if (self.__class__.__name__ == "ServiceMap" ):
        #     print(f"====================================> Runnning pre-process {BaseData.call_cnt}-- in {self.__class__.__name__}:{in_dict}")
        in_dict = self.do_pre_process(in_dict) ### Right, I should pre-process the env, not validate.
        if in_dict == None:
            raise Exception("Pre process must return a processed dict")
        in_dict = self.do_env_mapping(in_dict)
        required_keys, optional_keys = self.get_all_keys()
        for key, expected_type in required_keys.items():
            assert type(expected_type) != str
        for key, expected_type in optional_keys.items():
            assert type(expected_type) != str

        if trim == False:
            init_dict = in_dict
        else:
            all_keys = list(required_keys.keys()) + list(optional_keys.keys())
            init_dict = in_dict.copy()
            for k in init_dict.keys():
                if k not in all_keys:
                    del(init_dict[k])
        
        # Validate and convert required keys
        #print(f"{self.__class__.__name__}.REQ_KEYS: {list(required_keys.keys())}" )
        for key, expected_type in required_keys.items():
            self.validate_and_convert(key, expected_type, init_dict)
            if key not in init_dict and key != '*':
                raise ValueError(f"Key '{key}' must be in the initialization dictionary")

        # Validate and convert optional keys if they are present
        #print(f"{self.__class__.__name__}.OPT_KEYS: {list(optional_keys.keys())}" )
        #print(in_dict)
        for key, expected_type in optional_keys.items():
            if key in init_dict:
                self.validate_and_convert(key, expected_type, init_dict) ###### <-------
        wildcard = required_keys.get('*') or optional_keys.get('*')
        if wildcard:
            for key in list(init_dict.keys()):
                if key not in required_keys and key not in optional_keys:
                    self.validate_and_convert(key, wildcard, init_dict)                

        self.dirty_dict = None
        for key, value in init_dict.items():
              newval,msg = self.do_every_validation(key, value)
              if len(msg) > 0:
                  raise Exception(msg)
              init_dict[key] = newval

        defaults = self.get_all_defaults() ######## <----- FAILS
        for key in defaults.keys():
            if key not in init_dict and defaults[key] != None:
                init_dict[key] = defaults[key]
        #print(f"final dict {init_dict}")
        super().__init__(init_dict)
        
    def __setitem__(self, key, value):
        # print(f"Doing validation for key {key}")
        # TODO, Generalize the validation check, and run it on set in a complete manner
        # validated_value, message = self.do_validation(key, value)
        #
        required_keys, optional_keys = self.get_all_keys()
        all_keys = {**required_keys, **optional_keys}
        out_data = {key:value}
        #print(f"-~-~-~-~-~-~-~-~> <{key}->{value}> in {all_keys.keys()}")
        if key in list(all_keys.keys()):
            #print(f"--------------------------------> {key}")
            self.validate_and_convert( key=key,expected_type= all_keys[key], init_dict=out_data)
        super().__setitem__(key, value)

    # New __getitem__ wrapper
    def __getitem__(self, key):
        try:
            # Retrieve the value using the parent dict's method.
            value = super().__getitem__(key)
        except KeyError as e:
            self.do_raise(f"Key '{key}' not found in the BaseData instance")
        return self.do_get_filtered(key,value)

    def set(self,key,val):
        self.__setitem__(key, val)
        return True

    def to_safe_value(self,key, val):
        if hasattr(val, "to_safe_dict") and callable(val.to_safe_dict):
            #print(f"\n\nwtf \na:{type(self)} \nb:{type(val)} -.\n\nc:{key}:{val}")
            return val.to_safe_dict()
        if isinstance(val, dict):
            val = BaseData(val)
            return val.to_safe_dict(val)
        if isinstance(val, list):
            return self.to_safe_list(val)
        if isinstance(val, tuple):
            return tuple(self.to_safe_list(list(val)))
        if isinstance(val, type):
            return val.__name__
        return val


    def to_safe_dict(self, target_dict=None):
        """
        Recursively convert this mapping to built-ins, using to_safe_value.
        """
        if target_dict is None:
            target_dict = self

        safe = {}
        for key, val in target_dict.items():
            safe[key] = self.to_safe_value(key,val)
        return safe


    def to_safe_list(self, target_list):
        """
        Recursively convert a list of mixed elements to built-ins.
        """
        return [self.to_safe_value(None,val) for val in target_list]



#
# # # #
#
def run_simple_test():

    class BodyPartData(BaseData):
        def get_keys(self):
            required = {'id': str, 'part_name': str}
            optional = {'health': int, 'skills': dict}
            return required, optional    

    class HumanData(BaseData):
        def get_keys(self):
            required = {'id': str, 'name': str}
            optional = {'age': int, 'interests': dict,'arm':BodyPartData}
            return required, optional    
        
        def do_validation(self,key,value):
            if key == 'age':
                assert value > 0 and value < 120, "Humans must have a valid age range"
            return value,""

    class CarData(BaseData):
        def get_keys():
            required = {'id': str, 'name': str}
            optional = {'driver': HumanData}
            return required, optional    
    import pprint    
    # Example usage
    humanData = HumanData({'id': '123', 
                    'name': "Jeff", 
                    'age': 30,
                    'arm':{'id': "bigArm", 'part_name': "part_1"}})


    arm = BodyPartData({'id': "bigArm", 'part_name': "part_1"})
    humanData2 = HumanData({'id': '123', 
                    'name': "Jeff", 
                    'age': 30,
                    'arm':arm})

#from decelium_wallet import core as core



class ConnectionConfig(BaseData):
    def decw(self):
        return self['decw']
    def user_context(self) -> str:
        return self['user_context']
    def connection_settings(self) -> dict:
        return self['connection_settings']
    def backup_path(self) -> str:
        return self['backup_path']
    def local_test_folder(self) -> str:
        return self['local_test_folder']
    
    def get_keys(self):
        required = {'decw':lambda v:v, # (╯°□°)╯︵ ┻━┻ 
                    'user_context':dict,
                    'connection_settings':dict,
                    'backup_path':str,
                    'local_test_folder':str,
                    }
        return required,{}

# lambda v: v if (v in self.corruption_types and type(v) is str) else self.do_raise("corruption"),
class TestConfig(ConnectionConfig):
    def decelium_path(self) ->str:
        return self['decelium_path']
    def obj_id(self) -> str:
        return self['obj_id']
    def eval_context(self) -> dict:
        return self['eval_context']
    
    def get_keys(self):
        super_required,optional = super().get_keys()
        required = {** super_required,
                    'decelium_path':str,
                    'obj_id':str,
                    'eval_context':dict,
                    }
        return required,optional

class DeploymentConfig(BaseData):
    def get_keys(self):
        required = {'server_address_config':ServerAddressConfig,
                    'branch':str,
                    'container_mode':str
                    }
        optional = {}
        return required,optional

class ServerAddressConfig(BaseData):
    def node_url(self):
        return f"{self['node_protocol']}://{self['host']}:{self['node_port']}/{self['node_url']}"
    
    def base_url(self):
        return f"{self['node_protocol']}://{self['host']}"
    
    def web_url(self):
        return f"{self['node_protocol']}://{self['host']}:{self['node_port']}/"
    
    def ipfs_connection_settings(self):
        return {
            'host':self['host'],
            'port':self['ipfs_port'],
            'protocol':self['ipfs_protocol'],
        }
    
    def get_host(self):
        return self['host']
    def get_port(self):
        return self['node_port']
    
    def get_protocol(self):
        return self['node_protocol']
    
    def get_keys(self):
        required = {
            'host':str,
            'node_port':str,
            'node_protocol':str,
            'node_url':str,
            'ipfs_port':str,
            'ipfs_protocol':str            
        }
        return required,{}

    def do_pre_process(self,in_dict):
        defaults = {
            'node_port':'5000',
            'node_protocol':'http',
            'node_url':'/data/query',
            'ipfs_port':'5001',
            'ipfs_protocol':'http'
        }
        for k in defaults:
            if not k in in_dict:
                in_dict[k] = defaults[k]
        return in_dict




class CommandResponse(BaseData):
    def debug_print(self):
        print(json.dumps({
            'status':self['status'],
            'response':self['response'],
                          },indent=1))
        print("STOUT")
        print(self['stout'])
        print("STERR")
        print(self['sterr'])

    def get_keys(self):
        required = {
                    'status':float, 
                    'response':dict, 
                    'stout':str,
                    'sterr':str
                    }
        return required,{}
    
''' 
EXAMPLES 
------

class AgentCommand(BaseData):
    def __init__(self,in_dict,trim=False):
        propagator_commands = ["validate","backup","append","status","purge_corrupt","push","repair","pull"]
        
        self.legal_commands = [
                         'gitpull','gitpush', # GIT (For Servers)
                         'test','redeploy','undeploy', # SERVER OPS (For servers)
                         'deploy_app', # APP OPS (For apps)
                         ]
        for pcommand in propagator_commands:
            self.legal_commands.append('p'+pcommand)
        super().__init__(in_dict,trim=False)
       
    def get_keys(self):
        required = {
                    'command':lambda v: v if (v in self.legal_commands and type(v) is str) else self.do_raise("Could not identify a valid commad type"),
                    }
        optional = {
                    'src_branch':str, 
                    'dst_branch':str, 
                    'src_server':str, 
                    'dst_server':str, 
                    'bck_id':str, 
                    }
        
        return required,optional


class Query(BaseData):
    f_messages = 'messages'
    f_model = 'model'
    f_max_tokens = 'max_tokens'
    f_temperature = 'temperature'
    f_openai_key = 'openai_key' 
    f_user_prompt = 'user_prompt' 
    f_context_marker = 'context_marker'
    c_system = 'system'
    c_assistant = 'assistant'
    c_user = 'user'
    
    def get_keys(self):
        # required, optional
        return {
            self.f_messages: list,
            self.f_model: str,
            self.f_max_tokens: int,
            self.f_temperature: float,
            self.f_openai_key: str,
            self.f_context_marker: str

        }, {
            self.f_user_prompt: str,
        }

    def clean(self):
        cleaned = super().clean()
        cleaned.pop(self.f_openai_key, None)
        cleaned.pop(self.f_user_prompt, None)
        cleaned.pop(self.f_context_marker, None)
        return cleaned
    
    def do_pre_process(self,in_dict):
        mspec = ChatGPTServiceSchema.Message
        qspec = ChatGPTServiceSchema.Query
        rspec = ChatGPTServiceSchema.Response
        if in_dict[qspec.f_user_prompt] in ["__integrated_a__","__integrated_b__","__ignored__"]:
            return in_dict
        # If you have no messages, create a default init
        if qspec.f_messages not in in_dict or in_dict[qspec.f_messages ] == None:
            in_dict[qspec.f_messages ] = []
            assert qspec.f_user_prompt in in_dict and in_dict[qspec.f_user_prompt] is not None, "Must provide user_prompt if messages are not set"
            in_dict[qspec.f_messages ]= [
                mspec({mspec.f_role: qspec.c_system, mspec.f_content: "You are a helpful assistant"}),
                mspec({mspec.f_role: qspec.c_user, mspec.f_content: in_dict[qspec.f_user_prompt]})
            ]
            in_dict[qspec.f_user_prompt] = "__integrated_a__"
        
        # If you have messages, append the prompt at the end
        elif qspec.f_user_prompt in in_dict and in_dict[qspec.f_user_prompt] is not None:
            assert type(in_dict[qspec.f_messages ] ) == list
            in_dict[qspec.f_messages].append(mspec({
                mspec.f_role: qspec.c_user,
                mspec.f_content: in_dict[qspec.f_user_prompt]
            }))
            in_dict[qspec.f_user_prompt] = "__integrated_b__"
        # If you have no f_user_prompt
        else:
            assert len(in_dict[qspec.f_messages]) > 0, "If you pass messages manually, they must not be empty"
            in_dict[qspec.f_user_prompt] = "__ignored__"

        if in_dict[qspec.f_openai_key] == None or qspec.f_openai_key not in in_dict :
            in_dict[qspec.f_openai_key] = "<<OPEN_AI_KEY>>"

        return in_dict

'''


class FloatRange(BaseData):
    f_min = "min"
    f_index = "index"
    f_max = "max"

    def get_keys(self):
        required = {
            self.f_min: float,
            self.f_index: float,
            self.f_max: float,
        }
        return required, {}

    def do_validation(self, key, value):
        if key in [self.f_min, self.f_index, self.f_max]:
            value = float(value)
        return value, ""

    def Set(self, value: float):
        clamped = max(self[self.f_min], min(self[self.f_max], value))
        super().__setitem__(self.f_index, clamped)

    def __setitem__(self, key, value):
        if key == self.f_index:
            self.Set(value)
        else:
            super().__setitem__(key, value)


#
# UPGRADE TASKS
#

'''
Here’s a focused list of the core schema-and-spec features you’ll want to layer into BaseData if you’re “reinventing” Pydantic-style validation and tooling:

1. **Declarative Field Metadata**

   * A `Field(...)` descriptor (or use `typing.Annotated`) carrying:

     * `default` value
     * `type` or `validator`
     * `alias` / `alias_priority`
     * `description` & `example`

2. **Automatic Type-Hint Parsing**

   * In `__init_subclass__`, read `__annotations__` (and any `Field` or `Annotated` metadata) to build your internal schema.
   * Support all typing constructs: `Union`, `Optional`, `Literal`, `List`, `Dict`, `Tuple`, nested `BaseData`, `Enum`, etc.

3. **Hooks & Validators**

   * Per-field validators (e.g. `@validator("x", pre=True/post=True)`)
   * Root validators (`@root_validator`) for cross-field checks
   * Allow custom‐callable converters that return converted value or raise

4. **Defaults & Required vs Optional**

   * Infer “required” from absence of a default
   * Populate defaults automatically before validation
   * Configurable “allow\_empty” / “allow\_extra” behavior

5. **Schema Introspection & JSON Schema Export**

   * A `.schema()` or `.json_schema()` method that emits a JSON-Schema dict with:

     * `title`, `type`, `properties`, `required`, `definitions` for nested models
     * `description` and `examples` pulled from your metadata

6. **OpenAPI / FastAPI Integration**

   * A helper to turn `.schema()` into a FastAPI model, or inject into an OpenAPI docs generator
   * Support for `response_model`, `request_body` schemas

7. **Serialization / Export**

   * `.dict()` / `.json()` methods honoring aliases, `exclude_unset`, `exclude_defaults`, `by_alias`
   * ISO formatting for `datetime` / `date` / `time` fields

8. **Config & Meta Options**

   * Class‐level `Config` for:

     * `orm_mode`, `allow_mutation`, `validate_assignment`
     * `alias_generator`, `use_enum_values`
     * `json_encoders` for custom types

9. **Performance & Caching**

   * Cache the generated schema and validators per class so you don’t re-inspect on each instantiation
   * Optionally compile hot paths (e.g. Cython or built-in type checks) later

10. **IDE & Documentation Support**

* Generate Sphinx or Markdown docs from your schema metadata
* Expose a `.__fields__` mapping so editors can autocomplete model attributes

---

**Next steps**:

* Introduce a `Field` class (or leverage `typing.Annotated`) and collect metadata in a metaclass or in `__init_subclass__`.
* Build your `.schema()` exporter by walking that metadata tree.
* Layer in decorator hooks (`@validator`, `@root_validator`) that attach to your field definitions.
* Expose `.dict()`/`.json()` with alias support.

That foundation will give you most of the Pydantic-style ecosystem without the external dependency.

'''
