#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3


def write_data(db_name,text_data,fingerprints,if_exists):
    """Store text data in DB:

        (1) text name and content
        (2) text fingerprints
    """

    out = True

    # unpack data to write
    text_name,text_string = text_data
    hashes,positions = fingerprints

    # connect to / create databse
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    # if not exists, create tables
    t1 = has_table(cur,'full_texts')
    t2 = has_table(cur,'fingerprints')

    # manage DB tables 'fail', 'replace', 'append'
    insert_data = True

    if not t1 and not t2:

        # init tables
        _init_tables(cur)

    # something strange happened here
    elif t1 ^ t2:
        raise sqlite3.OperationalError('Table inconsistency')

    else:

        if if_exists=='replace':
            # drop tables and re-init them
            _drop_tables(cur)
            _init_tables(cur)

        elif if_exists=='fail':
            # do nothing
            insert_data = False

    if insert_data:

        # insert text_name/full-text
        stmt = "insert into full_texts values (?,?)"

        try:
            cur.execute(stmt,[text_name,text_string])

        except sqlite3.IntegrityError as si:
            out = False
            print('error while updating data : {0}'.format(str(si)))

        # insert fingerprints
        stmt = "insert into fingerprints values (?,?,?)"
        for fp,pos in zip(hashes,positions):

            try:
                cur.execute(stmt,[text_name,str(fp),pos])

            except sqlite3.IntegrityError as si:
                out = False
                print('error while updating data : {0}'.format(str(si)))

    # commit & close connection
    con.commit()
    con.close()

    return out

def read_table(db_name,table_name):
    """Read table from DB
        NOT USED
    """

    # connect to / create databse
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    # table checks
    if not has_table(cur,'full_texts'):
        raise sqlite3.OperationalError('Table full_texts not found')
    if not has_table(cur,'fingerprints'):
        raise sqlite3.OperationalError('Table fingerprints not found')

    stmt = 'select * from {0}'.format(table_name)
    table_rows = []
    for row in cur.execute(stmt):
        table_rows.append(row)

    con.close()

    return table_rows


def _init_tables(cur):
    """Init tables in DB

    Create tables:
        (1) full_text
        (2) fingerprints
    """

    # create table with full texts
    stmt = 'create table full_texts(text_name text, text_string text, primary key (text_name))'
    cur.execute(stmt)

    # create table with fingerprints and positions
    stmt = 'create table fingerprints(text_name text, hash text, position integer, primary key (text_name,hash,position))'
    cur.execute(stmt)


def _drop_tables(cur):
    """Drop tables of DB (for 'replace' mode)
    """

    stmt = 'drop table if exists full_texts'
    cur.execute(stmt)
    stmt = 'drop table if exists fingerprints'
    cur.execute(stmt)


def has_table(cur,name):
    """Check if table esists in DB
    """

    # check if table exists
    query = ("select name from sqlite_master where type='table' and name=?")

    return len(cur.execute(query, [name,]).fetchall()) > 0


def get_text_names(db_name):
    """Read names of texts stored in DB
    """

    # connect to / create databse
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    stmt = 'select text_name from full_texts'

    exceprts = []
    for row in cur.execute(stmt):
        exceprts.append(row[0])

    # disconnect
    con.close()

    return exceprts


def get_text(db_name,text_name):
    """Read from DB a full-text given its name
    """

    # connect to / create databse
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    # text query
    stmt = 'select text_string from full_texts where text_name=?'
    cur.execute(stmt,(text_name,))
    text = cur.fetchone()[0]

    # disconnect
    con.close()

    return text


def get_fingerprints(db_name,text_name):
    """Read from DB the fingerprints of a given text
    """

    # connect to / create databse
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    # text query
    stmt = 'select hash,position from fingerprints where text_name=?'
    cur.execute(stmt,(text_name,))
    rows = cur.fetchall()

    hashes = []
    positions = []
    for row in rows:
        hashes.append(eval(row[0]))
        positions.append(row[1])

    fingerprints = hashes,positions

    # disconnect
    con.close()

    return fingerprints
