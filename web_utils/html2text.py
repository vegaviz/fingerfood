# -*- coding: utf-8 -*-
import re

RE_HEAD = re.compile(r'<head.*?<\/head>', re.MULTILINE|re.DOTALL)
RE_SCRIPTS = re.compile(r'<script.*?<\/script>', re.MULTILINE|re.DOTALL)
RE_NOSCRIPT = re.compile(r'<noscript>.+?<\/noscript>', re.MULTILINE|re.DOTALL)
RE_STYLES = re.compile(r'<style.*?<\/style>', re.MULTILINE|re.DOTALL)
RE_COMMENT = re.compile(r'<!--.*?-->', re.MULTILINE|re.DOTALL)
RE_P = re.compile(r'<p(?: .+?)?>(.+?)<\/p>', re.MULTILINE|re.DOTALL)
#RE_H1 = re.compile(r'<h1.*?>(.+?)<\/h1>', re.MULTILINE|re.DOTALL)
#RE_H2 = re.compile(r'<h2.*?>(.+?)<\/h2>', re.MULTILINE|re.DOTALL)
#RE_H3 = re.compile(r'<h3.*?>(.+?)<\/h3>', re.MULTILINE|re.DOTALL)
RE_A = re.compile(r'<a .*?>(.+?)<\/a>', re.MULTILINE|re.DOTALL)
RE_SPACES = re.compile(r'\s+', re.MULTILINE|re.DOTALL)
RE_SPAN = re.compile(r'<span.*?>(.+?)<\/span>', re.MULTILINE|re.DOTALL)
RE_IMG = re.compile(r'<img .+?>', re.MULTILINE|re.DOTALL)
RE_GEN = re.compile(r'<.+?>', re.MULTILINE|re.DOTALL)

class Html2Text:
    """ Class for extracting text from raw html.

    Includes a few simple methods for TAG cleansing and string url-decoding.
    """

    def __init__(self, len_thr=50, decoding=None):
        """Object initialization.

        Args:
            len_thr: Length threshold (characters). Only text fragments longer
                than threshold will be extracted.
            decoding: Data for url-decoding (optional). If specified, must be
                a dict where keys and values are respectively encoded and
                decoded strings.
        """
        self.len_thr = len_thr
        self.decoding = decoding


    def __call__(self, html):
        """ Extracts text fragments from raw html and stores them internally.

        Args:
            html: Html code to parse.

        Returns:
            A list of text fragments as extracted from html code.
        """

        html = self._declutter(html)

        # p-tag extraction
        parts = []
        for m in RE_P.finditer(html):

            if self.decoding:
                text = self._decode(m.group(1))
            text = self._clean_text(text)

            if len(text) > self.len_thr:
                parts.append(text)

        return parts

    def _clean_text(self, text):
        """ Removes A, SPAN and spurious tags. """
        text = self._extract_from_tag(RE_A, text)
        text = self._extract_from_tag(RE_SPAN, text)
        text = RE_GEN.sub('', text).strip()

        return text

    def _declutter(self, html):
        """ Removes extra-text sections and style tags. """
        html = RE_HEAD.sub('', html)
        html = RE_SCRIPTS.sub('', html)
        html = RE_NOSCRIPT.sub('', html)
        html = RE_STYLES.sub('', html)
        html = RE_COMMENT.sub('', html)
        html = RE_SPACES.sub(' ', html)
        html = RE_IMG.sub(' ', html)
        html = html.replace('<em>', '').replace('</em>', '')
        html = html.replace('<strong>', '').replace('</strong>', '')

        return html

    def _decode(self, text):
        """ Simple url-decoding based on replacement. """

        for k, v in self.decoding.items():
            text = text.replace(k, v)

        return text

    def _extract_from_tag(self, regex, html):

        m = regex.search(html)
        while m:
            html = html[:m.start()] + m.group(1) + html[m.end():]
            m = RE_A.search(html)

        return html
