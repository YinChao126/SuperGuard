import os
from distutils.dir_util import copy_tree

if __name__ == '__main__':
    BASE = os.path.split(os.path.realpath(__file__))[0]
    #1.安装依赖
    cmd = 'pip install -r requirements.txt'
    os.system(cmd)
    
    #2.拷贝Config文件夹
    src_dir = BASE + '/doc/ConfigExample'
    dst_dir = BASE + '/superguard/Config'
    copy_tree(src_dir, dst_dir)
    
    #3.新建output文件夹
    directory = BASE + '/superguard/output'
    if not os.path.exists(directory):
        os.makedirs(directory)
