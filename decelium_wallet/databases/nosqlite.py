import sqlite3, json,uuid,datetime
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
        for k, v in dct.items():
            if isinstance(v, str) and "T" in v:
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

class nosqlite():


    def table_exists(self, table_name):
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
        result = self.execute(query, (table_name,)).fetchone()  # Assuming self.execute executes the SQL query and returns the result
        return bool(result)

    #def create_table(self, table_name):
    #    query = f"CREATE TABLE {table_name} (value TEXT);"
    #    self.execute(query)

    def __init__(self,path=None):
        # Connect to an in-memory SQLite database
        self.ID_FIELD = "_id"
        self.conn = sqlite3.connect(path if path else ':memory:')
        self.conn.row_factory = sqlite3.Row  # Access rows as dictionaries instead of tuples        
    
    def execute(self,qtype, source, filterval=None, setval=None, limit=None, offset=None, field=None):
        dat = self.build_query(qtype,source, filterval, setval, limit, offset, field)
        print(dat['query'])
        print(dat['args'])
        return self.__execute(dat['query'],dat['args'])
    
    def __execute(self, query, args_raw=None):
        """Execute a SQL query."""
        args = []
        if args_raw:
            for a in args_raw:
                if type(a) == datetime.datetime:
                    args.append(jsonwithdate.date_dump(a)) 
                else:
                    args.append(a) 

        with self.conn:
            cur = self.conn.cursor()
            if args:
                try:
                    cur.execute(query, args)
                except:
                    print("Could not execute Query," +str(query) + "," + str(args))
                    raise Exception("Could not execute Query :: " +str(query) + " :: " + str(args))
            else:
                cur.execute(query)
            
            # Return all rows if it's a SELECT; else, return nothing
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
    
    def ensure_table_exists(self, table_name):
        """Ensure a table exists or create it if not."""
        # This method only creates the table if it doesn't exist already
        create_table_query = f'''CREATE TABLE IF NOT EXISTS {table_name} (
                                '''+self.ID_FIELD+''' TEXT PRIMARY KEY UNIQUE,
                                value TEXT NOT NULL
                             )'''
        self.__execute(create_table_query)
    
    def build_query(self, qtype, source, filterval=None, setval=None, limit=None, offset=None, field=None):
        self.ensure_table_exists(source)
        if qtype == 'find':
            return self.sqlite_find( source, filterval, setval, limit, offset, field)
        if qtype == 'update':
            return self.sqlite_update_many( source, filterval, setval, limit, offset, field)
        if qtype == 'upsert':        
            return self.sqlite_upsert( source, filterval, setval, limit, offset, field)        
        if qtype == 'delete':
            return self.sqlite_delete_many( source, filterval, setval, limit, offset, field)
        if qtype == 'insert':
            return self.sqlite_insert(source, filterval, setval, limit, offset, field)    
        if qtype == 'count':
            return self.sqlite_count(source, filterval, setval, limit, offset, field)    
        raise Exception("No Query Selected")
    
    def sqlite_unset(self, source, filterval, setval):
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
        
        return {"query": query, "args": tuple(args)}
    
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
            

        return {"query": query, "args": tuple(args)}
    
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
        return {"query": query, "args": tuple(args)}

    def sqlite_update_many(self, source, filterval, setval, limit, offset, field):
        table_name = source  # Assuming `source` is equivalent to the MongoDB collection name

        # Constructing the SET clause
        set_conditions = ["value = json_set(value"]
        args = []

        for k, v in setval.items():
            # Since all keys are paths within the JSON, we always update within the JSON "value" column
            set_conditions.append(f"'$.{k}', ?")
            args.append(v)

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

        # Finalizing the UPDATE query
        query = f"UPDATE {table_name} SET {set_str} WHERE {where_str}"

        return {"query": query, "args": tuple(args)}

    
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

        return {"query": query, "args": tuple(args)}    
    
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

        return {"query": query, "args": tuple(args)}


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
        find_result = self.sqlite_find(source, filterval, None, None, None, None)
        query = find_result["query"]
        args = find_result["args"]

        existing_records = self.__execute(query, args)
        if len(existing_records) > 0:
            return self.sqlite_update_many( source, filterval, setval, limit, offset, field)
        else:
            return self.sqlite_insert(source, filterval, setval, limit, offset, field)
    
    def get_by_path(self, root, items):
        """Fetch nested key from dictionary using dot notation."""
        return reduce(lambda d, k: d[k], items, root)

    def sqlite_distinct_find(self, source, filterval, setval, limit, offset, field):
        # First, fetch all results
        results = self.sqlite_find(source, filterval, setval, limit, offset, field)

        # If a field for distinct is not specified, return the fetched results
        if not field:
            return results

        distinct_vals = set()
        distinct_results = []

        for result in results:
            # Extract the field's value using dot notation
            value = self.get_by_path(result, field.split('.'))

            # Convert the value to string to make it hashable for the set
            str_value = jsonwithdate.dumps(value, sort_keys=True)

            if str_value not in distinct_vals:
                distinct_vals.add(str_value)
                distinct_results.append(result)

        return distinct_results   

class TestSqliteConnector():    
    def test_init(self):
        db = nosqlite()
        '''
        q = {}
        q = {'qtype': "find",
            'source' : "transactions",
            'filterval' : {"id":{"$gt":10}},
            'setval' : None,
            'limit' : None,
            'offset' : None,
            'field' : None
            }
        sql = db.build_query( **q)
        print(sql)

        q = {'qtype': "find",
            'source' : "transactions",
            'filterval' : {"id":{"$gt":10}},
            'setval' : None,
            'limit' : 10,
            'offset' : 4,
            'field' : None
            }
        sql = db.build_query( **q)
        print(sql)

        q = {'qtype': "find",
            'source' : "transactions",
            'filterval' : {"id":{"$gt":10}},
            'setval' : None,
            'limit' : 10,
            'offset' : 4,
            'field' : None
            }
        sql = db.build_query( **q)

        q = {'qtype': "update",
            'source' : "transactions",
            'filterval' : {"id":{"$gt":10}},
            'setval' : {"name":"travis"},
            'field' : None
            }
        sql = db.build_query( **q)    

        q = {'qtype': "insert",
             'source' : "transactions",
             'setval' : {"id": 15, "name": "travis", "amount": 200}
             }
        sql = db.build_query( **q)    
        print(sql)    
        '''

        db.execute(**{'qtype': "insert",
             'source' : "transactions",
             'setval' : {"id": 15, "name": "travis", "amount": 200}
             })
        q = {'qtype': "find",
            'source' : "transactions",
            'filterval' : {"id":{"$gt":10}},
            'setval' : None,
            'limit' : None,
            'offset' : None,
            'field' : None
            }
        recs = db.execute( **q)
        
    def test_insert(self):
        # Test string, int, datetime,
        print("test_insert ...")
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
        print(rec)
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
        print(" pass")

    def test_date(self):
        print("test_insert ...")
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
        print("pass")
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
        print("pass")
        
    def test_update(self):
        db = nosqlite()
        print("test_insert ...")
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

        
    def test_upsert(self):
        db = nosqlite()
        print("test_insert ...")
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
        print("test_insert ...")
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
        '''
            -insert_many
        '''
        db = nosqlite()
        
    def test_distinct(self):
        '''
            -distinct
        '''
        db = nosqlite()
        
      
        
if __name__=="__main__": 
    tester = TestSqliteConnector()
    #tester.test_init()
    #tester.test_insert()
    #tester.test_date()
    #tester.test_save_restart()
    #tester.test_update()
    #tester.test_upsert()
    tester.test_count()