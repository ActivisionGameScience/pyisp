import radix
import urllib.request
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context
import os
import time
import re
from tempfile import gettempdir

from ipaddress import ip_address

__all__ = ['Reader', ]


class ISPResponse():
    """Struct to hold a response from the database
    """

    autonomous_system_number = None
    autonomous_system_organization = None


class Reader():
    """ISP database reader (with auto-fetch and auto-update capabilities)
    """

    asn_isp_url = "http://thyme.apnic.net/current/data-used-autnums"
    ip_asn_url = "http://thyme.apnic.net/current/data-raw-table"
    asn_isp_prefix = "pyisp_asn_isp_db_"
    ip_asn_prefix = "pyisp_ip_asn_db_"

    def __init__(self, refresh_days=14, cache_dir=None):

        # initialize some variables
        self._refresh_seconds = refresh_days*86400
        self._cache_dir = cache_dir
        if not self._cache_dir:
            self._cache_dir = os.path.join(gettempdir(), 'pyisp')

        # if a cache directory was specified, find the latest files
        if os.path.isdir(self._cache_dir):
            asn_isp_file = self._find_latest_filename_in_dir(self._cache_dir, self.asn_isp_prefix)
            ip_asn_file = self._find_latest_filename_in_dir(self._cache_dir, self.ip_asn_prefix)
            # compute the timestamp
            self._last_refresh = self._extract_timestamp_from_filename(asn_isp_file)
            # sanity check that both files are in sync
            if self._last_refresh != self._extract_timestamp_from_filename(ip_asn_file):
                self._last_refresh = 0
        else:
            os.mkdir(self._cache_dir)
            self._last_refresh = 0

        # if files are too old (or missing), then refresh
        if time.time() > self._last_refresh + self._refresh_seconds:
            self._refresh()

        # else load from the files
        else:
            with open(os.path.join(self._cache_dir, asn_isp_file), 'rb') as f:
                asn_isp_raw = f.read()
            with open(os.path.join(self._cache_dir, ip_asn_file), 'rb') as f:
                ip_asn_raw = f.read() 
            self._build_radix_tree(asn_isp_raw, ip_asn_raw)

        self.is_busy = False

    def _find_latest_filename_in_dir(self, dirname, file_prefix):
        if not os.path.isdir(dirname):
            raise RuntimeError("directory %s does not exist" % dirname)

        # find all files matching pattern
        candidates = [fn for fn in os.listdir(dirname) if fn.startswith(file_prefix)]

        # grab the latest one
        if len(sorted(candidates)) > 0:
            return candidates[-1]
        else:
            return None

    def _extract_timestamp_from_filename(self, fn):
        if fn is not None:
            m = re.search(r'\d+$', fn)
            return int(m.group(0))
        else:
            return 0

    def _build_radix_tree(self, asn_isp_raw, ip_asn_raw):
        self._rtree = radix.Radix()

        # build the asn -> ISP lookup
        asn_isp_map = {}
        lines = asn_isp_raw.decode('utf-8', 'ignore').splitlines()
        for line in lines:
            tokens = line.split()
            try:
                asn = int(line[:6])  # this occasionally fails, so skip if so
            except:
                continue
            isp = line[7:]
            asn_isp_map[asn] = isp
    
        # build the ipaddr -> ASN lookup
        lines = ip_asn_raw.decode('utf-8', 'ignore').splitlines()
        for line in lines:
            tokens = line.split()
            ipmask = tokens[0]
            asn = int(tokens[1])
        
            rnode = self._rtree.add(ipmask)
            rnode.data['asn'] = asn
            try:
                rnode.data['isp'] = asn_isp_map[asn]
            except:
                rnode.data['isp'] = ''

    def _refresh(self):
        self.is_busy = True
        print("Fetching from %s" % self.asn_isp_url)
        with urllib.request.urlopen(self.asn_isp_url) as response:
            asn_isp_raw = response.read()

        print("Fetching from %s" % self.ip_asn_url)
        with urllib.request.urlopen(self.ip_asn_url) as response:
            ip_asn_raw = response.read()

        self._build_radix_tree(asn_isp_raw, ip_asn_raw)
        self._last_refresh = int(time.time())
        self._save_files(asn_isp_raw, ip_asn_raw)
        self.is_busy = False

    def _save_files(self, asn_isp_raw, ip_asn_raw):
        if self._cache_dir is None:
            return

        timestamp = str(self._last_refresh)
        asn_isp_file = os.path.join(self._cache_dir, self.asn_isp_prefix + timestamp)
        ip_asn_file = os.path.join(self._cache_dir, self.ip_asn_prefix + timestamp)

        with open(asn_isp_file, 'wb') as f:
            f.write(asn_isp_raw)

        with open(ip_asn_file, 'wb') as f:
            f.write(ip_asn_raw)

    def isp(self, ipaddress):
        # do we need to refresh the database?
        if time.time() > self._last_refresh + self._refresh_seconds:
            self._refresh()

        # convert ip to string (in case somebody sent int)
        ipaddress = str(ip_address(ipaddress))

        response = ISPResponse()
        rnode = self._rtree.search_best(ipaddress)
        if rnode is None:
            return None
        response.autonomous_system_number = rnode.data['asn']
        response.autonomous_system_organization = rnode.data['isp']

        return response
