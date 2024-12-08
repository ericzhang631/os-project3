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

def main():
    current_index = None
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
            filename = input("Enter filename (including extension): ").strip()
            idx = IndexFile()
            if not idx.open(filename):
                print(f"Failed to open {filename}.")
            else:
                current_index = idx
                print(f"Index {filename} opened.")
        elif cmd == 'insert':
            if current_index is None or not current_index.is_open:
                print("No index currently open.")
                continue
            print("not implemented yet.")
        elif cmd == 'search':
            if current_index is None or not current_index.is_open:
                print("No index currently open.")
                continue
            print("Search not implemented yet.")
        elif cmd == 'load':
            if current_index is None or not current_index.is_open:
                print("No index currently open.")
                continue
            print("not implemented yet.")
        elif cmd == 'print':
            if current_index is None or not current_index.is_open:
                print("No index currently open.")
                continue
            print("implemented yet.")
        elif cmd == 'extract':
            if current_index is None or not current_index.is_open:
                print("No index currently open.")
                continue
            print("not implemented yet.")
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
