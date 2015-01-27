from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.funfile import Base
from couchpotato.core.media.movie.providers.base import MovieProvider

log = CPLog(__name__)

autoload = 'Funfile'


class Funfile(MovieProvider, Base):
    pass
