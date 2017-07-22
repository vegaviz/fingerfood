#!/usr/bin/python3
# -*- coding: utf-8 -*-

import fingerfood as fd
from os import remove, path

# testing texts
text_01 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis finibus metus quam, eget pulvinar ligula viverra vitae. Duis egestas vitae diam ac sodales. Mauris mattis lacinia sodales. Aliquam vitae finibus tortor. Aliquam erat volutpat. Duis et ex aliquam, ultrices ipsum non, malesuada tortor. Pellentesque bibendum elit dolor, quis malesuada turpis viverra sit amet. Ut pretium aliquam vehicula. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Aenean vel convallis arcu. Sed non feugiat mi. Fusce vulputate dui vel metus tincidunt blandit. Sed finibus faucibus mi, quis dictum nulla tempus non. Ut ultricies sagittis laoreet."

text_02 = "Aenean consectetur turpis et gravida pharetra. Mauris vitae faucibus orci. Curabitur lobortis arcu id iaculis scelerisque. Morbi magna nunc, blandit quis congue eu, ullamcorper ac odio. Nullam luctus semper tristique. Integer vel rhoncus odio, nec fermentum libero. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur in nibh ante. In gravida vitae augue sed rhoncus. Curabitur lobortis aliquam faucibus. Vestibulum pharetra orci finibus viverra lacinia. Suspendisse quis varius enim."


def test_hashing():

    # normal hash
    hh0 = fd.HashedString.normal('Lorem ipsum dolor sit amet')
    assert hh0.get_hash_string() == '74.65.6d.61.20.74.69.73.20.72.6f.6c.6f.64.20.6d.75.73.70.69.20.6d.65.72.6f.4c'

    # rolling vs normal hash
    hh1 = fd.HashedString.rolling('orem ipsum dolor sit amet,',hh0.get_hash_list())
    hh2 = fd.HashedString.normal('orem ipsum dolor sit amet,')

    assert hh1.get_hash_string() == hh2.get_hash_string()


def test_comparing():

    fp1 = fd.Fingerprint(text_01,'text_01',kgram_len=12,detection_thr=30)
    fp2 = fd.Fingerprint(text_02,'text_02',kgram_len=12,detection_thr=30)

    # compare Fingerprint objects
    m = fp1.compare_with(fp2)
    assert m
    assert m[0].get('pos') == 16
    assert m[0].get('substr') == 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '

    # compare Fingerprint obj with string
    m = fp1.compare_with(text_02)
    assert m
    assert m[0].get('pos') == 16
    assert m[0].get('substr') == 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '


def test_db_io():

    fp = fd.Fingerprint(text_01,'text_01')

    # remove existing database
    if path.isfile('test.db'):
        remove('test.db')

    # store data to db
    res = fp.to_sql('test.db')
    assert res

    # load data from db
    stored_text= fd.sql.get_text('test.db','text_01')
    stored_fps = fd.sql.get_fingerprints('test.db','text_01')

    # store same data to db
    res = fp.to_sql('test.db',if_exists='replace')
    assert res

    # remove db
    remove('test.db')

    # check content
    assert stored_text == text_01
    assert len(stored_fps[0]) == len(fp.fingerprints[0])

    for el in fp.fingerprints[0]:
        assert el in stored_fps[0]
    for el in fp.fingerprints[1]:
        assert el in stored_fps[1]


def test_db_match():

    fp1 = fd.Fingerprint(text_01,'text_01')
    fp2 = fd.Fingerprint(text_02,'text_02')

    # remove existing database
    if path.isfile('test.db'):
        remove('test.db')

    # store data to db
    fp1.to_sql('test.db','replace')

    m = fp2.search_in_db('test.db')

    # remove db
    remove('test.db')

    assert m
    assert m[0].get('pos') == 279
    assert m[0].get('substr') == 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '


if __name__ == '__main__':

    print('starting tests...')

    # testing fingerprints
    test_hashing()

    # testing text compare
    test_comparing()

    # testing sql storing
    test_db_io()

    # testing db search
    test_db_match()

    print('success!')
