import traceback

from bs4 import BeautifulSoup
from couchpotato.core.helpers.encoding import tryUrlencode, toUnicode
from couchpotato.core.helpers.variable import tryInt
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider


log = CPLog(__name__)


class Base(TorrentProvider):

    urls = {
        'test': 'https://www.funfile.org/',
        'login': 'https://www.funfile.org/takelogin.php',
        'login_check': 'https://www.funfile.org/my.php',
        'detail': 'https://www.funfile.org/details.php?id=%s',
        'search': 'https://www.funfile.org/browse.php?search=%s&cat=19&incldead=0&s_title=1&showspam=0',
        'download': 'https://www.funfile.org/download.php/%s/%s',
    }

    quality_map = {
        '720p': '720p x264',
        '1080p': '1080p x264',
        'BR-Rip': 'BDRip x264',
        'BR-Disk': 'Bluray',
        'DVD-Rip': 'DVDRip x264',
    }

    http_time_between_calls = 1 #Seconds

    def getQuality(self, quality = None):

        if not quality: return ''
        identifier = quality.get('identifier')
        return self.quality_map.get(identifier, '')

    def _searchOnTitle(self, title, movie, quality, results):

        url = self.urls['search'] % tryUrlencode('%s %s %s' % (title.replace(':', '').replace(' ', '.'), movie['info']['year'], self.getQuality(quality)))
        data = self.getHTMLData(url)

        if data:
            html = BeautifulSoup(data)

            try:
                result_table = html.find('table', attrs = {'cellspacing':'0', 'cellpadding':'2'})
                if not result_table:
                    return

                entries = result_table.find_all('tr')

                for result in entries[1:]:

                    cells = result.find_all('td')

                    if len(cells) > 6:

                        torrent = cells[1].find('a', attrs = {'style': 'float: left; vertical-align: middle; font-weight: bold;'})

                        if torrent:

                            torrent_id = torrent['href']
                            torrent_id = torrent_id.replace('details.php?id=', '')
                            torrent_id = torrent_id.replace('&hit=1', '')

                            torrent_name = torrent.getText()

                            results.append({
                                'id': torrent_id,
                                'name': torrent_name,
                                'url': self.urls['download'] % (torrent_id, torrent_name + '.torrent'),
                                'detail_url': self.urls['detail'] % torrent_id,
                                'size': self.parseSize(cells[7].contents[0] + cells[7].contents[2]),
                                'seeders': tryInt(cells[9].find('span').contents[0]),
                                'leechers': tryInt(cells[10].find('span').contents[0]),
                            })

            except:
                log.error('Failedtoparsing %s: %s', (self.getName(), traceback.format_exc()))

    def getLoginParams(self):
        return {
            'username': self.conf('username'),
            'password': self.conf('password'),
            'login': 'Login',
        }

    def loginSuccess(self, output):
        return 'logout.php' in output.lower()

    loginCheckSuccess = loginSuccess


config = [{
    'name': 'funfile',
    'groups': [
        {
            'tab': 'searcher',
            'list': 'torrent_providers',
            'name': 'Funfile',
            'description': '<a href="http://funfile.org">Funfile</a>',
            'wizard': True,
            'icon': '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',
            'options': [
                {
                    'name': 'enabled',
                    'type': 'enabler',
                    'default': False,
                },
                {
                    'name': 'username',
                    'default': '',
                },
                {
                    'name': 'password',
                    'default': '',
                    'type': 'password',
                },
                {
                    'name': 'seed_ratio',
                    'label': 'Seed ratio',
                    'type': 'float',
                    'default': 1,
                    'description': 'Will not be (re)moved until this seed ratio is met.',
                },
                {
                    'name': 'seed_time',
                    'label': 'Seed time',
                    'type': 'int',
                    'default': 40,
                    'description': 'Will not be (re)moved until this seed time (in hours) is met.',
                },
                {
                    'name': 'extra_score',
                    'advanced': True,
                    'label': 'Extra Score',
                    'type': 'int',
                    'default': 20,
                    'description': 'Starting score for each release found via this provider.',
                }
            ],
        },
    ],
}]
