## 12/7/2024 10:02PM
**Thoughts so far:**
- forgot to make updates to the devlog and do commits but basically just have the menu and some basic file io so no biggy i think

**Plan:**
- add devlog.md
- implement file handling with create and open functionality
- print menu

**Session Work:**
- made a csv file to test the load function later
- created devlog.md
- created project3.py
- implemented menu loop
- create and open functionalities

## 12/7/2024 11:10PM
**Thoughts so far:**
- need b-tree structure

**Plan:**
- add btreenode class
- implement methods to read/write node from 512 block

**Session Work:**
- added btreenode class
- implemented to_bytes and from_bytes methods

## 12/7/2024 11:42PM
**Thoughts so far:**
- need to integrate node into a b-tree

**Plan:**
- add btree class
- basic insert and search functionalities

**Session Work:**
- created btree class
- insert and search have some basic functionalities

## 12/8/2024 1:15AM
**Thoughts so far:**
- btree working, but doesn't split

**Plan:**
- add splitchild and insertnonfull methods
- have insert handle full root
- update search to descend nodes

**Session Work:**
- implemented splitchild, insertnonfull
- updated insert
- search traverses down tree