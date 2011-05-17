"""Primary application classes."""

import sys

from cement.core.backend import default_config, get_minimal_logger
from cement.core.exc import CementConfigError
from cement.core.handler import define_handler, register_handler, get_handler
from cement.core.log import ILogHandler, LoggingLogHandler
from cement.core.config import IConfigHandler, ConfigParserConfigHandler

log = get_minimal_logger(__name__)

def lay_cement(app_name, *args, **kw):
    """
    Initialize the framework.

    Required Arguments:
    
        app_name
            The name of the application.
            
        
    Optional Keyword Arguments:

        defaults
            The default config dictionary, other wise use default_config().
            
        argv
            List of args to use.  Default: sys.argv.
    
    """
    
    defaults = kw.get('defaults', default_config())
    argv = kw.get('argv', sys.argv)
    
    # basic logging setup first (mostly for debug/error)
    if '--debug' in argv:
        kw['defaults']['log']['level'] = 'DEBUG'
        kw['defaults']['base']['debug'] = True
        
    define_handler('log', ILogHandler)
    define_handler('config', IConfigHandler)
    #define_handler('output')
    #define_handler('option')
    #define_handler('command')
    #define_handler('hook')
    #define_handler('plugin')
    #define_handler('error')
    
    register_handler(ConfigParserConfigHandler)
    register_handler(LoggingLogHandler)
    
    app = CementApp(app_name, *args, **kw)
    return app
    
class CementApp(object):
    def __init__(self, app_name, **kw):
        self.defaults = kw.get('defaults', default_config())
        if not self.defaults['base']['app_name']:
            self.defaults['base']['app_name'] = app_name

        # initialize handlers if passed in
        self.config = kw.get('config', None)
        self.log = kw.get('log', None)
        self.options = None
        self.commands = None
        
    def run(self):
        self._setup_config()
        self._validate_required_config()
        self._validate_config()
        self._setup_logging()
        
    def load_ext(self, ext_name):
        __import__("cement.ext.ext_%s" % ext_name)
        
    def _setup_config(self):
        if not self.config:
            h = get_handler('config', self.defaults['base']['config_handler'])
            self.config = h()
        
        
        self.config.__cement_init__(self.defaults)
        for _file in self.config.get('base', 'config_files'):
            self.config.parse_file(_file)

    def _setup_logging(self):
        handler = get_handler('log', self.config.get('base', 'log_handler'))
        self.log = handler()
        self.log.__cement_init__(self.config)
        # then setup logging for the app    
        #handler = get_handler('log', self.config.get('base', 'log_handler'))
        #self.log = handler(self.config.get('base', 'app_module'))
        #self.log.setup_logging(
        #    level=self.config.get('base', 'log_level'),
        #    to_console=self.config.get('base', 'log_to_console'),
        #    clear_loggers=self.config.get('base', 'log_clear_loggers'),
        #    log_file=self.config.get('base', 'log_file'),
        #    max_bytes=self.config.get('base', 'log_max_bytes'),
        #    max_files=self.config.get('base', 'log_max_files'),
        #    file_formatter=self.config.get('base', 'log_file_formatter'),
        #    console_formatter=self.config.get('base', 'log_console_formatter'),
        #    )
        
    def _validate_required_config(self):
        """
        Validate base config settings required by cement.
        """
        # need to shorten this a bit
        c = self.config

        if not c.has_key('base', 'app_name') or \
           not c.get('base', 'app_name'):
            raise CementConfigError("config['app_name'] required.")
        if not c.has_key('base', 'app_module') or \
           not c.get('base', 'app_module'):
            c.set('base', 'app_module', c.get('base', 'app_name'))
        if not c.has_key('base', 'app_egg') or \
           not c.get('base', 'app_egg'):
            c.set('base', 'app_egg', c.get('base', 'app_name'))
        
        self.config = c
        
    def _validate_config(self):
        """
        Validate application config settings.
        """
        pass
        