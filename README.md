# project3.py
Python source code for b-tree program

# devlog.md
A development log detailing the sessions, thoughts, plans, and actions taken

# How to run the project:
1. Ensure you have Python 3 installed on your system.
2. Open a terminal (or SSH into the cs1 or cs2 machines).
3. Run the program in the same directory as project3.py:
       
       bash
       ```
       python3 project3.py
       ```
       
       This will start the interactive menu.

4. Follow the on-screen instructions to:
       - create an index file
       - open an existing index file (must include the file extension in your input)
       - insert keys/values (keys and values are unsigned integers)
       - search for specific keys
       - load keys/values from a CSV file (each line: `key,value`)
       - print all entries
       - extract all entries to a file
       - quit when done

# Additional Notes:
- The index file uses 512-byte blocks with a header and B-tree nodes stored on disk.
- Keys and values are stored as 64-bit big-endian integers.
- Make sure the file names you provide exist (for open or load commands) and that you have proper permissions.
- The load command will skip keys that already exist.
- Tested with .idx files.