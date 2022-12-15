import sys
import pytest

sys.argv = sys.argv[5:]
sys.exit(pytest.console_main())
