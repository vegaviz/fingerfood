#!/usr/bin/python3
# -*- coding: utf-8 -*-

class HashNotFound(AttributeError):
    '''String has not been hashed'''


class HashedString():

    def __init__(self,word):

        # original word
        self.word = word
        self.hashed = None


    def __eq__(self,other):
        return self.hashed == other.hashed


    def __lt__(self,other):

        for ii in range(len(self.hashed)):

            x = self.hashed[ii]
            y = other.hashed[ii]

            if (x<y):
                return True
            elif (x>y):
                return False

        return False


    def __gt__(self,other):

        for ii in range(len(self.hashed)):

            x = self.hashed[ii]
            y = other.hashed[ii]

            if (x>y):
                return True
            elif (x<y):
                return False

        return False


    def __le__(self,other):
        pass

    def ge(self,other):
        pass

    def ne(self,other):
        return self.hashed != other.hashed


    def char2hex(self,c,num_hex):
        return "{0:0{1}x}".format(ord(c),num_hex)


    @classmethod
    def normal(self,word):

        # init new Hash obj
        hh = HashedString(word)

        word_len = len(word)

        hashed = [0]*word_len
        for ii in range(word_len):

            idx = word_len-ii-1

            # fixed-length hexadecimal representation for unicode characters
            hashed[idx] = hh.char2hex(word[ii],2)

        hh.hashed = hashed

        return hh


    @classmethod
    def rolling(self,new_word,old_hash):

        # init new Hash obj
        hh = HashedString(new_word)

        hashed = [hh.char2hex(new_word[-1],2)] + old_hash[:-1]
        hh.hashed = hashed

        return hh


    def get_hash_list(self):

        if self.hashed:
            return self.hashed
        else:
            raise HashNotFound('no hash found for this k-gram')


    def get_hash_string(self):

        if self.hashed:
            return '.'.join(self.hashed)
        else:
            raise HashNotFound('no hash found for this k-gram')
