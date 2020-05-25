import sys
import os
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.join('..', 'md5model'))))


class TestContext:
    def test_imports(self):
        assert 'md5model' in sys.modules
        attributes = sys.modules['md5model'].__dict__.keys()
        assert 'parsec' in attributes
        assert 'helpers' in attributes
        assert 'md5mesh' in attributes
        assert 'md5anim' in attributes
