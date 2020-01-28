import unittest

import caliban.docker as d


class DockerTestSuite(unittest.TestCase):
  """Tests for the docker package."""

  def test_shell_dict(self):
    """Tests that the shell dict has an entry for all possible Shell values."""

    self.assertSetEqual(set(d.Shell), set(d.SHELL_DICT.keys()))