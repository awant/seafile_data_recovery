# Scripts to analyse and restore data and files from seafile structure

## Utils

* seafile_data_recovery.py
* seafile_data_profiler.py

## seafile_data_recovery.py

Restores files (and a folder tree) from 'seafile-data' folder. It recovers your data and saves files into recovered_data (by user and top-level folder).

Example of usage:

```sh
python seafile_data_recovery.py --src seafile-data --tgt recovered_data
```

## seafile_data_profiler.py

Shows the most important information from folders: fs/commits/blocks. Helps to explore a structure of your 'seafile-data' folder.

Example of usage (repo is a repo_id, which is a folder name in **commits/** folder):

```sh
python seafile_data_profiler.py --src seafile-data --repo 52ad7c5f-403b-4949-a12a-ed1a5a537d69
```

Example of output:

```sh
--- --- --- --- --- --- --- COMMITS --- --- --- --- --- --- ---
obj_id: 60f2d9c3bdf0d0ae1fb281ee5c18fc60603e5855
    commit_id: 60f2d9c3bdf0d0ae1fb281ee5c18fc60603e5855
    root_id: 0000000000000000000000000000000000000000
    repo_id: 52ad7c5f-403b-4949-a12a-ed1a5a537d69
    repo_name: My Library
    repo_desc: My Library
    description: Created library
    parent_id: None
    ctime: 1655553915
obj_id: 64aaa70c00e6c2228a9e748dc8acd516bd3e7978
    commit_id: 64aaa70c00e6c2228a9e748dc8acd516bd3e7978
    root_id: fafcea93a3343f3db91adc212f58c03fec2e437c
    repo_id: 52ad7c5f-403b-4949-a12a-ed1a5a537d69
    repo_name: My Library
    repo_desc: My Library
    description: Added "seafile-tutorial.doc"
    parent_id: 60f2d9c3bdf0d0ae1fb281ee5c18fc60603e5855
    ctime: 1655553915
--- --- --- --- --- --- --- FS --- --- --- --- --- --- ---
obj_id: b88ab96740ef53249b9d21fb3fa28050842266ba
    type: 1
    size: 300544
    block_ids:
    8663a70ef30a5987b440a621483af2044bae1e0a
obj_id: fafcea93a3343f3db91adc212f58c03fec2e437c
    type: 3
    dirents:
      seafile-tutorial.doc b88ab96740ef53249b9d21fb3fa28050842266ba
--- --- --- --- --- --- --- BLOCKS --- --- --- --- --- --- ---
block_id: 8663a70ef30a5987b440a621483af2044bae1e0a, size: 300544
```