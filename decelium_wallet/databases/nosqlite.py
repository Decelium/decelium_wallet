import sqlite3, json,uuid,datetime
from functools import reduce
import re
from collections import deque

class jsonwithdate:
    def loads(dic):
        return json.loads(dic,object_hook=jsonwithdate.date_load)
    def dumps(dic):
        return json.dumps(dic,default=jsonwithdate.date_dump)

    def date_dump(o):
        if isinstance(o, tuple):
            l = ['__ref']
            l = l + o
            return l
        if isinstance(o, (datetime.date, datetime.datetime,)):
            return o.isoformat()

    def date_load(dct):
        DATE_FORMAT_WITH_MS = '%Y-%m-%dT%H:%M:%S.%f'
        DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
        ISO_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$')
        
        for k, v in dct.items():
            #if isinstance(v, str) and "T" in v:
            if isinstance(v, str) and ISO_REGEX.match(v):
                try:
                    dct[k] = datetime.datetime.strptime(v, DATE_FORMAT_WITH_MS)
                except ValueError:  # If the first format doesn't work, try the second one
                    import traceback as tb
                    tb.print_exc()
                    try:
                        dct[k] = datetime.datetime.strptime(v, DATE_FORMAT)
                    except ValueError:
                        pass
        return dct    


import copy,threading,queue

class NosqlThread():
    worker_thread = None
    
    def Instance():
        if NosqlThread.worker_thread is None or not NosqlThread.worker_thread.is_alive():
            NosqlThread.worker_thread = NosqlThread()
        return NosqlThread.worker_thread

    def threaded_execute(self, query, args_raw=None, path=None, timeout=None):
        correlation_id = str(uuid.uuid4())
        local_result_queue = queue.Queue()
        self.result_queues[correlation_id] = local_result_queue
        self.command_queue.put(("execute", (query, args_raw, correlation_id, path)))

        try:
            result = local_result_queue.get(timeout=timeout)  # Add timeout
        except queue.Empty:
            del self.result_queues[correlation_id]
            raise TimeoutError("Operation timed out")
        else:
            del self.result_queues[correlation_id]
            return result     

    def threaded_close(self, path=None, timeout=None):
        correlation_id = str(uuid.uuid4())
        local_result_queue = queue.Queue()
        self.result_queues[correlation_id] = local_result_queue
        self.command_queue.put(("terminate", (None, None, correlation_id, path)))

        try:
            result = local_result_queue.get(timeout=timeout)  # Add timeout
        except queue.Empty:
            del self.result_queues[correlation_id]
            raise TimeoutError("Operation timed out")
        else:
            del self.result_queues[correlation_id]
            return result
            
    def _worker(self):
        while True:
            command, args = self.command_queue.get()
            if command == "terminate":
                query, args_raw, correlation_id, path = args
                self.result_queues[correlation_id].put(True)
                break
            elif command == "execute":
                query, args_raw, correlation_id, path = args
                result = self.__execute(query, args_raw, path)
                self.result_queues[correlation_id].put(result)

    
    def __init__(self,path=None):
        self.command_queue = queue.Queue()
        self.result_queues = {}
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        self.conns = {}        
    
    def __execute(self, query, args_raw=None,path=None):
        """Execute a SQL query."""
        args = []
        assign_a_temp = []
        cnt = 0
        if args_raw:
            for a in args_raw:
                if type(a) == datetime.datetime:
                    args.append(jsonwithdate.date_dump(a)) 
                elif type(a) == dict:
                    args.append(jsonwithdate.dumps(a)) 
                    assign_a_temp.append(cnt)
                elif type(a) == list:
                    args.append(jsonwithdate.dumps(a)) 
                    assign_a_temp.append(cnt)
                elif type(a) == str:
                    args.append(a) 
                else:
                    args.append(a) 
                cnt = cnt + 1
        for b in args:
            try:
                assert (b is None) or (type(b) in [str,int,float])
            except Exception as e:
                print("Found an invalid argument "+ str(b) + " of type " + str(type(b)))
                raise e
        if path == None:
            path = ':memory:'
        if path not in self.conns:
            print(path)
            self.conns[path] = sqlite3.connect(path)
            self.conns[path].row_factory = sqlite3.Row
        conn = self.conns[path]
        with conn:
            cur = conn.cursor()
            if args:
                try:
                    res = cur.execute(query, args)
                except Exception as e:
                    print("Could not execute Query :: " +str(query) + " :: " + str(args))
                    raise e
            else:
                res = cur.execute(query)
            
            if query.lstrip().upper().startswith('SELECT') and not query.lstrip().upper().startswith('SELECT COUNT'):
                rows = []
                for row_in in cur.fetchall():
                    try:
                        row = jsonwithdate.loads(row_in[1])
                    except:
                        import traceback as tb
                        row = {"__db_error":"could not unpack row content "+tb.format_exc()}
                    rows.append(row)
                return rows
            if query.lstrip().upper().startswith('SELECT COUNT'):
                for row_in in cur.fetchall():
                    try:
                        val = int(row_in[0])
                    except:
                        import traceback as tb
                        val = {"__db_error":"could not unpack row content "+tb.format_exc()}
                    return val
            try:
                conn.commit()
            except:
                pass

class nosqlite():

    def __init__(self,path=None):
        self.ID_FIELD = "_id"
        self.kernel = NosqlThread()
        self.path = path
    
    def __execute(self, query, args_raw=None):
        """Execute a SQL query."""
        return self.kernel.threaded_execute(query=query, args_raw=args_raw,path=self.path)
        
    def __close(self):
        """Execute a SQL query."""
        return self.kernel.threaded_close(path=self.path)
        
    def close(self):
        return self.__close()
        
    def execute(self,qtype, source, filterval=None, setval=None, limit=None, offset=None, field=None):
        #print(" ")
        #print("Executing: "+ qtype)
        #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        
        try:
            filterval = copy.deepcopy(filterval)
        except:
            pass
        try:
            setval = copy.deepcopy(setval)
        except:
            pass
        
        if qtype == 'distinct':
            # Unfortunately, distinct breaks the pattern and has to operate manually in memory, not directly as a query
            return self.execute_sqlite_distinct(source, filterval, setval, limit, offset, field)    
        else:
            return self.run_query(qtype,source, filterval, setval, limit, offset, field)
                
    def ensure_table_exists(self, table_name):
        create_table_query = f'''CREATE TABLE IF NOT EXISTS {table_name} (
                                '''+self.ID_FIELD+''' TEXT PRIMARY KEY UNIQUE,
                                value TEXT NOT NULL
                             )'''
        self.__execute(create_table_query)
        
    def sqlite_insert_many(self, source, filterval, setval, limit=None, offset=None, field=None):
        table_name = source  # Assuming `source` is equivalent to the MongoDB collection name

        # Preparing the multi-row insert
        args = []
        queries = []
        assert type(setval) == list
        for record in setval:
            json_data = {}
            if not self.ID_FIELD in record:
                record[self.ID_FIELD] = str(uuid.uuid4())

            for k, v in record.items():
                json_data[k] = v

            queries.append(f"(?, ?)")
            args.append(record[self.ID_FIELD])
            args.append(jsonwithdate.dumps(json_data))  # Convert the dict to a JSON string

        insert_placeholders = ', '.join(queries)
        query = f"INSERT INTO {source} ({self.ID_FIELD}, value) VALUES {insert_placeholders}"
        
        return self.__execute(query,tuple(args))    
        #return {"query": query, "args": tuple(args)}
    
    def run_query(self, qtype, source, filterval=None, setval=None, limit=None, offset=None, field=None):
        self.ensure_table_exists(source)
        #             return self.__execute(dat['query'],dat['args'])

        if qtype == 'find':
            return self.sqlite_find( source, filterval, setval, limit, offset, field)#
        if qtype == 'update':
            return self.sqlite_update_many( source, filterval, setval, limit, offset, field)
        if qtype == 'upsert':        
            return self.sqlite_upsert( source, filterval, setval, limit, offset, field)        
        if qtype == 'delete':
            return self.sqlite_delete_many( source, filterval, setval, limit, offset, field)
        if qtype == 'insert':
            return self.sqlite_insert(source, filterval, setval, limit, offset, field)    
        if qtype == 'insert_many':
            return self.sqlite_insert_many(source, filterval, setval, limit, offset, field)    
        if qtype == 'count':
            return self.sqlite_count(source, filterval, setval, limit, offset, field)    
        if qtype == 'unset':
            return self.sqlite_unset(source, filterval, setval, limit, offset, field)    
        raise Exception("No Query Selected")
    
    def sqlite_unset(self, source, filterval, setval, limit, offset, field):
        table_name = source  # Assuming `source` is equivalent to the MongoDB collection name

        # Constructing the UNSET (remove) clause
        unset_conditions = []
        args = []

        for k in setval.keys():
            # Since all keys are paths within the JSON, we always modify within the JSON "value" column
            json_query = f"json_remove(value, '$.{k}')"
            unset_conditions.append(json_query)

        unset_str = ", ".join(unset_conditions)

        # Constructing the WHERE clause
        where_conditions = []

        if filterval:
            for k, v in filterval.items():
                # Since all attributes are inside the JSON field, we always query within the JSON "value" column
                json_query = f"json_extract(value, '$.{k}')"

                if isinstance(v, dict):  # MongoDB-style operators
                    for op, val in v.items():
                        if op == "$gt":
                            where_conditions.append(f"{json_query} > ?")
                        elif op == "$lt":
                            where_conditions.append(f"{json_query} < ?")
                        elif op == "$gte":
                            where_conditions.append(f"{json_query} >= ?")
                        elif op == "$lte":
                            where_conditions.append(f"{json_query} <= ?")
                        elif op == "$ne":
                            where_conditions.append(f"{json_query} != ?")
                        args.append(val)
                else:
                    where_conditions.append(f"{json_query} = ?")
                    args.append(v)

            where_str = " AND ".join(where_conditions)
        else:
            where_str = "1"  # If no filter is provided, default to true condition

        # Finalizing the UPDATE query
        query = f"UPDATE {table_name} SET value = {unset_str} WHERE {where_str}"
        return self.__execute(query,tuple(args)) 
        #return {"query": query, "args": tuple(args)}
    
    def sqlite_count(self,  source, filterval, setval, limit, offset, field):
        table_name = source  # Assuming `source` is equivalent to the MongoDB collection name

        query = f"SELECT COUNT(*) FROM {table_name}"
        args = []

        if filterval:
            conditions = []
            for k, v in filterval.items():
                # Since all attributes are inside the JSON field, we always query within the JSON "value" column
                json_query = f"json_extract(value, '$.{k}')"

                if isinstance(v, dict):  # MongoDB-style operators
                    for op, val in v.items():
                        if op == "$gt":
                            conditions.append(f"{json_query} > ?")
                        elif op == "$lt":
                            conditions.append(f"{json_query} < ?")
                        elif op == "$gte":
                            conditions.append(f"{json_query} >= ?")
                        elif op == "$lte":
                            conditions.append(f"{json_query} <= ?")
                        elif op == "$ne":
                            conditions.append(f"{json_query} != ?")
                        # ... Add more operators as needed
                        args.append(val)
                else:
                    conditions.append(f"{json_query} = ?")
                    args.append(v)

            conditions_str = " AND ".join(conditions)
            query += f" WHERE {conditions_str}"
        else:
            query += f" WHERE 1"
            
        return self.__execute(query,tuple(args)) 
        #return {"query": query, "args": tuple(args)}
    
    def sqlite_delete_many(self, source, filterval, setval, limit, offset, field):
        table_name = source  # Assuming `source` is equivalent to the MongoDB collection name

        query = f"DELETE FROM {table_name}"
        args = []

        if filterval:
            where_conditions = []
            for k, v in filterval.items():
                # Since all attributes are inside the JSON field, we always query within the JSON "value" column
                json_query = f"json_extract(value, '$.{k}')"

                if isinstance(v, dict):  # MongoDB-style operators
                    for op, val in v.items():
                        if op == "$gt":
                            where_conditions.append(f"{json_query} > ?")
                        elif op == "$lt":
                            where_conditions.append(f"{json_query} < ?")
                        elif op == "$gte":
                            where_conditions.append(f"{json_query} >= ?")
                        elif op == "$lte":
                            where_conditions.append(f"{json_query} <= ?")
                        elif op == "$ne":
                            where_conditions.append(f"{json_query} != ?")
                        args.append(val)
                else:
                    where_conditions.append(f"{json_query} = ?")
                    args.append(v)

            where_str = " AND ".join(where_conditions)
            query += f" WHERE {where_str}"
        return self.__execute(query,tuple(args))    
        # return {"query": query, "args": tuple(args)}
    def extract_leaves(self,data):
        leaves = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                leaves.extend(self.extract_leaves(value))
        elif isinstance(data, list):
            for item in data:
                leaves.extend(self.extract_leaves(item))
        else:
            leaves.append(data)
        
        return leaves
    def replace_leaves_with_placeholder(self,data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self.replace_leaves_with_placeholder(value)
                else:
                    data[key] = "?"
        elif isinstance(data, list):
            for i in range(len(data)):
                if isinstance(data[i], (dict, list)):
                    self.replace_leaves_with_placeholder(data[i])
                else:
                    data[i] = "?"
        else:
            return "?"
    
        return data    

    def convert_json_to_sqlite(self,a):
        obj = copy.deepcopy(a)
        leaves = self.extract_leaves(obj)
        obj = self.replace_leaves_with_placeholder(obj)
        obj = jsonwithdate.dumps(obj)
        obj = obj.replace('"',"'")
        obj = obj.replace("{","json_object(")
        obj = obj.replace("}",")")
        obj = obj.replace("[","json_array(")
        obj = obj.replace("]",")")
        obj = obj.replace("'?'","?")
        obj = obj.replace(":",",")
        return obj,leaves

    def sqlite_update_many(self, source, filterval, setval, limit, offset, field):
        existing_records = self.sqlite_find(source, filterval, None, None, None, None)
        for rec in existing_records:
            new_rec = self.merge_dicts(rec,setval)
            self.sqlite_delete_many(source, {"_id":rec["_id"]}, None, None, None, None)
            self.sqlite_insert(source, None, new_rec, None, None, None)
        return True
    
    def sqlite_update_many_old(self, source, filterval, setval, limit, offset, field):
        table_name = source  # Assuming `source` is equivalent to the MongoDB collection name

        # Constructing the SET clause
        set_conditions = ["value = json_set(value"]
        args = []

        for k, a in setval.items():
            if type(a) == datetime.datetime:
                set_conditions.append(f"'$.{k}', ?")
                args.append(a) 
            elif type(a) == dict:
                obj, leaves = self.convert_json_to_sqlite(a)                
                set_conditions.append(f"'$.{k}', "+obj)
                for l in leaves:
                    args.append(l) 
            elif type(a) == list:
                obj, leaves = self.convert_json_to_sqlite(a)                
                set_conditions.append(f"'$.{k}', "+obj)
                for l in leaves:
                    args.append(l) 
            elif type(a) == str:
                set_conditions.append(f"'$.{k}', ?")
                args.append(a) 
            else:
                set_conditions.append(f"'$.{k}', ?")      
                args.append(a) 
        
        set_str = ", ".join(set_conditions) + ")"  # closing bracket for json_set is appended here

        # Constructing the WHERE clause
        where_conditions = []

        if filterval:
            for k, v in filterval.items():
                # Since all attributes are inside the JSON field, we always query within the JSON "value" column
                json_query = f"json_extract(value, '$.{k}')"

                if isinstance(v, dict):  # MongoDB-style operators
                    for op, val in v.items():
                        if op == "$gt":
                            where_conditions.append(f"{json_query} > ?")
                        elif op == "$lt":
                            where_conditions.append(f"{json_query} < ?")
                        elif op == "$gte":
                            where_conditions.append(f"{json_query} >= ?")
                        elif op == "$lte":
                            where_conditions.append(f"{json_query} <= ?")
                        elif op == "$ne":
                            where_conditions.append(f"{json_query} != ?")
                        args.append(val)
                else:
                    where_conditions.append(f"{json_query} = ?")
                    args.append(v)

            where_str = " AND ".join(where_conditions)
        else:
            where_str = "1"  # If no filter is provided, default to true condition (this means all records will be updated)

        query = f"UPDATE {table_name} SET {set_str} WHERE {where_str}"
        return self.__execute(query,tuple(args))
    
    def sqlite_insert(self, source, filterval, setval, limit, offset, field):
        table_name = source  # Assuming `source` is equivalent to the MongoDB collection name

        # Constructing the INSERT clause
        args = []
        json_data = {}
        if not self.ID_FIELD in setval:
            setval[self.ID_FIELD] = str(uuid.uuid4())
        
        for k, v in setval.items():
            # Inserting the entire data as a JSON object in the `value` column
            json_data[k] = v

        query = f"INSERT INTO {table_name} ("+self.ID_FIELD+", value) VALUES (?, ?)"
        args.append(setval[self.ID_FIELD])
        args.append(jsonwithdate.dumps(json_data))  # Convert the dict to a JSON string
        return self.__execute(query,tuple(args))
        #return {"query": query, "args": tuple(args)}    
    
    def sqlite_find(self, source, filterval, setval, limit, offset, field):
        table_name = source  # Assuming `source` is equivalent to the MongoDB collection name

        query = f"SELECT * FROM {table_name}"
        args = []
        if filterval:
            conditions = []
            for k, v in filterval.items():
                # Since all attributes are inside the JSON field, we always query within the JSON "value" column
                json_query = f"json_extract(value, '$.{k}')"
                
                
                if isinstance(v, dict):  # MongoDB-style operators
                    for op, val in v.items():
                        if op == "$gt":
                            conditions.append(f"{json_query} > ?")
                        elif op == "$lt":
                            conditions.append(f"{json_query} < ?")
                        elif op == "$gte":
                            conditions.append(f"{json_query} >= ?")
                        elif op == "$lte":
                            conditions.append(f"{json_query} <= ?")
                        elif op == "$ne":
                            conditions.append(f"{json_query} != ?")
                        # ... Add more operators as needed
                        args.append(val)
                else:
                    conditions.append(f"{json_query} = ?")
                    args.append(v)

            conditions_str = " AND ".join(conditions)
            query += f" WHERE {conditions_str}"

        if limit:
            query += f" LIMIT ?"
            args.append(limit)

        if offset:
            query += f" OFFSET ?"
            args.append(offset)
            
        return self.__execute(query,tuple(args))


    def merge_dicts(self, d1, d2):
        """Recursively merge two dictionaries."""
        for k, v in d2.items():
            if isinstance(v, dict) and k in d1 and isinstance(d1[k], dict):
                d1[k] = self.merge_dicts(d1[k], v)
            else:
                d1[k] = v
        return d1

    def sqlite_upsert(self, source, filterval, setval, limit, offset, field):
        # First, attempt to retrieve the existing record
        existing_records = self.sqlite_find(source, filterval, None, None, None, None)

        if len(existing_records) > 0:
            return self.sqlite_update_many( source, filterval, setval, limit, offset, field)
        else:
            return self.sqlite_insert(source, filterval, setval, limit, offset, field)
    
    def get_by_path(self, root, items):
        return reduce(lambda d, k: d[k], items, root)
    
    def execute_sqlite_distinct(self, source, filterval, setval, limit, offset, field):
        if not field or not isinstance(field, str):
            return {"error": "Please include a field as a string"}

        # Fetch all the records from the table
        existing_records = self.sqlite_find(source, filterval, None, limit, offset, field)

        distinct_values = set()
        keys = field.split('.')  # Convert dot-notation to list
        for record in existing_records:
            try:
                value = self.get_by_path(record, keys)
                distinct_values.add(value)
            except KeyError:
                pass
        return list(distinct_values)
    

class TestSqliteConnector():    
        
    def test_insert(self):
        # Test string, int, datetime,
        db = nosqlite()
        db.execute(**{'qtype': "insert",
             'source' : "transactions",
             'setval' : {"id": 15, "name": "travis", "amount": 200}
             })
        db.execute(**{'qtype': "insert",
             'source' : "transactions",
             'setval' : {"id": 9, "name": "travis", "amount": 200}
             })
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {}})        
        assert len(res) == 2
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {"id":{"$gt":9}}
            })
        assert len(res) == 1
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {"id":{"$gte":9}}
            })
        assert len(res) == 2
        db.execute(**{'qtype': "delete",
            'source' : "transactions",
            'filterval' : {"id":{"$gt":9}}
            })
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {"id":{"$gt":9}}
            })
        assert len(res) == 0
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {"id":{"$lte":9}}
            })
        assert len(res) == 1
        rec = res[0]
        db.execute(**{'qtype': "delete",
            'source' : "transactions",
            'filterval' : {"_id":rec["_id"]}
            })        
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {"id":{"$lte":9}}
            })
        assert len(res) == 0
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {}
            })
        assert len(res) == 0
        del(db)

    def test_date(self):
        db = nosqlite()
        dt = datetime.datetime.utcnow()
        db.execute(**{'qtype': "insert",
             'source' : "transactions",
             'setval' : {"id": 15, 
                         "name": "travis", 
                         "amount": 200,
                        "date":dt}
             })
        db.execute(**{'qtype': "insert",
             'source' : "transactions",
             'setval' : {"id": 9, "name": "travis", "amount": 200}
             })
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {"date":dt}})
        assert res[0]["date"] == dt
        assert len(res) == 1
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {"date":datetime.datetime.utcnow()}})
        assert len(res) == 0
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {"date":{"$lt":datetime.datetime.utcnow()}}})
        assert len(res) == 1
        del(db)
        
    def test_save_restart(self):
        # Delete the file if it exists
        try:
            import os
            os.remove("./test.db")
        except FileNotFoundError:
            pass
        db = nosqlite("./test.db")
        db.execute(**{'qtype': "insert",
             'source' : "transactions",
             'setval' : {"id": 9, "name": "travis", "amount": 200}
             })
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {}})
        assert len(res) == 1
        del(db)
        db = nosqlite("./test.db")
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {}})
        assert len(res) == 1
        db.execute(**{'qtype': "delete",
            'source' : "transactions",
            'filterval' : {}})
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {}})
        assert len(res) == 0
        
    def test_update(self):
        db = nosqlite()
        db = nosqlite()
        db.execute(**{'qtype': "insert",
             'source' : "transactions",
             'setval' : {"id": 9, "name": "travis", "amount": 200}
             })
        db.execute(**{'qtype': "update",
             'source' : "transactions",
             'filterval':{"id": 9},
             'setval' : {"amount": 500}
             })
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {}})        
        assert len(res) == 1
        assert res[0]["amount"] == 500
        assert res[0]["name"] == "travis"

    def test_update_dict(self): 
        db = nosqlite()
        update_settings = {'ipfs_cid': 'QmQDcMyPKqYZmnoVu8VyGTuCW4oYfX4JPEECJRN4VhxfbZ', 'ipfs_name': 'obj-c4e11714-d35a-44a6-bd20-fa9bb608460a' }    
        db.execute(**{'qtype': "insert",
             'source' : "transactions",
             'setval' : {"id": 9, "name": "travis", "amount": 200}
             })
        db.execute(**{'qtype': "update",
             'source' : "transactions",
             'filterval':{"id": 9},
             'setval' : {"settings":update_settings }
             })
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {}})   

        import pprint
        pprint.pprint(res)
        assert len(res) == 1
        assert res[0]["amount"] == 200
        assert res[0]["name"] == "travis"
        print(type(res[0]["settings"]))
        assert type(res[0]["settings"]) == dict
        assert res[0]["settings"]["ipfs_cid"] == "QmQDcMyPKqYZmnoVu8VyGTuCW4oYfX4JPEECJRN4VhxfbZ"
             
        db.execute(**{'qtype': "update",
             'source' : "transactions",
             'filterval':{"id": 9},
             'setval' : {"settings.ipfs_cid":[10,20,30] }
             })
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {}})     

        print(res)
        assert type(res[0]["settings"]) == dict
        assert type(res[0]["settings"]["ipfs_cid"]) == list
        assert res[0]["settings"]["ipfs_cid"][0] == 10

    def test_upsert(self):
        db = nosqlite()
        db.execute(**{'qtype': "insert",
             'source' : "transactions",
             'setval' : {"id": 9, "name": "travis", "amount": 200}
             })
        db.execute(**{'qtype': "upsert",
             'source' : "transactions",
             'filterval':{"id": 9},
             'setval' : {"amount": 500}
             })
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {}})        
        assert len(res) == 1
        assert res[0]["amount"] == 500
        assert res[0]["name"] == "travis"
        res = db.execute(**{'qtype': "delete",
            'source' : "transactions",
            'filterval' : {}})  
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {}})           
        assert len(res) == 0
        db.execute(**{'qtype': "upsert",
             'source' : "transactions",
             'setval' : {"id": 9, "name": "bravis", "amount": 100}
             })
        db.execute(**{'qtype': "upsert",
             'source' : "transactions",
             'filterval':{"id": 90},                      
             'setval' : {"id": 90, "name": "bravis", "amount": 1000}
             })
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {"id": 9}}) 
        assert len(res) == 1
        assert res[0]["amount"] == 100
        assert res[0]["name"] == "bravis"
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {"id": 90}}) 
        assert len(res) == 1
        assert res[0]["amount"] == 1000
        assert res[0]["name"] == "bravis"        
        del(db)
        
        
        
    def test_count(self):
        db = nosqlite()
        db = nosqlite()
        db.execute(**{'qtype': "insert",
             'source' : "transactions",
             'setval' : {"id": 9, "name": "travis", "amount": 200}
             })
        db.execute(**{'qtype': "insert",
             'source' : "transactions",
             'setval' : {"id": 90, "name": "travis", "amount": 200}
             })
        res = db.execute(**{'qtype': "count",
            'source' : "transactions",
            'filterval' : {}}) 
        assert res == 2
        res = db.execute(**{'qtype': "count",
            'source' : "transactions",
            'filterval' : {"id":{"$gt":9}}})        
        assert res == 1
        del(db)
        
        
    def test_insert_many(self):
        db = nosqlite()
        db.execute(**{'qtype': "insert_many",
             'source' : "transactions",
             'setval' : [
                         {"id": 9, "name": "travis", "amount": 200},
                         {"id": 10, "name": "bravis", "amount": 300},
                         {"id": 11, "name": "cravis", "amount": 400}
                        ]
             })
        res = db.execute(**{'qtype': "count",
            'source' : "transactions",
            'filterval' : {}})
        assert res == 3
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {"id":10}})  
        assert res[0]["name"] == "bravis"
        del(db)
        
        
    def test_distinct(self):
        db = nosqlite()
        db.execute(**{'qtype': "insert_many",
             'source' : "transactions",
             'setval' : [
                         {"id": 9, "category": "a", "amount": 200},
                         {"id": 10, "category": "a", "amount": 300},
                         {"id": 11, "category": "a", "amount": 300},
                         {"id": 12, "category": "b", "amount": 300},
                         {"id": 13, "category": "b", "amount": 300},
                         {"id": 14, "category": "b", "amount": 400}
                        ]
             })
        res = db.execute(**{'qtype': "distinct",
            'source' : "transactions",
            'filterval' : {"category":"a"},
            'field':"amount"})    
        assert len(res) == 2
        assert 200 in res
        assert 300 in res
        
    def test_unset(self):
        db = nosqlite()
        db.execute(**{'qtype': "insert_many",
             'source' : "transactions",
             'setval' : [
                         {"id": 9, "category": "a", "amount": 200},
                         {"id": 10, "category": "a", "amount": 300},
                         {"id": 11, "category": "a", "amount": 300},
                         {"id": 12, "category": "b", "amount": 300},
                         {"id": 13, "category": "b", "amount": 300},
                         {"id": 14, "category": "b", "amount": 400}
                        ]
             })
        db.execute(**{'qtype': "unset",
            'source' : "transactions",
            'setval':{"amount":None},
            'filterval' : {"category":"a"}}) 
        res = db.execute(**{'qtype': "find",
            'source' : "transactions",
            'filterval' : {"category":"a"}})          
        
if __name__=="__main__": 
    conTester = TestSqliteConnector()
    
    conTester.test_insert()
    conTester.test_date()
    conTester.test_save_restart()
    conTester.test_update()
    conTester.test_upsert()
    conTester.test_count()
    conTester.test_insert_many()
    conTester.test_distinct()    
    conTester.test_unset()
    conTester.test_update_dict()