# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import os
import re
import glob
import yt_dlp
import random
import asyncio
import aiohttp
from pathlib import Path

# Patch py_yt API key at import time so Railway fresh Docker installs use our key
try:
    import py_yt.core.constants as _yt_const
    import py_yt.core.video as _yt_video
    _YT_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyBza3ew7sdakHkF3irNQwRotoXi_6q84ug")
    _yt_const.searchKey = _YT_API_KEY
    for _client in _yt_video.CLIENTS.values():
        _client["api_key"] = _YT_API_KEY
except Exception:
    pass

from py_yt import Playlist, VideosSearch

from anony import logger
from anony.helpers import Track, utils


class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = False
        self.cookie_dir = "anony/cookies"
        self.warned = False
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )
        self.iregex = re.compile(
            r"https?://(?:www\.|m\.|music\.)?(?:youtube\.com|youtu\.be)"
            r"(?!/(watch\?v=[A-Za-z0-9_-]{11}|shorts/[A-Za-z0-9_-]{11}"
            r"|playlist\?list=PL[A-Za-z0-9_-]+|[A-Za-z0-9_-]{11}))\S*"
        )
        os.makedirs(self.cookie_dir, exist_ok=True)
        os.makedirs("downloads", exist_ok=True)
        self._load_env_cookies()

    def _load_env_cookies(self):
        cookies_txt = os.getenv("COOKIES_TXT", "").strip()
        if cookies_txt:
            cookie_path = f"{self.cookie_dir}/env_cookies.txt"
            try:
                import base64
                decoded = base64.b64decode(cookies_txt).decode("utf-8")
                with open(cookie_path, "w") as f:
                    f.write(decoded)
                logger.info("Cookies loaded from COOKIES_TXT env var.")
            except Exception:
                with open(cookie_path, "w") as f:
                    f.write(cookies_txt)
                logger.info("Cookies loaded from COOKIES_TXT env var (plain text).")

    def get_cookies(self):
        if not self.checked:
            self.cookies = []
            for file in os.listdir(self.cookie_dir):
                if file.endswith(".txt"):
                    self.cookies.append(f"{self.cookie_dir}/{file}")
            self.checked = True
        if not self.cookies:
            if not self.warned:
                self.warned = True
                logger.warning("Cookies missing; using mobile client fallback.")
            return None
        return random.choice(self.cookies)

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("Saving cookies from urls...")
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    name = url.rstrip("/").split("/")[-1]
                    fetch_url = "https://batbin.me/raw/" + name if "batbin.me" in url else url
                    async with session.get(fetch_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                        resp.raise_for_status()
                        with open(f"{self.cookie_dir}/{name}.txt", "wb") as fw:
                            fw.write(await resp.read())
                    logger.info(f"Cookie saved: {name}.txt")
                except Exception as e:
                    logger.warning(f"Failed to save cookie from {url}: {e}")
        self.checked = False
        logger.info(f"Cookies saved in {self.cookie_dir}.")

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    def invalid(self, url: str) -> bool:
        return bool(re.match(self.iregex, url))

    def _find_downloaded(self, video_id: str) -> str | None:
        """Find the actual downloaded file regardless of extension."""
        matches = glob.glob(f"downloads/{video_id}.*")
        if matches:
            return matches[0]
        return None

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        try:
            _search = VideosSearch(query, limit=1, with_live=False)
            results = await _search.next()
        except Exception:
            return None
        if results and results["result"]:
            data = results["result"][0]
            return Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name"),
                duration=data.get("duration"),
                duration_sec=utils.to_seconds(data.get("duration")),
                message_id=m_id,
                title=data.get("title")[:25],
                thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                url=data.get("link"),
                view_count=data.get("viewCount", {}).get("short"),
                video=video,
            )
        return None

    async def playlist(self, limit: int, user: str, url: str, video: bool) -> list[Track | None]:
        tracks = []
        try:
            plist = await Playlist.get(url)
            for data in plist["videos"][:limit]:
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")),
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails")[-1].get("url").split("?")[0],
                    url=data.get("link").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
        except Exception:
            pass
        return tracks

    async def download(self, video_id: str, video: bool = False) -> str | None:
        url = self.base + video_id

        # Check if already downloaded (any extension)
        existing = self._find_downloaded(video_id)
        if existing:
            return existing

        cookie = self.get_cookies()

        base_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "no_warnings": True,
            "overwrites": False,
            "nocheckcertificate": True,
            "retries": 5,
            "fragment_retries": 5,
            "extractor_args": {
                "youtube": {
                    "player_client": ["tv_embed", "web_creator", "android", "web"],
                }
            },
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (Linux; Android 12; SM-G991B) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Mobile Safari/537.36"
                ),
            },
        }

        if cookie:
            base_opts["cookiefile"] = cookie

        if video:
            ydl_opts = {
                **base_opts,
                "format": "bestvideo[height<=?720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=?720]+bestaudio/best[height<=?720]/best",
                "merge_output_format": "mp4",
            }
        else:
            ydl_opts = {
                **base_opts,
                # Prefer audio-only; falls back to best combined (pytgcalls extracts audio)
                "format": "bestaudio[acodec=opus]/bestaudio[ext=m4a]/bestaudio/best",
            }

        def _download():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except yt_dlp.utils.DownloadError as e:
                logger.warning("yt-dlp DownloadError: %s", str(e)[:300])
                return None
            except Exception as ex:
                logger.warning("Download exception: %s", ex)
                return None

            # Find the actual downloaded file (extension may differ)
            result = self._find_downloaded(video_id)
            if not result:
                logger.warning("Download completed but file not found: %s", video_id)
            return result

        return await asyncio.to_thread(_download)
