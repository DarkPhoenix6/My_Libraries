#!/usr/bin/env python
import re
import sys
import fileinput

# passed in parameters
file = sys.argv[1]
drupal_db = sys.argv[2]  # "drupal7e_drupalville"
username = sys.argv[3]
passwd = sys.argv[4]
find_str = '$databases = array();'
to_write = "$databases['default']['default'] = array(\n" \
           + "  'driver' => 'mysql',\n" \
           + "  'database' => '" + drupal_db + "',\n" \
           + "  'username' => '" + username + "',\n" \
           + "  'password' => '" + passwd + "',\n" \
           + "  'host' => 'localhost',\n" \
           + "  'charset' => 'utf8mb4',\n" \
           + "  'collation' => 'utf8mb4_general_ci',\n" \
           + ");\n"


def to_file():
    with fileinput.FileInput(files=file, inplace=True, backup='.bak') as file2:
        for line in file2:
            print(line.replace(find_str, to_write), end='')


def main():
    to_file()


if __name__ == '__main__':
    main()
