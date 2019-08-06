# -*- coding: utf-8 -*-
from collections import namedtuple

Sample = namedtuple('Sample', ['pts', 'pos'])

class Fingerprint:
    """ Class for document fingerprinting.

    This class provides methods to extract fingerprints from text, thus allowing
    duplicate detection. Fingerprinting is based on local algorithm winnowing
    (http://theory.stanford.edu/~aiken/publications/papers/sigmod03.pdf).
    """

    def __init__(self, noise_thr=60, detection_thr=80, **kwargs):
        """Object initialization.

        Args:
            noise_thr: Threshold for noise detection (characters). No match with
                length less than noise_thr will be detected.
            detection_thr: Guarantee threshold (characters). Any match at least
                as long as guarantee threshold will be detected.
        """

        self.kgram_size = noise_thr
        self.detection_thr = detection_thr
        self.win_size = detection_thr - noise_thr + 1
        # base for hash evaluation
        self.B = 2

    def __call__(self, text):
        """ Generates fingerprints for input text.

        Args:
            text: Text string to fingerprint.

        Returns:
            A namedtuple Sample, which contains:
                - Sample.pts, fingerprint points (int);
                - Sample.pos, fingerprint position in text.
        """

        kgram_size = self.kgram_size
        win_size = self.win_size

        # generate k-grams
        # ----------------------------------------------- #

        # text length
        text_len = len(text)

        num_kgrams = text_len-kgram_size+1

        kgrams = []
        for ii in range(num_kgrams):
            kgrams.append(text[ii:ii+kgram_size])

        # hash the k-grams
        hashes = [self._hash(kgram) for kgram in kgrams]

        # selection of fingerprints
        # ----------------------------------------------- #
        sel_hashes = []
        sel_positions = []

        # kgram window
        win = hashes[:win_size]
        hash_last = min(win)
        pos_last = win.index(hash_last)

        # add first hash and position
        sel_hashes.append(hash_last)
        sel_positions.append(pos_last)

        # moving window
        for ii in range(1, num_kgrams - win_size + 1):

            win = hashes[ii:ii+win_size]

            # new candidate hash
            candidate = min(win)

            # position in in hashes
            pos = win.index(candidate) + ii

            if (candidate != hash_last) or (candidate == hash_last and pos > pos_last):

                # add new fingerprint
                sel_hashes.append(candidate)
                sel_positions.append(pos)

                # update hash/position
                hash_last = candidate
                pos_last = pos

        return Sample(pts=sel_hashes, pos=sel_positions)

    def _hash(self, kgram):
        """ Evaluates polynomial hash value. """

        assert len(kgram) == self.kgram_size
        #raise ValueError(f'String must have length {self.str_size}')

        hh = sum([ord(kgram[ii]) * (self.B**(self.kgram_size - ii)) for ii in range(self.kgram_size)])

        return hh
