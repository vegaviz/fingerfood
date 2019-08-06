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

# list of encoding codes - TBC
DEFAULT_DECODING = {
    '&#8217;': '\'',
    '&nbsp;': ' ',
    '&quot;': '"',
    '&#8220;': '"',
    '&#8221;': '"',
    '&apos;': '\'',
    '&#39;': '\'',
    '&#8211;': '-',
    '&agrave;': 'à',
    '&egrave;': 'è',
    '&eacute;': 'é',
    '&igrave;': 'ì',
    '&ograve;': 'ò',
    '&ugrave;': 'ù',
    '7&deg;': '°',
    '&amp;': '&',
    '&rsquo;': '\'',
    '&rdquo;': '"',
    '&ldquo;': '"',
    '&raquo;': '>',
    '&laquo;': '<',
    '&ndash;': '-'
}

class Html2Text:
    """ Class for extracting text from raw html.

    Includes a few simple methods for TAG cleansing and string url-decoding.
    """

    def __init__(self, len_thr=50, decoding=DEFAULT_DECODING):
        """Object initialization.

        Args:
            len_thr: Length threshold (characters). Only text fragments longer
                than threshold will be extracted.
            decoding: A dict for url-decoding. Keys and values contain the
                encoded and decoded strings respectively.
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

            text = self._decode(m.group(1))
            text = self._clean_text(text)

            if len(text) > self.len_thr:
                parts.append(text)

        return parts

    def _clean_text(self, text):

        # remove tags
        text = self._extract_from_tag(RE_A, text)
        text = self._extract_from_tag(RE_SPAN, text)

        # remove spurious
        text = RE_GEN.sub('', text).strip()

        return text

    def _declutter(self, html):
        """ De-clutters raw html. """

        # useless parts
        html = RE_HEAD.sub('', html)
        html = RE_SCRIPTS.sub('', html)
        html = RE_NOSCRIPT.sub('', html)
        html = RE_STYLES.sub('', html)
        html = RE_COMMENT.sub('', html)
        html = RE_SPACES.sub(' ', html)
        html = RE_IMG.sub(' ', html)

        # remove style tags
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
