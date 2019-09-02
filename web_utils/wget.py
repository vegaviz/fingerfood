# -*- coding: utf-8 -*-
from sys import path as sys_path
from os import makedirs, path
from datetime import datetime
import uuid
import re
from requests.exceptions import RequestException as request_exception
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests import Session

SCHEME_SEP = '://'
HTTP_SCHEME = 'http'
HTTPS_SCHEME = 'https'
HTML_CONTENT = 'text/html'
RE_LINKS = re.compile(r'(href|src)="(\S+)"')

class Url:
    """Class for URL objects. Performs sanity checks on URL string and manages
    its components, including scheme, hierarchical domains and extensions.

    Attributes:
        url: Original URL string.
        scheme: HTTP or HTTPS.
        loc: Path of URL.
        domain: Domain of URL.
        ext: The extension of URL resource (if present).
        """

    def __init__(self, url):
        """Object initialization.

        Args:
            url: URL string.
        """

        self.url = url
        self.scheme = self._check_scheme(url)
        self.loc = url.split(SCHEME_SEP)[1]

        parts = self.loc.split('/')
        self.domain = parts[0]
        self.ext = self._get_ext(parts)

    def _check_scheme(self, url):
        """Checks the validity of URL scheme."""
        if url[:7] == HTTP_SCHEME + SCHEME_SEP:
            scheme = HTTP_SCHEME
            loc = url[7:]
        elif url[:8] == HTTPS_SCHEME + SCHEME_SEP:
            scheme = HTTPS_SCHEME
            loc = url[8:]
        else:
            raise ValueError('No scheme or scheme not supported')

        return scheme

    def _get_ext(self, parts):
        """Checks presence of a file extension in url."""
        if len(parts) > 1:
            resource = parts[-1]
            res_parts = resource.split('.')
            if len(res_parts) > 1:
                ext = res_parts[-1]
            else:
                ext = None
        else:
            ext = None

        return ext

    def matches_domains(self, other_domains):
        """Checks if url domain matches against a list of given domains."""
        res = False

        for domain in other_domains:
            if domain in self.domain:
                res = True
                break

        return res


class Wget:
    """A convenient implementation of wget GNU utility.

    Attributes:
        visited: Set of (unique) web-sites traversed by the object.
        data_index: An index of downloaded content. Each entry includes:
            saved filename, origin url, web domain and timestamp.
    """

    def __init__(self, conn_timeout=3, retries=3, backoff_factor=0.3,
        status_forcelist=(500, 502, 503, 504), recursive=False,
        recursion_level=3, accept_ext=[], reject_ext=[], include_domains=[],
        exclude_domains=[], datapath=None):
        """Object initialization.

        Args:
            conn_timeout: Connection timeout. Set to 3 seconds by default.
            retries: Num of connection retries. Set to 3 by default.
            backoff_factor: Backoff factor for connection retry.
            status_forcelist: HTTP responses for which retry is triggered.
            recursive: Follow page links (recursive download).
            recursion_level: Level of recursion (link depth).
            accept_ext: If specified, download only resources with extension in
                this list.
            reject_ext: If specified, do not download resources with extension
                in this list.
            include_domains: If specified, follow only domains in this list.
            exclude_domains: If specified, do not follow domains in this list.
            datapath: Path for saved data.
        """

        # data and index path
        self.datapath = datapath or sys_path[0]
        # connection
        self.conn_timeout = conn_timeout
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist
        # recursion
        self.recursive = recursive
        self.recursion_level = recursion_level
        self.include_domains = include_domains
        self.exclude_domains = exclude_domains
        # download
        self.accept_ext = accept_ext
        self.reject_ext = reject_ext
        # globally set visited urls and download metadata
        self.visited = set()
        self.data_index = []

    def get(self, url, **kwargs):
        """Starts crawling the given url. """

        # kept  at object-level
        visited = self.visited
        data_index = self.data_index

        # prepare folder for data
        if not path.isdir(self.datapath):
            makedirs(self.datapath)

        # override object settings
        for k, v in kwargs.items():
            setattr(self, k, v)

        # set recursion
        if self.recursive:
            recursion_level = self.recursion_level
        else:
            recursion_level = 1

        # get session and request data
        session = self._get_session()

        curr_links = [url]

        curr_level = 1
        while curr_level <= recursion_level:

            next_links = []
            for url in curr_links:

                # clean & check
                _url = Url(url)

                if _url.loc in visited:
                    continue
                else:
                    visited.add(_url.loc)

                try:
                    resp = session.get(url)

                except request_exception:
                    resp = None

                else:

                    if self._check_download(_url.ext):

                        uid = uuid.uuid4().hex
                        filename = self._save_data(resp, _url, uid)

                        if filename:
                            data_index.append(
                                {
                                    'filename': filename,
                                    'url': url,
                                    'domain': _url.domain,
                                    'timestamp': self._timestamp()
                                }
                            )

                    content_type = resp.headers.get('Content-Type')

                    if content_type and content_type.find(HTML_CONTENT) != -1:

                        # search for links
                        html = resp.text
                        links = self._extract_links(_url, html)

                        next_links += links

            curr_links = next_links
            curr_level += 1
            del next_links

    def _get_session(self):

        # init session
        session = Session()

        # define retry mechanism
        retry = Retry(total=self.retries, read=self.retries,
            connect=self.retries, backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist)

        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def _save_data(self, resp, _url, name):
        """Saves data to file """

        filepath = path.join(self.datapath, _url.domain)
        if not path.isdir(filepath):
            makedirs(filepath)

        if _url.ext:
            filename = path.join(filepath, name + '.' + _url.ext)
        else:
            filename = path.join(filepath, name)

        with open(filename, 'wb') as f:
            f.write(resp.content)

        return filename

    def _extract_links(self, _url, html):

        links = []

        # href links / src images
        matches = RE_LINKS.findall(html)

        for m in matches:

            lnk = m[1].split('?')[0]
            lnk = lnk.split('#')[0]

            if lnk:

                if lnk[0:2] == '//':
                    lnk = '{0}://{1}'.format(_url.scheme, lnk[2:])
                elif lnk[0] == '/':
                    lnk = '{0}://{1}{2}'.format(_url.scheme, _url.domain, lnk)

                try:

                    _lnk = Url(lnk)

                    check_include = (not self.include_domains) or \
                        _lnk.matches_domains(self.include_domains)

                    check_exclude = (not self.exclude_domains) or \
                        (not _lnk.matches_domains(self.exclude_domains))

                    if check_include and check_exclude:
                        print(f'Added {lnk}')
                        links.append(lnk)

                    else:
                        print(f'Rejected {lnk}')

                except ValueError:
                    # link not valid
                    pass

        return list(set(links))

    def _check_download(self, ext):
        """ Checks if resource has to be downloads. """

        # download settings
        accept_ext=self.accept_ext
        reject_ext=self.reject_ext

        download = True

        if ext:
            if accept_ext and ext not in accept_ext:
                download = False
            if reject_ext and ext in reject_ext:
                download = False
        elif accept_ext:
            download = False

        return download

    def _timestamp(self):
        """ Generates a timestamp of download. """

        datefmt = "%Y-%m-%d %H:%m:%S"

        return datetime.now().strftime(datefmt)
