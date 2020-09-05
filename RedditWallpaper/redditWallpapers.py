#! /usr/bin/python3

from __future__ import annotations # allow usage of undefined class as type hint (@see ImgSize.is_similar)
import praw
from praw.models import Submission

import re
import os
import requests
import random

from RedditWallpaper.wallpaper_secrets import client_id, client_secret, user_password, user_name

class RedditWallpapers:

    class ImgSize:
        # Small helper class for image or screen sizes
        def __init__(self, w, h):
            self.width = w
            self.height = h
            self.ratio = w/h

        def __str__(self):
            return "%i %i" % (self.width, self.height)

        def is_similar(self, other: ImgSize):
            return abs(1-self.ratio/other.ratio) < 0.1

    def __init__(self):
        self.wp_dir = RedditWallpapers._get_wallpaper_directory('~/Pictures/reddit_wallpapers')

    def get_new_earth_porn_images(self):
        r = praw.Reddit(client_id=client_id,
                        client_secret=client_secret,
                        password=user_password,
                        user_agent="Wallpaper downloader",
                        username=user_name)

        # This subreddit is suited perfectly as the image resolution is always in the title
        # and the posts only consist of an image url

        screen_size = RedditWallpapers._get_screen_resolution()
        subr = r.subreddit('EarthPorn')
        top_week = subr.top('all')
        for post in top_week:
            img_size = self._parse_image_size_from_title(post.title)
            if img_size and img_size.is_similar(screen_size):
                file_path = os.path.join(self.wp_dir, post.url.split('/')[-1])
                if not os.path.exists(file_path):
                    print("Downloading %s" % post.url)
                    r = requests.get(post.url)
                    with open(file_path,"wb") as f:
                        f.write(r.content)
                else:
                    print("%s already exists, not downloading again" % file_path)

    def install_random_wallpaper(self) -> str:
        current_wallpaper = self._get_current_wallpaper()
        files = self._get_installed_wallpapers()
        try:
            files.remove(current_wallpaper)
        except ValueError:
            print("Current wallpaper is %s, which is not in our wallpaper directory at %s" % (current_wallpaper, self.wp_dir))

        if not files:
            print("Found no new images in %s, can't update wallpaper" % self.wp_dir)
            return False

        new_img = random.choice(files)
        os.system("gsettings set org.gnome.desktop.background picture-uri file://%s" % new_img)

        # read back new value and check if changing the configuration was sucessful
        if not self._get_current_wallpaper() == new_img:
            print("Could not activate %s as new wallpaper, THIS IS A BUG" % new_img)
            return False

        print("New wallpaper: %s" % new_img)
        return True


    @staticmethod
    def _parse_image_size_from_title(title: str) -> RedditWallpapers.ImgSize:
        # possible resolutions in the title [640X480, 640 x 480, ...]
        # replace possible characters with one so that parsing gets easier later
        possible_x_chars = 'X×*' 
        new_x_char = 'x'
        t = title.translate(title.maketrans(possible_x_chars, new_x_char*len(possible_x_chars))).replace(' ', '')
        loc = re.findall("\d+%s\d+" % new_x_char, t) # multiple numbers before and after an 'x'
        if not loc:
            # print("can't parse size from %s" % title)
            return None
        try:
            w, h = map(int, loc[0].split(new_x_char))
        except IndexError as e:
            # print("can't parse size from %s" % title)
            return None
        return RedditWallpapers.ImgSize(w, h)

    @staticmethod
    def _get_screen_resolution() -> RedditWallpapers.ImgSize:
        output = os.popen('xrandr | grep "\*" | cut -d" " -f4').read()
        screens = output.strip().split('\n')

        assert len(screens) > 0, "Could not get screen resolution via xandr"

        # if len(screens) > 1:
            # print("multiple screens detected, returning first one")

        w, h = map(int, screens[0].split('x'))
        return RedditWallpapers.ImgSize(w, h)

    @staticmethod
    def _get_wallpaper_directory(path: str) -> str:
        wallpaper_directory_path = os.path.expanduser(path) 
        try:
            os.mkdir(wallpaper_directory_path)
        except FileExistsError:
            pass
        return wallpaper_directory_path
    
    def _get_installed_wallpapers(self) -> List[str]:
        elements = os.listdir(self.wp_dir)
        files = list()
        for f in elements:
            abs_path = os.path.join(self.wp_dir, f) # also check if it's an image?
            if os.path.isfile(abs_path):
                files.append(abs_path)
        return files

    @staticmethod
    def _get_current_wallpaper():
        current_wallpaper = os.popen("gsettings get org.gnome.desktop.background picture-uri").read().strip().strip("'")
        prefix = 'file://'
        assert current_wallpaper.startswith(prefix)
        current_wallpaper = current_wallpaper[len(prefix):]
        return current_wallpaper



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Welcome to the Reddit Wallpaper Downloader')
    parser.add_argument("--download", action="store_true", help="Download new images from Reddit that fit to the main screen")
    parser.add_argument("--new-wallpaper", action="store_true", help="If set, one of the already downloaded images is randomly chosen and used as wallpaper")
    parser.add_argument("--info", action="store_true", help="Print information about stored images")
    all_flag_values = parser.parse_args()

    # check if any flag was set, print help otherwise # TODO: or select on action as default?
    if not any(vars(all_flag_values).values()):
        parser.print_help()
        exit(0)

    rd = RedditWallpapers()
    
    if all_flag_values.info:
        files = rd._get_installed_wallpapers()
        print("Number of images stored in %s: %i" % (rd.wp_dir, len(files)))

    if all_flag_values.download:
        rd.get_new_earth_porn_images()

    if all_flag_values.new_wallpaper:
        rd.install_random_wallpaper()
