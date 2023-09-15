import sqlite3, json

'''
    elif  q['type'] == 'unset':

    DRAFTED:
    elif q['type'] == 'count':
    if q['type'] == 'distinct':
    elif q['type'] == 'upsert':
    elif  q['type'] == 'update':
    elif q['type'] == 'insert':
    elif q['type'] == 'find':
    elif q['type'] == 'insert_many':            
    elif q['type'] == 'delete':
'''

class nosqlite():

    def build_query(self, qtype, source, filterval=None, setval=None, limit=None, offset=None, field=None):
        print(qtype)
        if qtype == 'find':
            return self.sqlite_find( source, filterval, setval, limit, offset, field)
        if qtype == 'update':
            return self.sqlite_update_many( source, filterval, setval, limit, offset, field)
        if qtype == 'delete':
            return self.sqlite_delete_many( source, filterval, setval, limit, offset, field)
        if qtype == 'insert':
            return self.sqlite_insert(source, setval)        
        return {}
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
    
    def sqlite_count(self, source, filterval):
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

        return {"query": query, "args": tuple(args)}
    
    def sqlite_delete_many(self, source, filterval):
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
        set_conditions = []
        args = []

        for k, v in setval.items():
            # Since all keys are paths within the JSON, we always update within the JSON "value" column
            json_query = f"json_set(value, '$.{k}', ?)"
            set_conditions.append(json_query)
            args.append(v)

        set_str = ", ".join(set_conditions)

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
    
    def sqlite_insert(self, source, setval):
        table_name = source  # Assuming `source` is equivalent to the MongoDB collection name

        # Constructing the INSERT clause
        args = []
        json_data = {}
        for k, v in setval.items():
            # Inserting the entire data as a JSON object in the `value` column
            json_data[k] = v

        query = f"INSERT INTO {table_name} (value) VALUES (?)"
        args.append(json.dumps(json_data))  # Convert the dict to a JSON string

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

    def sqlite_upsert(self, source, filterval, setval):
        # First, attempt to retrieve the existing record
        find_result = self.sqlite_find(source, filterval, None, None, None, None)
        query = find_result["query"]
        args = find_result["args"]

        #existing_record = self.execute(query, args).fetchone()
        existing_record = None
        if existing_record:
            # Record exists, merge the data and update
            existing_data = json.loads(existing_record["value"])
            merged_data = self.merge_dicts(existing_data, setval)

            update_query = f"UPDATE {source} SET value = ? WHERE rowid = ?"
            args = (json.dumps(merged_data), existing_record["rowid"])
        else:
            # Record doesn't exist, insert new record
            insert_result = self.sqlite_insert(source, setval)
            update_query = insert_result["query"]
            args = insert_result["args"]

        return {"query": update_query, "args": args}
    
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
            str_value = json.dumps(value, sort_keys=True)

            if str_value not in distinct_vals:
                distinct_vals.add(str_value)
                distinct_results.append(result)

        return distinct_results    
    
if __name__=="__main__":
    db = nosqlite()
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
    print(sql)