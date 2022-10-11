from collections import OrderedDict
import os
import random
from app import dbconnection

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

    def put(self, key, value, path):
        self.num_request += 1
        item_size = os.stat(path).st_size

        if item_size > self.capacity * 1024 * 1024:
            # image is too large
            return -1

        if key in self.cache:
            self.invalidate_key(key)

        self.free_cache(item_size)

        # add image into cache
        self.num_item += 1
        self.total_size += item_size
        self.cache[key] = value

        if self.policy == "LRU":
            self.cache.move_to_end(key)

        return 1
    
    def free_cache(self, item_size):
        # remove items until the new image can fit into the cache
        while item_size + self.total_size > self.capacity * 1024 * 1024:
            if self.policy == "LRU":
                item_to_remove = self.cache.popitem(last=False)
            else:
                item_to_remove = self.cache.pop(random.choice(self.cache.keys()))
            self.num_item -= 1
            self.total_size -= os.stat(item_to_remove).st_size

    def clear(self):
        self.num_request += 1
        self.num_item = 0
        self.total_size = 0
        self.cache.clear()

    def invalidate_key(self, key):
        self.num_request += 1
        if key in self.cache:
            item_to_remove = self.cache.pop(key)
            self.num_item -= 1
            self.total_size -= os.stat(item_to_remove).st_size
            return 1
        else:
            return -1

    def refreshConfiguration(self):
        # TODO: connect to DB and get value
        self.capacity = 0
        self.policy = 1
