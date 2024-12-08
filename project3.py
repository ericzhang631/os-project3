import os

def write_uint64_be(value):
    return value.to_bytes(8, 'big', signed=False)

def read_uint64_be(data):
    return int.from_bytes(data, 'big', signed=False)

class IndexFile:
    BLOCK_SIZE = 512
    MAGIC = b'4337PRJ3'

    def __init__(self):
        self.fp = None
        self.is_open = False
        self.root_block_id = 0
        self.next_block_id = 1
        self.filename = None

    @staticmethod
    def file_exists(filename):
        return os.path.exists(filename)

    def create(self, filename):
        try:
            with open(filename, 'w+b') as f:
                block = bytearray(self.BLOCK_SIZE)
                block[0:8] = self.MAGIC
                block[8:16] = write_uint64_be(0)
                block[16:24] = write_uint64_be(1)
                f.seek(0)
                written = f.write(block)
                f.flush()
                if written != self.BLOCK_SIZE:
                    return False
        except IOError:
            return False
        return True

    def open(self, filename):
        if not self.file_exists(filename):
            return False
        try:
            self.fp = open(filename, 'r+b')
        except IOError:
            return False
        self.filename = filename
        self.is_open = True
        if not self.read_header():
            self.close()
            return False
        if not self.check_magic_number():
            self.close()
            return False
        return True

    def close(self):
        if self.is_open and self.fp is not None:
            self.fp.close()
            self.fp = None
        self.is_open = False

    def write_header(self):
        if not self.is_open:
            return False
        block = bytearray(self.BLOCK_SIZE)
        block[0:8] = self.MAGIC
        block[8:16] = write_uint64_be(self.root_block_id)
        block[16:24] = write_uint64_be(self.next_block_id)
        self.fp.seek(0)
        written = self.fp.write(block)
        self.fp.flush()
        return written == self.BLOCK_SIZE

    def read_header(self):
        if not self.is_open:
            return False
        self.fp.seek(0)
        block = self.fp.read(self.BLOCK_SIZE)
        if len(block) != self.BLOCK_SIZE:
            return False
        self.root_block_id = read_uint64_be(block[8:16])
        self.next_block_id = read_uint64_be(block[16:24])
        return True

    def check_magic_number(self):
        if not self.is_open:
            return False
        self.fp.seek(0)
        magic = self.fp.read(8)
        return magic == self.MAGIC

    def write_block(self, block_id, data):
        if not self.is_open:
            return False
        if len(data) != self.BLOCK_SIZE:
            return False
        try:
            self.fp.seek(block_id * self.BLOCK_SIZE)
            written = self.fp.write(data)
            self.fp.flush()
            return written == self.BLOCK_SIZE
        except:
            return False

    def read_block(self, block_id):
        if not self.is_open:
            return b''
        try:
            self.fp.seek(block_id * self.BLOCK_SIZE)
            data = self.fp.read(self.BLOCK_SIZE)
            if len(data) == self.BLOCK_SIZE:
                return data
            else:
                return b''
        except:
            return b''

class BTreeNode:
    def __init__(self):
        self.block_id = 0
        self.parent_id = 0
        self.num_keys = 0
        self.keys = [0]*19
        self.values = [0]*19
        self.children = [0]*20

    def to_bytes(self):
        b = bytearray(512)
        b[0:8] = write_uint64_be(self.block_id)
        b[8:16] = write_uint64_be(self.parent_id)
        b[16:24] = write_uint64_be(self.num_keys)
        pos = 24
        for i in range(19):
            b[pos:pos+8] = write_uint64_be(self.keys[i])
            pos+=8
        for i in range(19):
            b[pos:pos+8] = write_uint64_be(self.values[i])
            pos+=8
        for i in range(20):
            b[pos:pos+8] = write_uint64_be(self.children[i])
            pos+=8
        return b

    def from_bytes(self, data):
        self.block_id = read_uint64_be(data[0:8])
        self.parent_id = read_uint64_be(data[8:16])
        self.num_keys = read_uint64_be(data[16:24])
        pos = 24
        for i in range(19):
            self.keys[i] = read_uint64_be(data[pos:pos+8])
            pos+=8
        for i in range(19):
            self.values[i] = read_uint64_be(data[pos:pos+8])
            pos+=8
        for i in range(20):
            self.children[i] = read_uint64_be(data[pos:pos+8])
            pos+=8

    def is_leaf(self):
        for c in self.children:
            if c != 0:
                return False
        return True

class BTree:
    def __init__(self, index_file):
        self.index_file = index_file
        if self.index_file.root_block_id == 0:
            self.create_root()

    def create_root(self):
        node = BTreeNode()
        node.block_id = self.index_file.next_block_id
        self.index_file.next_block_id += 1
        self.index_file.write_header()
        self.save_node(node)
        self.index_file.root_block_id = node.block_id
        self.index_file.write_header()

    def load_node(self, block_id):
        data = self.index_file.read_block(block_id)
        if len(data) != 512:
            return None
        node = BTreeNode()
        node.from_bytes(data)
        return node

    def save_node(self, node):
        data = node.to_bytes()
        self.index_file.write_block(node.block_id, data)

    def search(self, key):
        return self._search_node(self.index_file.root_block_id, key)

    def _search_node(self, block_id, key):
        if block_id == 0:
            return None
        node = self.load_node(block_id)
        if node is None:
            return None
        i = 0
        while i < node.num_keys and key > node.keys[i]:
            i+=1
        if i < node.num_keys and key == node.keys[i]:
            return node.values[i]
        if node.is_leaf():
            return None
        return self._search_node(node.children[i], key)

    def insert(self, key, value):
        if self.index_file.root_block_id == 0:
            self.create_root()
        root = self.load_node(self.index_file.root_block_id)
        if root.num_keys == 19:
            new_root = BTreeNode()
            new_root.block_id = self.index_file.next_block_id
            self.index_file.next_block_id+=1
            new_root.children[0] = root.block_id
            root.parent_id = new_root.block_id
            self.save_node(root)
            self.split_child(new_root, 0)
            self.save_node(new_root)
            self.index_file.root_block_id = new_root.block_id
            self.index_file.write_header()
            self.insert_nonfull(new_root, key, value)
        else:
            self.insert_nonfull(root, key, value)

    def insert_nonfull(self, node, key, value):
        while True:
            if node.is_leaf():
                i = node.num_keys - 1
                while i >= 0 and node.keys[i] > key:
                    node.keys[i+1] = node.keys[i]
                    node.values[i+1] = node.values[i]
                    i-=1
                if i>=0 and node.keys[i] == key:
                    self.save_node(node)
                    return
                node.keys[i+1] = key
                node.values[i+1] = value
                node.num_keys+=1
                self.save_node(node)
                return
            else:
                i = node.num_keys-1
                while i>=0 and node.keys[i] > key:
                    i-=1
                i+=1
                child = self.load_node(node.children[i])
                if child.num_keys == 19:
                    self.split_child(node, i)
                    if key > node.keys[i]:
                        i+=1
                    child = self.load_node(node.children[i])
                node = child

    def split_child(self, node, i):
        child = self.load_node(node.children[i])
        new_child = BTreeNode()
        new_child.block_id = self.index_file.next_block_id
        self.index_file.next_block_id+=1
        mid = 9
        new_child.num_keys = 9
        for j in range(9):
            new_child.keys[j] = child.keys[j+mid+1]
            new_child.values[j] = child.values[j+mid+1]
        for j in range(mid+1, child.num_keys+1):
            new_child.children[j-(mid+1)] = child.children[j]
        for j in range(new_child.num_keys+1,20):
            new_child.children[j] = 0
        for j in range(mid+1,19):
            child.keys[j]=0
            child.values[j]=0
        for j in range(mid+1,20):
            child.children[j]=0
        child.num_keys = mid
        new_child.parent_id = node.block_id
        for j in range(node.num_keys, i, -1):
            node.children[j+1] = node.children[j]
        node.children[i+1]=new_child.block_id
        for j in range(node.num_keys-1, i-1, -1):
            node.keys[j+1]=node.keys[j]
            node.values[j+1]=node.values[j]
        node.keys[i]=child.keys[mid]
        node.values[i]=child.values[mid]
        node.num_keys+=1
        child.keys[mid]=0
        child.values[mid]=0
        self.save_node(child)
        self.save_node(new_child)
        self.save_node(node)

def main():
    current_index = None
    current_btree = None
    while True:
        print("\n--- Menu ---")
        print("create   Create new index")
        print("open     Set current index")
        print("insert   Insert a new key/value pair into current index")
        print("search   Search for a key in current index")
        print("load     Insert key/value pairs from a file into current index")
        print("print    Print all key/value pairs in current index in key order")
        print("extract  Save all key/value pairs in current index into a file")
        print("quit     Exit the program")
        cmd = input("\nEnter command: ").strip().lower()
        if cmd == 'quit':
            if current_index:
                current_index.close()
                current_index = None
                current_btree = None
            break
        elif cmd == 'create':
            filename = input("Enter filename: ").strip()
            if IndexFile.file_exists(filename):
                ans = input(f"{filename} exists. Overwrite? (y/n): ").strip().lower()
                if ans not in ['y', 'yes']:
                    print("Aborted.")
                    continue
            idx = IndexFile()
            if not idx.create(filename):
                print("Failed to create index.")
            else:
                print(f"Index {filename} created.")
        elif cmd == 'open':
            if current_index:
                current_index.close()
                current_index = None
                current_btree = None
            filename = input("Enter filename: ").strip()
            idx = IndexFile()
            if not idx.open(filename):
                print(f"Failed to open {filename}.")
            else:
                current_index = idx
                current_btree = BTree(current_index)
                print(f"Index {filename} opened.")
        elif cmd == 'insert':
            if current_index is None or not current_index.is_open:
                print("No index currently open.")
                continue
            k = input("Enter key: ").strip()
            v = input("Enter value: ").strip()
            try:
                k=int(k)
                v=int(v)
            except:
                print("Invalid input.")
                continue
            if current_btree is not None:
                current_btree.insert(k,v)
                print("Inserted key/value.")
        elif cmd == 'search':
            if current_index is None or not current_index.is_open:
                print("No index currently open.")
                continue
            k = input("Enter key: ").strip()
            try:
                k=int(k)
            except:
                print("Invalid key.")
                continue
            if current_btree is not None:
                val = current_btree.search(k)
                if val is None:
                    print("Key not found.")
                else:
                    print(k,val)
        elif cmd == 'load':
            if current_index is None or not current_index.is_open:
                print("No index currently open.")
                continue
            print("not implemented yet.")
        elif cmd == 'print':
            if current_index is None or not current_index.is_open:
                print("No index currently open.")
                continue
            print("not implemented yet.")
        elif cmd == 'extract':
            if current_index is None or not current_index.is_open:
                print("No index currently open.")
                continue
            print("not implemented yet.")
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
