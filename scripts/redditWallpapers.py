#! /usr/bin/python3
from __future__ import annotations

import praw
from praw.models import Submission

import re
import os
import requests
import random
from wallpaper_secrets import client_id, client_secret, user_password, user_name


class RedditWallpapers:
    def __init__(self):
        super().__init__()
        self.wp_dir = RedditWallpapers._get_wallpaper_directory()


    class ImgSize:
        def __init__(self, w, h):
            self.width = w
            self.height = h
            self.ratio = w/h

        def __str__(self):
            return "%i %i" % (self.width, self.height)

        def is_similar(self, other: ImgSize):
            return abs(1-self.ratio/other.ratio) < 0.1

    @staticmethod
    def _parse_image_size_from_title(title: str) -> RedditWallpapers.ImgSize:
        x_chars = 'X×*'
        t = title.translate(title.maketrans(x_chars, 'x'*len(x_chars))).replace(' ', '')
        loc = re.findall("\d+x\d+", t) 
        if not loc:
            print("can't parse size from %s" % title)
            return None
        try:
            w, h = map(int, loc[0].split('x'))
        except IndexError as e:
            print("can't parse size from %s" % title)
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
    def _get_wallpaper_directory() -> str:
        wallpaper_directory_path = os.path.expanduser('~/Pictures/reddit_wallpapers') 
        try:
            os.mkdir(wallpaper_directory_path)
        except FileExistsError:
            pass

        return wallpaper_directory_path

    def get_new_earth_images(self):
        r = praw.Reddit(client_id=client_id,
                            client_secret=client_secret,
                            password=user_password,
                            user_agent="Wallpaper downloader",
                            username=user_name)

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
        elements = os.listdir(self.wp_dir)
        files = list()
        print(elements)
        for f in elements:
            abs_path = os.path.join(self.wp_dir, f)
            if os.path.isfile(abs_path):
                files.append(abs_path)
        if not files:
            print("Found no images in %s, can't update wallpaper" % self.wp_dir)
        new_img = random.choice(files)
        os.system("gsettings set org.gnome.desktop.background picture-uri file://%s" % new_img)

# install_random_wallpaper(wp_dir)


if __name__ == "__main__":
    rd = RedditWallpapers()

    # rd.get_new_earth_images()
    rd.install_random_wallpaper()
