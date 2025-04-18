import os
import json
from decelium_wallet.commands.BaseService import BaseService
from decelium_wallet.commands.BaseData import safe_open
from typing import Union, Dict
#
# A mistake that alyaws repeats, until you nail it (1% of the time): a home made graph DB.
# Why? Core needs
# - FIle system based, easy to combine with data and other elements, like GUI elements, Unity 3d, so that editor and plugin integration in a deep manner is possible
# - Nice, and easy, seperation between graphs and nodes
# - Optimized for file system ops, and mimimized operations and memory. It is stateless, and all the logic is built into the file system itself
# - Needs to support partial replication and commit batching, as well as decentralized synchronization in a P2P and untrusted environment
# ---- It should be possible to sync operations that have local effects, easily, from the rest of the system
# ---- It shoudd be possoble to easily accept, reject, and revert operations
# -------- Because the system is file system based, it is possible to add and remove graph portions via file system operations only. A partial invalid graph will have no global effects o
# -------- on the database or graph. This is ideal for miners, and nodes, as data can easily be added and discarded, without effecting many files. This makes the footprint of caching, hashes,
# -------- and P2P challenges easier to manage. Instead of each edit changing a whole database, or having to maintain a whole "record hash database" (with just record hashed [ahem: propagator, 6 months of work])
# -------- maybe it is possible to directly hash the nodes and edges, making it easier to version control and analyze
# -------- P2P network systems dont have a "search" or "list". its always a pain to model such systems on trad-dbs, because the natural first step is to (a) load the data and (b) search the data. However, when then
# -------- trying to adapt such systems for decentralized networks, one needs to handle the constant design challenge of either (a) blocking on long, unguarnteed, list operations which take forever to stub or
# -------- (b) creating elaborate cache management systems, that populate results of list (miny indexes). However, GraphData has no list functions -- its a "real" graph. You want 100 records? you have to explore the graph
# -------- This puts the indexing and searching problem higher in the application (where it belongs), and simplifies all aspects of the data model.
# -------- It is multi-threaded and multi-computer and multi-player by default -- the file system locking mechanism doesnt care if 10 or 1000 people attack the same graph, and even if they are on different computers, there are no barriers
# -------- will play well with git, and git status can be used to easily inspect what nodes have changed, including the ability for all the records and changes to be easily versioned. This means this whole DB can sit in git, and (MAYBE), managed 
# -------- via gits commit mechanism, including graceful rollbacks of data
# -------- Edges and Nodes are kept VERY seperate, meaning it is possible to edit nodes, edges, independently. This allows many logical graphs of relationships tp exist in harmony on top of the same data
# -------- No in memory process, or database process to manage, upgrade, and guard from hackers.

# Lastly: The implementation that hits most of this seems to be, what, 300 loc? Its a small tiny kernel that can be easily embedded into applications seamlessly.
# So motivation seems good. However lets see if any of this is as easy as it sounds ..... smells like dunning kruger.


from decelium_wallet.commands.BaseData import BaseData
''' 
Node
{
    "id": "node_id",
    "type": "type1",
    "data": {
        "key1": "value1",
        "key2": "value2"
    },
    "attached_groups": ["group_id_1", "group_id_2"]
}

'''
class Node(BaseData):
    def get_keys(self):
        required = {
            "node_id": str,
            "node_type_id": str,
            "data": dict,
            "attached_groups": list
        }
        optional = {}
        return required, optional
    
    def get_groups(self):
        return self["attached_groups"]
    
    def add_group(self,group_id:str):
        return self["attached_groups"].append(group_id)
    def remove_group(self,group_id:str):
        return self["attached_groups"].remove(group_id)
    
    def validate(self, graph):
        # Validate type
        node_config = graph.get_node_config(self["type"])
        assert node_config, f"Invalid node type: {self['type']}"
        
        # Validate allowed fields
        allowed_fields = node_config["allowed_fields"]
        for field in self["data"].keys():
            assert field in allowed_fields, f"Invalid field '{field}' for node type '{self['type']}'"
'''
Group
{
    "id": "group_id",
    "name": "Group Name",
    "type": "edge",
    "metadata": {
        "description": "Edge connecting two nodes",
        "created_at": "timestamp"
    },
    "members": [
        {"node_id": "node_id_1", "role": "source", "weight": 1.0},
        {"node_id": "node_id_2", "role": "target", "weight": 1.0}
    ]
}
'''

#class Group(BaseData):
#    def get_keys(self):
#        required = {
#            "group_type_id": str,
#            "name": str,
#            "members": list
#        }
#        optional = {}
#        return required, optional
#    
#    def get_node_ids(self):
#        ids = []
#        for member in self['members']:
#            ids.append(member["node_id"])
#        return ids
#    def do_validation(self,key,value,init_data):
#        if key == "members":
#            for item in value:
#                assert type(item) == dict
#                assert "node_id" in item
#                assert "role" in item
#                assert "weight" in item#
#
#        return value,""
class Group(BaseData):
    def get_keys(self):
        required = {
            "group_id": str,          # Added 'group_id' to required keys
            "group_type_id": str,
            "name": str,
            "members": list
        }
        optional = {}
        return required, optional

    def get_node_ids(self):
        return [member["node_id"] for member in self['members']]

    def add_member(self, member_info: dict):
        """
        Adds a new member to the group.

        :param member_info: A dictionary containing 'node_id', 'role', and 'weight'.
        """
        # Validate the member_info
        assert isinstance(member_info, dict), "member_info must be a dictionary"
        assert "node_id" in member_info, "member_info must contain 'node_id'"
        assert "role" in member_info, "member_info must contain 'role'"
        assert "weight" in member_info, "member_info must contain 'weight'"

        # Check if the node is already a member
        node_ids = self.get_node_ids()
        if member_info["node_id"] not in node_ids:
            self['members'].append(member_info)
        else:
            raise ValueError(f"Node '{member_info['node_id']}' is already a member of the group")

    def remove_member(self, node_id: str):
        """
        Removes a member from the group by node_id.

        :param node_id: The ID of the node to remove from the group's members.
        """
        original_length = len(self['members'])
        self['members'] = [member for member in self['members'] if member["node_id"] != node_id]
        if len(self['members']) == original_length:
            raise ValueError(f"Node '{node_id}' is not a member of the group")

    def do_validation(self, key, value, init_data):
        if key == "members":
            for item in value:
                assert isinstance(item, dict), "Each member must be a dictionary"
                assert "node_id" in item, "Each member must contain 'node_id'"
                assert "role" in item, "Each member must contain 'role'"
                assert "weight" in item, "Each member must contain 'weight'"

        return value, ""


''' Graph
{
    "id": "graph_id",
    "name": "Graph Name",
    "node_directory": "path_to_node_directory",
    "group_directory": "path_to_group_directory",
    "node_types": {
        "type1": {
            "allowed_fields": ["key1", "key2"],
            "description": "Type 1 description"
        },
        "type2": {
            "allowed_fields": ["keyA", "keyB"],
            "description": "Type 2 description"
        }
    },
    "group_types": {
        "edge": {
            "description": "An edge between two nodes",
            "min_members": 2,
            "max_members": 2
        },
        "region": {
            "description": "A region encompassing multiple nodes",
            "min_members": 3
        },
        "hierarchy": {
            "description": "A parent-child relationship",
            "min_members": 2
        }
    }
}


'''
class Graph(BaseData):
    def get_keys(self):
        required = {
            "id": str,
            "name": str,
            "node_directory": str,
            "group_directory": str,
            "node_types": dict,  # {type: {allowed_fields: list, description: str}}
            "group_types": dict  # {type: {description: str, min_members: int, max_members: int (optional)}}
        }
        optional = {}
        return required, optional
    
    def add_node_type(self,node_type_id,name):
        self["node_types"][node_type_id] = {"node_type_id": node_type_id, "name": name}        
        return True


    def add_group_type(self,group_type_id,name):
        self["group_types"][group_type_id] = {"group_type_id": group_type_id, "name": name}        
        return True
    
    def get_group_type(self,group_type_id):
        if group_type_id in self["group_types"]:
            return self["group_types"][group_type_id]
        return None        
    
    def get_node_type(self,node_type_id):
        if node_type_id in self["node_types"]:
            return self["node_types"][node_type_id]
        return None        


#
#
#
#
#
#

class GraphManager(BaseService):
    __data_types = {'Graph':Graph,
                    'Node':Node,
                    'Group':Group
                    }

    @classmethod
    def get_command_map(cls):
        return {
            'create_graph': { 'required_args': ['base_directory','graph_id','name'], 'method': cls.create_graph, },
            'add': { 'required_args': ['base_directory','data'], 'method': cls.add, },
            'remove': { 'required_args': ['base_directory', 'self_id',], 'method': cls.remove,}, ## FINISH AHD TEST
            'get': { 'required_args': ['base_directory', 'self_id',], 'method': cls.get,}, ## FINISH AHD TEST
            'add_group_type': { 'required_args': ['base_directory','group_type_id','name'], 'method': cls.add_group_type, },
            'add_node_type': { 'required_args': ['base_directory','node_type_id','name'], 'method': cls.add_node_type, },
        }
    
    @classmethod
    def __load_graph(cls, base_directory: str) -> Graph:
        graph_path = cls._get_file_path(base_directory, 'graph')
        print(graph_path)
        graph_data = cls._read_json_file(graph_path) 
        if graph_data == None:
            
            return None
        
        graph_data = Graph(graph_data)  # Validate against Graph type
        return graph_data

    @classmethod
    def __save_item(cls, base_directory: str, item:dict):
        
        if type(item) == Graph or issubclass(item,Graph):
            return cls._write_json_file(cls._get_file_path(base_directory, 'graph'), item)
        if type(item) == Node or issubclass(item,Node):
            return cls._write_json_file(cls._get_file_path(base_directory, 'node',f"{item['node_id']}"), item)
        if type(item) == Group or issubclass(item,Group):
            return cls._write_json_file(cls._get_file_path(base_directory, 'group',f"{item['group_id']}"), item)
        return False
    
  

    @classmethod
    def _get_file_path(cls, base_directory: str, file_type: str, identifier: str = None) -> str:
        print( os.path.join(base_directory, 'graph.json'))
        paths = {
            'graph': os.path.join(base_directory, 'graph.json'),
            'node': os.path.join(base_directory, 'nodes', f"{identifier}.json") if identifier else os.path.join(base_directory, 'nodes'),
            'group': os.path.join(base_directory, 'groups', f"{identifier}.json") if identifier else os.path.join(base_directory, 'groups'),
        }
        if file_type not in paths:
            raise ValueError(f"Unknown file type: {file_type}")
        return paths[file_type]

    @classmethod
    def _read_json_file(cls, file_path: str) -> Union[Dict, None]:
        if not os.path.exists(file_path):
            return None
        with safe_open(file_path, 'r') as file:
            return json.load(file)

    @classmethod
    def _write_json_file(cls, file_path: str, data: Dict):
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with safe_open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    
    @classmethod
    def __remove_json_file(cls, file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(file_path):
            raise Exception("COULD NOT REMOVE FILE file_path")
        return True
    
    #  base_directory: str, file_type: str, identifier:
    @classmethod
    def load_graph(cls, base_directory: str) -> Graph:
        return cls.__load_graph(base_directory)
    #  base_directory: str, file_type: str, identifier:

    @classmethod
    def create_graph(cls, graph_id: str, name: str, base_directory: str):
        graph_data = Graph({
            "id": graph_id,
            "name": name,
            "node_directory": cls._get_file_path(base_directory, 'node'),
            "group_directory": cls._get_file_path(base_directory, 'group'),
            "node_types": {},
            "group_types": {}
        })
        #navigation_group_type = {
        #    "group_type_id": "nav",
        #    "name": "NavigationLink",
        #    "required":["source_id","destination_id"]
        #}
        #cls.add_group_type({**navigation_group_type,"base_directory":base_directory})
        if os.path.exists(cls._get_file_path(base_directory, 'graph')):
            raise Exception("Can not create, graph already exists.")
        saved = cls.__save_item(base_directory, graph_data)
        if saved == False:
            raise Exception("Could not save new graph")
        saved = cls.add_group_type(base_directory=base_directory, 
                           group_type_id="navigation_link",
                           name="navigation")
        if saved == False:
            raise Exception("Could init the graph types ")
        
        return cls.__save_item(base_directory, graph_data)
        # print(f"Graph '{name}' created successfully at {cls._get_file_path(base_directory, 'graph')}")

    @classmethod
    def add(cls, base_directory: str, data: dict,type_id:str=None,overwrite=False):   
        if type(data) == str:
            data = json.loads(data)

        graph_data = cls.__load_graph(base_directory)
        if graph_data == None:
            raise Exception("Could not load graph")
            return False
        #
        if type_id != None:
            assert type_id in cls.__data_types, f"type {type_id} not registered with GraphManager"
            if type(data) == cls.__data_types[type_id] or  issubclass(type(data),cls.__data_types[type_id]):
                data = cls.__data_types[type_id](data)
            else:
                raise Exception(f"GraphManager.add error: Type '{type(data)}'is not same as type '{cls.__data_types[type_id]}'.")
        
        if issubclass(type(data),Node) or type(data) == Node:
            print("I Should be printing as a node")
            print(str(data)[0:100])
            # Has valid type
            node_type:dict = graph_data.get_node_type(data['node_type_id'])
            if node_type == None:
                raise ValueError(f"Node type '{node_type}' is not defined in the graph. Please use add_node_type first.")
            
            # Doesnt already exist
            file_path = cls._get_file_path(base_directory, 'node',f"{data['node_id']}")
            if overwrite == False and os.path.exists(file_path):
                raise Exception("Can not overwrite")
            
            # Save the Group
            added= cls._write_json_file(file_path, data)
            if added != True:
                raise Exception("Could not complete add operation")
        
        elif issubclass(type(data),Group) or type(data) == Group:
            # Has valid type
            graph_type:dict = graph_data.get_group_type(data['group_type_id'])
            if graph_type == None:
                raise ValueError(f"Group type '{data['group_type_id']}' is not defined in the graph. Please use add_group_type first.")
            
            # Doesnt already exist
            file_path = cls._get_file_path(base_directory, 'group',f"{data['group_id']}")            
            if overwrite == False and os.path.exists(file_path):
                raise Exception("Can not overwrite")
            
            # Save the Group
            group_path = cls._get_file_path(base_directory, 'group',f"{data['group_id']}")
            try:
                added = cls._write_json_file(group_path, data)
                if added != True:
                    raise Exception("Could not complete add operation")
                theGroup:Group = data
                linked_node_ids:list = theGroup.get_node_ids()
                for nid in linked_node_ids:
                    source_node:Node = cls.get(base_directory=base_directory,self_id=nid)
                    if source_node != None:
                        source_node.add_group(data['group_id'])
                        cls.add(base_directory=base_directory,
                                data=source_node,
                                overwrite=True)
                    
            except Exception as e:
                cls.__remove_json_file(group_path)
                raise e
            # Now we have to add the ID into the source and destination

        else:
            added= False
            if added != True:
                raise Exception("Could not complete add operation")
    '''
    @classmethod
    def remove(cls, base_directory: str,self_id:str=None):

        graph_data = cls.__load_graph(base_directory)
        if graph_data == None:
            raise Exception("Could not load graph")
            return False
        #
        if (self_id != None):
            print("removing item_id")
            os.remove(os.path.join(base_directory, 'nodes',f"{self_id}.json"))
            os.remove(os.path.join(base_directory, 'groups',f"{self_id}.json"))
            return True       
    '''
    @classmethod
    def remove(cls, base_directory: str, self_id: str = None):
        graph_data = cls.__load_graph(base_directory)
        if graph_data is None:
            raise Exception("Could not load graph")

        if self_id is None:
            raise ValueError("self_id must be provided for removal")

        # Determine if self_id corresponds to a node or a group
        node_file_path = cls._get_file_path(base_directory, 'node', f"{self_id}")
        group_file_path = cls._get_file_path(base_directory, 'group', f"{self_id}")

        if os.path.exists(node_file_path):
            # It's a node
            # Load the node
            node_data:Node = cls.get(base_directory=base_directory, self_id=self_id)
            if node_data is None:
                raise Exception(f"Node with id '{self_id}' not found")

            # Remove node file
            os.remove(node_file_path)

            # Update all groups that this node is a member of
            attached_group_ids = node_data.get_groups()
            for group_id in attached_group_ids:
                group_data:Group = cls.get(base_directory=base_directory, self_id=group_id)
                if group_data is not None:
                    # Remove the node from the group's members
                    group_data.remove_member(self_id)
                    if len(group_data['members']) == 0:
                        # Optionally remove the group if it has no more members
                        cls.remove(base_directory=base_directory, self_id=group_id)
                    else:
                        # Overwrite the group file with updated data
                        cls.add(base_directory=base_directory, data=group_data, overwrite=True)

        elif os.path.exists(group_file_path):
            # It's a group
            # Load the group
            group_data = cls.get(base_directory=base_directory, self_id=self_id)
            if group_data is None:
                raise Exception(f"Group with id '{self_id}' not found")

            # Remove group file
            os.remove(group_file_path)

            # Update all nodes that are members of this group
            member_node_ids = group_data.get_node_ids()
            for node_id in member_node_ids:
                node_data = cls.get(base_directory=base_directory, self_id=node_id)
                if node_data is not None:
                    # Remove the group from the node's attached_groups
                    node_data.remove_group(self_id)
                    # Overwrite the node file with updated data
                    cls.add(base_directory=base_directory, data=node_data, overwrite=True)
        else:
            raise Exception(f"No node or group found with id '{self_id}'")
        return True    
    
    @classmethod
    def get(cls, base_directory: str,self_id:str):
        graph_data = cls.__load_graph(base_directory)
        if graph_data == None:
            raise Exception(f"Could not load graph at {base_directory}")
        
        if (self_id == None):
            return False
        
        pth = os.path.join(base_directory, 'nodes',f"{self_id}.json")
        print(f"searching 1 in {pth}")
        if os.path.exists(pth):
            with safe_open(pth,'r') as f:
                return Node(json.loads(f.read()))
        
        pth = os.path.join(base_directory, 'groups',f"{self_id}.json")
        print(f"searching 2 in {pth}")
        if os.path.exists(pth):
            with safe_open(pth,'r') as f:
                return Group(json.loads(f.read()))
        return None
              
    @classmethod
    def add_group_type(cls, base_directory: str, group_type_id: str, name: str):
        graph_data = cls.__load_graph(base_directory)
        if graph_data == None:
            raise Exception("Could not load graph")

            return False
        graph_data.add_group_type(group_type_id,name)
        return cls.__save_item(base_directory,graph_data)

    @classmethod
    def add_node_type(cls, base_directory: str, node_type_id: str, name: str):
        graph_data = cls.__load_graph(base_directory)
        if graph_data == None:
            raise Exception("Could not load graph")
            return False
        graph_data.add_node_type(node_type_id,name)
        return cls.__save_item(base_directory, graph_data)

if __name__ == "__main__":
    GraphManager.run_cli()
# python3 graph_manager.py create_graph graph_id="test_graph" name="Test Graph" base_directory="./test_graph"
# python3 graph_manager.py add_node_type base_directory="./test_graph" name="simple_location" node_type_id="sim_locat"
# python3 graph_manager.py add base_directory="./test_graph" data='{"node_id": "n1", "node_type_id": "sim_locat", "data": "some/path","attached_groups": []}' type_id="Node"
# python3 graph_manager.py add base_directory="./test_graph" data='{"node_id": "n1",  "data": "some/path","attached_groups": []}'            