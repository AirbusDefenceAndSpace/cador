from behave.__main__ import main as behave_main

'''
Documentation : 
    http://behave.readthedocs.io/en/latest/tutorial.html

Command lines :
    -w        : turns off stdout capture
    -t,--tags : select stories to run based on tags (add '-' before tag to ignore it) ex: --tags=tag1,-ignored_tag
    -v        : verbose

'''

ROOT_PATH = '.'

ARGS = ['-t=-tag_service']

behave_main([ROOT_PATH, *ARGS])
