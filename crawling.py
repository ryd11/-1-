import os
from github_crawling import *
from stackoverflow_crawling import *

'''
※필독!※
language와 sort_tag를 정보에 맞게 넣어주세요 language = 개발언어, sort_tag = 'stars' or 'forks'
로그인 상태를 확인해주세요 아이디와 비밀번호를 자신의 비밀번호와 아이디로 넣어주세요
'''

language = "개발언어"
sort_tag = "stars or forks"
your_id = "아이디"
your_password = "비밀번호"

git_crawling(language, sort_tag, your_id, your_password)
stackoverflow_crawling(language)