import os
import argparse
import json
import zlib
import hashlib
import stat


EMPTY_SHA1 = '0'*40


def build_commits_folder_path(seafile_folder):
    return os.path.join(seafile_folder, 'storage', 'commits')


def build_fs_folder_path(seafile_folder):
    return os.path.join(seafile_folder, 'storage', 'fs')


def build_blocks_folder_path(seafile_folder):
    return os.path.join(seafile_folder, 'storage', 'blocks')


def iget_repo_ids(seafile_folder):
    commits_folder = build_commits_folder_path(seafile_folder)
    for repo_id in os.listdir(commits_folder):
        yield repo_id


def iget_commit(seafile_folder, repo_id):
    repo_folder = os.path.join(build_commits_folder_path(seafile_folder), repo_id)
    for prefix in os.listdir(repo_folder):
        for postfix in os.listdir(os.path.join(repo_folder, prefix)):
            with open(os.path.join(repo_folder, prefix, postfix), 'r') as file:
                commit = json.load(file)
                object_id = prefix + postfix
                yield (object_id, commit)


def get_fs_filepath(seafile_folder, repo_id, object_id):
    fs_folder = build_fs_folder_path(seafile_folder)
    return os.path.join(fs_folder, repo_id, object_id[:2], object_id[2:])


def get_blocks_filepath(seafile_folder, repo_id, object_id):
    blocks_folder = build_blocks_folder_path(seafile_folder)
    return os.path.join(blocks_folder, repo_id, object_id[:2], object_id[2:])


def get_fs_file_content(filepath):
    if not os.path.exists(filepath):
        return None
    data = open(filepath, 'rb').read()
    decompressed_data = zlib.decompress(data)
    return decompressed_data


def get_fs_file_content_json(filepath):
    fs_file_content = get_fs_file_content(filepath)
    if fs_file_content is None:
        raise RuntimeError(f'The {filepath=} content is None')
    return json.loads(fs_file_content)


def is_file_content_valid(content, object_id):
    if content is None:
        return False
    hex_value = hashlib.sha1(content).hexdigest()
    if hex_value != object_id:
        return False
    return True


def find_last_available_commit(seafile_folder, repo_id):
    commits = sorted(iget_commit(seafile_folder, repo_id), key=lambda commit: -commit[1]['ctime'])
    for object_id, commit in commits:
        if commit['root_id'] == EMPTY_SHA1:
            continue
        filepath = get_fs_filepath(seafile_folder, repo_id, commit['root_id'])
        file_content = get_fs_file_content(filepath)
        if is_file_content_valid(file_content, commit['root_id']):
            return commit
    return None


def create_file(seafile_folder, repo_id, obj_id, mtime, path):
    filepath = get_fs_filepath(seafile_folder, repo_id, obj_id)
    content = get_fs_file_content_json(filepath)
    file_size, block_ids = content['size'], content['block_ids']

    with open(path, 'wb') as out_f:
        for block_id in block_ids:
            current_block_path = get_blocks_filepath(seafile_folder, repo_id, block_id)
            with open(current_block_path, 'rb') as inp_f:
                out_f.write(inp_f.read())

    os.chmod(path, 0o666)
    os.utime(path, (mtime, mtime))


def extract_data_recursive(seafile_folder, repo_id, obj_id, tgt_directory):
    filepath = get_fs_filepath(seafile_folder, repo_id, obj_id)

    file_content = get_fs_file_content_json(filepath)

    for dirent in file_content['dirents']:
        dirent_id = dirent['id']
        if dirent_id == EMPTY_SHA1:
            continue
        cur_path = os.path.join(tgt_directory, dirent['name'])
        if stat.S_ISREG(dirent['mode']):
            create_file(seafile_folder, repo_id, dirent_id, dirent['mtime'], cur_path)
        elif stat.S_ISDIR(dirent['mode']):
            os.mkdir(cur_path, 0o777)
            extract_data_recursive(seafile_folder, repo_id, dirent_id, cur_path)


def recover_data(seafile_folder, target_folder, repo_id):
    print('Recover data for repo_id: ' + repo_id)
    commit = find_last_available_commit(seafile_folder, repo_id)
    if commit is None:
        print("Couldn't find relevant commit, skipping this repo. It can be due to an empty top-level directory")
        return
    print('Commit was found. creator_name: {}, repo_name: {}'.format(commit['creator_name'], commit['repo_name']))

    tgt_directory = os.path.join(target_folder, commit['creator_name'], commit['repo_name'])
    os.makedirs(tgt_directory)

    extract_data_recursive(seafile_folder, repo_id, commit['root_id'], tgt_directory)


def main():
    parser = argparse.ArgumentParser(description='Recover seafile data')
    parser.add_argument('--src', type=str, required=True, help='source folder \'seafile-data\' by default')
    parser.add_argument('--tgt', type=str, required=True, help='target folder where to save results')

    args = parser.parse_args()

    for repo_id in iget_repo_ids(args.src):
        recover_data(args.src, args.tgt, repo_id)


main()
