from collections import OrderedDict
import random
from app import dbconnection
import base64
import io


class Memcache:
    def __init__(self, capacity = 128, policy = "LRU"):
        Flask(__name__)
        self.cache = OrderedDict()
        # configuration
        self.capacity = capacity
        self.policy = policy
        # statistics
        self.num_item = 0
        self.total_size = 0
        self.num_request = 0
        self.num_get = 0
        self.num_miss = 0


    


    def free_cache(self, item_size):
        # remove items until the new image can fit into the cache
        while item_size + self.total_size > self.capacity * 1024 * 1024:
            if self.policy == "LRU":
                item_to_remove = io.BytesIO(base64.b64decode(self.cache.popitem(last=False)))
            else:
                item_to_remove = io.BytesIO(base64.b64decode(self.cache.pop(random.choice(self.cache.keys()))))
            self.num_item -= 1
            
            item_to_remove.seek(0, 2)  # seeks the end of the file
            item_to_remove_size = item_to_remove.tell()  # tell at which byte we are
            item_to_remove.seek(0, 0)  # go back to the beginning of the file
            
            self.total_size -= item_to_remove_size





    def invalidate_key(self, key):
        self.num_request += 1
        if key in self.cache:
            item_to_remove = io.BytesIO(base64.b64decode(self.cache.pop(key)))
            self.num_item -= 1
            
            item_to_remove.seek(0, 2)  # seeks the end of the file
            item_to_remove_size = item_to_remove.tell()  # tell at which byte we are
            item_to_remove.seek(0, 0)  # go back to the beginning of the file

            self.total_size -= item_to_remove_size
            return 1
        else:
            return -1


    





    