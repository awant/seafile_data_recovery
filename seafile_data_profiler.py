import os
import argparse
import json
import zlib
import hashlib
import stat


def read_commit(path):
    with open(path, 'r') as file:
        return json.load(file)


def read_fs(path):
    data = open(path, 'rb').read()
    decompressed_data = zlib.decompress(data)
    return json.loads(decompressed_data)


def show_header(header_name):
    print('--- --- --- --- --- --- --- {} --- --- --- --- --- --- ---'.format(header_name))


def show_commits(seafile_folder, repo_id):
    show_header('COMMITS')
    commits_folder = os.path.join(seafile_folder, 'storage', 'commits', repo_id)
    for prefix in os.listdir(commits_folder):
        for postfix in os.listdir(os.path.join(commits_folder, prefix)):
            obj_id = prefix + postfix
            obj_filepath = os.path.join(commits_folder, prefix, postfix)
            commit = read_commit(obj_filepath)


            print('obj_id: ' + obj_id)

            cols_to_show = [
                'commit_id', 'root_id', 'repo_id', 'repo_name', 'repo_desc', 'description',
                'parent_id', 'ctime'
            ]
            print('\n'.join(map(lambda col: '    {}: {}'.format(col, commit[col]), cols_to_show)))


def show_fs(seafile_folder, repo_id):
    show_header('FS')
    fs_folder = os.path.join(seafile_folder, 'storage', 'fs', repo_id)
    for prefix in os.listdir(fs_folder):
        for postfix in os.listdir(os.path.join(fs_folder, prefix)):
            obj_id = prefix + postfix
            obj_filepath = os.path.join(fs_folder, prefix, postfix)
            fs = read_fs(obj_filepath)

            print('obj_id: ' + obj_id)
            print('    type: {}'.format(fs['type']))

            if fs['type'] == 1:
                print('    size: ' + str(fs['size']))
                print('    block_ids:\n' + '\n'.join(map('    {}'.format, fs['block_ids'])))
            else:
                print('    dirents:\n' + '\n'.join(map(lambda d: '      {} {}'.format(d['name'], d['id']), fs['dirents'])))


def show_blocks(seafile_folder, repo_id):
    show_header('BLOCKS')
    block_folder = os.path.join(seafile_folder, 'storage', 'blocks', repo_id)
    for prefix in os.listdir(block_folder):
        for postfix in os.listdir(os.path.join(block_folder, prefix)):
            obj_id = prefix + postfix
            obj_filepath = os.path.join(block_folder, prefix, postfix)
            size = os.stat(obj_filepath).st_size 
            print('block_id: {}, size: {}'.format(obj_id, size))


def show_repos(seafile_folder):
    show_header('REPOS')
    fs_folder = os.path.join(seafile_folder, 'storage', 'fs')
    for repo_id in os.listdir(fs_folder):
        print(repo_id)


def profile_data(seafile_folder, repo_id):
    show_commits(seafile_folder, repo_id)
    show_fs(seafile_folder, repo_id)
    show_blocks(seafile_folder, repo_id)


def main():
    parser = argparse.ArgumentParser(description='Profile seafile data')
    parser.add_argument('--src', type=str, required=True, help='source seafile folder')
    parser.add_argument('--repo', type=str, required=True, help='repo_id')

    args = parser.parse_args()

    profile_data(args.src, args.repo)


main()


