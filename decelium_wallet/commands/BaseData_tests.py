import unittest
from decelium_wallet.commands.BaseData import BaseData  # adjust import
from typing import Union

class TestBaseDataInlineDefinitions(unittest.TestCase):
    def test_empty_default_constructor(self):
        class Empty(BaseData):
            def get_keys(self):
                return {}, {}
        e = Empty()
        self.assertEqual(dict(e), {})

    def test_dog_init_and_access(self):
        class Dog(BaseData):
            f_name = "name"
            f_age = "age"
            def get_keys(self):
                return {self.f_name: str}, {self.f_age: int}
        d = Dog({'name': 'Fido', 'age': 5})
        self.assertEqual(d[Dog.f_name], 'Fido')
        self.assertEqual(d[Dog.f_age], 5)
        with self.assertRaises(Exception):
            d = Dog({'name': 'Fido', 'age': "hello"})
        with self.assertRaises(Exception):
            d[d.f_age] = "should not assign"
            print( d[d.f_age])
        with self.assertRaises(Exception):
            _ = Dog({})  # missing required

    def test_dog_init_and_access_compact(self):
        class Dog(BaseData):
            f_name = "name"
            age:int
            def get_keys(self):
                return {self.f_name: str}, {}
        d = Dog({'name': 'Fido', 'age': 7})
        d.age = 5
        self.assertEqual(d[Dog.f_name], 'Fido')
        self.assertEqual(d["age"], 5)
        with self.assertRaises(Exception):
            d = Dog({'name': 'Fido', 'age': "hello"})
        with self.assertRaises(Exception):
            d["age"] = "should not assign"
            print( d["age"])
        with self.assertRaises(Exception):
            _ = Dog({})  # missing required            

    def test_nested_wrapping(self):
        class Dog(BaseData):
            f_name = "name"
            def get_keys(self):
                return {self.f_name: str}, {}
        class Owner(BaseData):
            f_dog = "dog"
            def get_keys(self):
                return {self.f_dog: Dog}, {}
        o = Owner({'dog': {'name': 'Max'}})
        self.assertIsInstance(o[Owner.f_dog], Dog)
        self.assertEqual(o[Owner.f_dog][Dog.f_name], 'Max')

    def test_typing(self):
        class TypingData(BaseData):
            f_x = "x"
            f_y = "y"
            x: Union[int, str]
            y: list[int]
            def get_keys(self):
                return {}, {}

        # passing cases
        t1 = TypingData({'x': 123, 'y': [1, 2, 3]})
        t2 = TypingData({'x': "hello", 'y': []})
        # failing cases
        with self.assertRaises(Exception):
            TypingData({'x': 1.23, 'y': [1]})
        with self.assertRaises(Exception):
            TypingData({'x': "ok", 'y': "notalist"})
        # assignment tests
        t1['x'] = "world"
        self.assertEqual(t1['x'], "world")
        with self.assertRaises(Exception):
            t1['y'] = ["ok", "bye", 99]

    def test_recursive_inner_dict(self):
        class Inner(BaseData):
            f_val = "val"
            def get_keys(self):
                return {self.f_val: int}, {}
        class Container(BaseData):
            f_inner = "inner"
            def get_keys(self):
                return {self.f_inner: Inner}, {}

        # dict input
        c = Container({'inner': {'val': 42}})
        self.assertIsInstance(c['inner'], Inner)
        self.assertEqual(c['inner']['val'], 42)
        # missing required
        with self.assertRaises(Exception):
            Container({})

    def test_recursive_inner_basedata(self):
        class Inner(BaseData):
            f_val = "val"
            def get_keys(self):
                return {self.f_val: int}, {}
        class Container(BaseData):
            f_inner = "inner"
            def get_keys(self):
                return {self.f_inner: Inner}, {}

        # BaseData instance input
        inner = Inner({'val': 7})
        c = Container({'inner': inner})
        self.assertIsInstance(c['inner'], Inner)


        # wrong BaseData type
        class Other(BaseData):
            f_val = "val"
            def get_keys(self):
                return {self.f_val: str}, {}
        with self.assertRaises(Exception):
            Container({'inner': Other({'val': 'oops'})})

    def test_recursive_inner_badbasedata(self):
        class InnerA(BaseData):
            f_val = "val"
            def get_keys(self):
                return {self.f_val: int}, {}
        class InnerB(BaseData):
            f_val = "val"
            def get_keys(self):
                return {self.f_val: int}, {}
        class Container(BaseData):
            f_inner = "inner"
            def get_keys(self):
                return {self.f_inner: InnerA}, {}

        # correct type
        c1 = Container({'inner': {'val': 1}})
        self.assertIsInstance(c1['inner'], InnerA)
        # wrong type instance
        b = InnerB({'val': 1})
        Container({'inner': b})
        self.assertIsInstance(c1['inner'], InnerA)

    def test_custom_lambda_error(self):
        class L(BaseData):
            f_x = "x"
            def get_keys(self):
                return {'x': lambda v: v > 0 or self.do_raise("must be positive")}, {}

        # passing
        L({'x': 10})
        # failing
        with self.assertRaises(Exception):
            L({'x': -1})

    def test_custom_lambda_success(self):
        class L(BaseData):
            f_x = "x"
            def get_keys(self):
                return {'x': lambda v: v if v % 2 == 0 else self.do_raise("must be even")}, {}
            
        # passing even value
        l = L({'x': 4})
        print(l)
        self.assertEqual(l['x'], 4)
        # failing odd
        with self.assertRaises(Exception):
            L({'x': 3})
    def test_custom_lambda_success_svlete(self):
        class L(BaseData):
            x: lambda v: v if v % 2 == 0 else self.do_raise("must be even")
            
        # passing even value
        l = L({'x': 4})
        print(l)
        self.assertEqual(l['x'], 4)
        # failing odd
        with self.assertRaises(Exception):
            L({'x': 3})

    def test_custom_lambda_success_svlete(self):
        class L(BaseData):
            x: lambda v: v if v % 2 == 0 else self.do_raise("must be even")
            
        # passing even value
        l = L(x=4)
        print(l)
        self.assertEqual(l['x'], 4)
        # failing odd
        with self.assertRaises(Exception):
            L(x=3)
        with self.assertRaises(Exception):
            l = L(x=4)
            l.x = 5
    def test_custom_lambda_named_instance_func(self):


        class L(BaseData):
            def validate_even(self,v):
                return v if v % 2 == 0 else self.do_raise("must be even")        
            x: validate_even

        # passing even value
        l = L(x=4)
        print(l)
        self.assertEqual(l['x'], 4)
        self.assertEqual(l.x, 4)
        # failing odd
        with self.assertRaises(Exception):
            L(x=3)
        with self.assertRaises(Exception):
            l = L(x=4)
            l.x = 5


    def test_custom_lambda_named_scope_func(self):


        def validate_even(v):
            return v if v % 2 == 0 else self.do_raise("must be even")        
        class L(BaseData):
            x: validate_even

        # passing even value
        l = L(x=4)
        print(l)
        self.assertEqual(l['x'], 4)
        # failing odd
        with self.assertRaises(Exception):
            L(x=3)
        with self.assertRaises(Exception):
            l = L(x=4)
            l.x = 5


    def test_custom_fieldname(self):

        def validate_even(v):
            return v if v % 2 == 0 else self.do_raise("must be even")        
        class L(BaseData):
            x: validate_even
        assert L.x == "x"
        l = L(x=10)
        assert l.x == 10


    def test_custom_fieldname_missing(self):

        def validate_even(v):
            return v if v % 2 == 0 else  None       
        class L(BaseData):
            x: (validate_even, None)
        assert L.x == "x"
        l = L()
        assert l.x == None
    def test_custom_fieldname_missing(self):
        from typing import Any
        class CommitExecution(BaseData):
            error:(Any,None)        
        ce = CommitExecution()
        assert ce.error == None
if __name__ == "__main__":
    unittest.main()
    #unittest.main(defaultTest="TestBaseDataInlineDefinitions.test_custom_fieldname")
