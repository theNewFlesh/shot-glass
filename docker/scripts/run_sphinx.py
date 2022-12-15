import sys
sys.argv = ['-M'] + sys.argv[5:]

from sphinx.cmd.build import main
sys.exit(main())