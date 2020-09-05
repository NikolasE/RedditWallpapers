#! /usr/bin/python3.8

from RedditWallpaper.redditWallpapers import RedditWallpapers
from RedditWallpaper.test_data.earth_titles import titles as earth_titles

import unittest

class parseTitles(unittest.TestCase):
    def test_earth(self):
        for t in earth_titles:
            s = RedditWallpapers._parse_image_size_from_title(t)
            self.assertTrue(200 <= s.width <= 7000, "%i" % s.width)
            self.assertTrue(200 <= s.height <= 7000, "%i" % s.height)
            
    def test_no_size(self):
        s = RedditWallpapers._parse_image_size_from_title("NO_SIZE_HERE")
        self.assertIsNone(s)

if __name__ == '__main__':
    unittest.main()