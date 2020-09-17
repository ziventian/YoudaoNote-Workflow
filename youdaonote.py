#!/usr/bin/python
# encoding: utf-8

import sys
import plistlib
import os.path
import sqlite3

from workflow import Workflow3 as Workflow

user_dir = os.path.expanduser('~')
youdao_part_dir = 'Library/Containers/com.youdao.note.YoudaoNoteMac/Data/Library/Application Support/com.youdao.note.YoudaoNoteMac'
youdao_dir = os.path.join(user_dir, youdao_part_dir)
session_file = 'sess.dat'
db_file = 'YoudaoNote.db'
content_dir = 'Contents'

key_file_title = 'ZTITLE'  # 设备名称的key
key_file_id = 'ZFILEID'  # 设备ID(真实文件名称)的key
sql = '''
SELECT
  *
FROM
  ZFILEMETA
WHERE
  ZTITLE LIKE ?
AND ZDIR = 0
LIMIT 10
'''
def get_current_user():
    pl = plistlib.readPlist(os.path.join(youdao_dir, session_file))
    # print(pl.user)
    return pl.user
def get_current_youdao_dir():
    return os.path.join(youdao_dir, get_current_user())

def get_user_content_dir():
    return os.path.join(get_current_youdao_dir(), content_dir)
def get_user_db():
    return os.path.join(get_current_youdao_dir(), db_file)

def get_orig_file_by_id(file_id):
    id_file_path = lambda f: os.path.join(get_user_content_dir(), f, file_id)
    id_dir_path = lambda d: os.path.join(get_user_content_dir(), d)
    file_id_dir = file_id[-1]
    orig_file = id_file_path(file_id_dir)
    if os.path.exists(id_dir_path(file_id_dir.lower())):
        orig_file = id_file_path(file_id_dir.lower())
    elif os.path.exists(id_dir_path(file_id_dir.upper())):
        orig_file = id_file_path(file_id_dir.upper())
    return orig_file

def search_title(query):
    conn = sqlite3.connect(get_user_db())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql, (query, ))
    all_list = cursor.fetchall()
    # print(all_list)
    cursor.close()
    conn.close()
    return all_list
def main(wf):
    # print(get_user_db())
    query = wf.args[0]
    notes = search_title(u'%{}%'.format(query))
    for note in notes:
        orig_file = get_orig_file_by_id(note[key_file_id])
        wf.add_item(title=note[key_file_title], arg=orig_file, valid=True)
    wf.send_feedback()

if __name__ == "__main__":
    wf = Workflow()
    sys.exit(wf.run(main))