#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import sql
from .hashing import HashedString

class Fingerprint:

    def __init__(self,text_string,text_name=None,**kwargs):

        # unique text identifier, if not specified it is extracted from text
        self.text_name = text_name or self.get_excerpt(text_string)

        # input text string
        self.text_string = text_string

        # winnowing parameters [chars]
        self.kgram_len = kwargs.get('kgram_len',15)                  # length of k-gram
        self.detection_thr = kwargs.get('detection_thr',40)         # detection threshold
        self.win_size = self.detection_thr - self.kgram_len + 1     # window size

        # generate fingerprints of input text
        self.fingerprints = self.generate(text_string)


    def get_excerpt(self,text_string):
        """ Extract an excerpt from text string
        """

        N = 30
        return text_string[:N]


    def remove_whitespaces(self,in_text):
        """ Remove all blanks from text string
        NOT USED
        """
        out_text = in_text.replace(" ", "")
        return out_text


    def generate(self,in_text):
        """ Generate fingerprints of input text
        """

        # preprocess text
        #clean_text = self.remove_whitespaces(in_text)

        # text length
        text_len = len(in_text)

        # text kgrams
        # ----------------------------------------------- #
        num_kgrams = text_len-self.kgram_len+1
        kgrams = []
        for ii in range(num_kgrams):
            kgrams.append( in_text[ii:ii+self.kgram_len] )

        # hash of k-grams
        # ----------------------------------------------- #
        hashes = []

        # first hash/position
        hh = HashedString.normal(kgrams[0])
        hashes.append(hh.get_hash_list())

        # next hashes
        for ii in range(1,num_kgrams):

            prev_hash = hashes[ii-1]

            # new rolling hash
            hh = HashedString.rolling(kgrams[ii],prev_hash)

            # new hash/position
            hashes.append( hh.get_hash_list() )

        # selection of fingerprints
        # ----------------------------------------------- #
        sel_hashes = []
        sel_positions = []

        # kgram window
        win = hashes[:self.win_size]
        last_hsh = min(win)
        last_pos = win.index(last_hsh)

        # add first hash and position
        sel_hashes.append( last_hsh )
        sel_positions.append( last_pos )

        # moving window
        for ii in range(1,text_len-self.win_size):

            win = hashes[ii:ii+self.win_size]

            # new candidate hash
            candidate = min(win)

            # absolute position in text
            pos = win.index(candidate)
            pos += ii

            if (candidate != last_hsh) or (candidate == last_hsh and pos>last_pos):

                # add new fingerprint
                sel_hashes.append( candidate )
                sel_positions.append( pos )

                # update hash/position
                last_hsh = candidate
                last_pos = pos

        fingerprints = (sel_hashes,sel_positions)

        return fingerprints



    def compare_with(self,other_obj):
        """ compare with another text or another fingerprint

        returns True if at least match is detected, False otherwise
        """

        # type check
        if type(other_obj) is Fingerprint:
            pass
        elif type(other_obj) is str:
            other_obj = Fingerprint(other_obj,kgram_len=self.kgram_len,detection_thr=self.detection_thr)
        else:
            raise TypeError('Only Fingerprint obj or str allowed!')

        # init
        self_hashes,self_positions = self.fingerprints
        other_hashes,other_positions = other_obj.fingerprints

        other_name = other_obj.text_name
        other_text = other_obj.text_string

        matches = self._search(other_name,other_hashes,other_positions,other_text)

        return matches



    def search_in_db(self,db_name):
        """ compare with fingerprints stored in sqlite database
        """

        # init
        all_matches = []

        # get stored exceprts
        other_names = sql.get_text_names(db_name)

        # get text and fingerprints
        # ----------------------------------------------- #
        for other_name in other_names:

            # get text from db
            other_text = sql.get_text(db_name,other_name)

            # get fingerprints from db
            other_fingerprints = sql.get_fingerprints(db_name,other_name)

            other_hashes,other_positions = other_fingerprints

            matches = self._search(other_name,other_hashes,other_positions,other_text)

            if matches:
                all_matches += matches
        return all_matches


    def to_sql(self,db_name,if_exists='append'):
        """ Write fingerprints to SQL database

        if database doesn't exist, it is created otherwise data are inserted
        """

        # action check
        if if_exists not in ('fail', 'replace', 'append'):
            raise ValueError("'{0}' is not valid for if_exists".format(if_exists))

        # packing arguments
        text_data = self.text_name,self.text_string

        res = sql.write_data(db_name,text_data,self.fingerprints,if_exists)

        return res


    def _search(self,other_name,other_hashes,other_positions,other_text):

        # init
        matches = []

        self_hashes,self_positions = self.fingerprints
        self_text = self.text_string
        self_len = len(self_text)

        other_len = len(other_text)

        last_found = 0
        for hsh,pos in zip(self_hashes,self_positions):

            # check for maximum match
            if hsh in other_hashes and pos>last_found:

                # self boundaries
                x1 = pos
                x2 = x1+self.kgram_len

                # other boundaries
                y1 = other_positions[other_hashes.index(hsh)]
                y2 = y1+self.kgram_len

                # left expanding
                while x1>0 and y1>0:
                    if (self_text[x1-1:x2] == other_text[y1-1:y2]):
                        x1-=1
                        y1-=1
                    else:
                        break

                # right expanding
                while x2<self_len and y2<other_len:
                    if (self_text[x1:x2+1] == other_text[y1:y2+1]):
                        x2+=1
                        y2+=1
                    else:
                        break

                # update last position of match
                last_found = x2

                if (x2-x1)>=self.detection_thr:

                    assert self_text[x1:x2] == other_text[y1:y2]

                    #other_idx = other_hashes.index(hsh)
                    m = dict()
                    m['pos'] = pos
                    m['substr'] = self_text[x1:x2]
                    m['found_in'] = other_name
                    matches.append(m)

        if not matches:
            matches = None

        return matches
