from collections import OrderedDict
import os
import random
from app import dbconnection
import sys
import base64
import io


class Memcache:
    def __init__(self, capacity = 128, policy = "LRU"):
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


    def get(self, key):
        self.num_request += 1
        self.num_get += 1

        if key in self.cache:
            if self.policy == "LRU":
                self.cache.move_to_end(key)
            return self.cache[key]
        else:
            # unknown key
            self.num_miss += 1
            return -1


    def put(self, key, value):
        self.num_request += 1

        value.seek(0, 2)  # seeks the end of the file
        item_size = value.tell()  # tell at which byte we are
        value.seek(0, 0)  # go back to the beginning of the file

        if item_size > self.capacity * 1024 * 1024:
            # image is too large
            return -1

        if key in self.cache:
            self.invalidate_key(key)

        self.free_cache(item_size)

        # add image into cache
        self.num_item += 1
        self.total_size += item_size
        value = base64.b64encode(value.read())
        self.cache[key] = value

        if self.policy == "LRU":
            self.cache.move_to_end(key)

        return 1


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


    def clear(self):
        self.num_request += 1
        self.num_item = 0
        self.total_size = 0
        self.cache.clear()


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


    def set_config(self, capacity, policy):
        dbconnection.put_config(capacity, policy)
        self.capacity = capacity
        self.policy = policy
        self.free_cache(0)


    def show_stat(self):
        return dbconnection.show_stat()


    def period_update(self):
        dbconnection.put_stat(self.num_item, self.total_size, self.num_request, self.num_get, self.num_miss)