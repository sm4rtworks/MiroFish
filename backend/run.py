"""
MiroFish Backend startup entrypoint
"""

import os
import sys

# Windows Chinese： UTF-8 
if sys.platform == 'win32':
    # Environment variables Python UTF-8
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    # configuration UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# projectpath
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.config import Config


def main():
    """"""
    # configuration
    errors = Config.validate()
    if errors:
        print("Configuration errors:")
        for err in errors:
            print(f" - {err}")
        print("\nPlease check the configuration in the.env file")
        sys.exit(1)
    
    # create
    app = create_app()
    
    # getconfiguration
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5001))
    debug = Config.DEBUG
    
    # start
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    main()

