#!/usr/bin/python3

import sys
import re
import subprocess
import urllib.parse

def read_stdin(prompt):
    print(prompt, end = "", flush = True)
    for line in sys.stdin:
        return(line.strip())

def lrc2txt(lrc_filename, txt_filename):
    txt = open(txt_filename, "w")
    with open(lrc_filename) as lrc:
        prev_line = ""
        for count, line in enumerate(lrc):
            line = line.strip()
            line = re.sub("\A\[[0-9:.]+\]", "", line)

            if line != "" and line != prev_line:
                txt.write(line + "\n")
                prev_line = line

def print_banner(message):
    full_msg = "+" + ("-" * 68) + "+\n"

    for line in message.splitlines():
        full_msg += "| " + line
        full_msg += " " * (66 - len(line))
        full_msg += " |\n"

    full_msg += "+" + ("-" * 68) + "+"
    print(full_msg)

def update_youtube_dl():
    print_banner("Update in progress.\nPlease wait")

    subprocess.run([
            "python", "lib\youtube-dl",
            "--version"
        ])

    update_proc = subprocess.run([
            "python", "lib\youtube-dl",
            "--update"
        ])
    if update_proc.returncode != 0:
        print_banner("Update failure")

def download_audio(youtube_url):
    p = subprocess.run([
            "python", "lib\youtube-dl",
            "--output", "%(id)s.%(ext)s", "--restrict-filenames",
            "-f", "bestaudio",
            "--write-auto-sub", "--convert-subs", "lrc",
            youtube_url
        ])
    return p.returncode

def get_filename_prefix(youtube_url):
    p = subprocess.run([
            "python", "lib\youtube-dl",
            "--output", "%(id)s.%(ext)s", "--restrict-filenames",
            "--get-filename",
            youtube_url
        ], shell=True, stdout=subprocess.PIPE)

    if p.returncode != 0:
        return None

    filename_full = p.stdout.decode('utf-8').strip()
    filename_prefix = re.sub("\.[0-9a-z]+\Z", "", filename_full)
    return filename_prefix

def youtube_url_filter_query(ori_url):
    parse_result = urllib.parse.urlparse(ori_url)
    query_dict = urllib.parse.parse_qs(parse_result.query)
    video_id = query_dict.get("v")
    if video_id != None:
        video_id = video_id[0]

    if video_id == None:
        return(ori_url)

    clean_url = urllib.parse.urlunparse((
            parse_result.scheme,
            parse_result.netloc,
            parse_result.path,
            parse_result.params,
            urllib.parse.urlencode({"v": [video_id]}, doseq=True),
            parse_result.fragment,
        ))
    return(clean_url)

def open_file_with_notepad(txt_filename):
    subprocess.run([
            "notepad",
            txt_filename
        ])

if len(sys.argv) == 2 and sys.argv[1] == "--update":
    update_youtube_dl()
    sys.exit()

print("Hint: Right-click to paste, and press Enter")
youtube_url = read_stdin("Please enter the YouTube video URL: ")
if youtube_url == "":
    sys.exit()

youtube_url = youtube_url_filter_query(youtube_url)

print_banner("Please wait...")
filename_prefix = get_filename_prefix(youtube_url)
if filename_prefix == None:
    print_banner("Invalid YouTube video URL")
    sys.exit()

print_banner("Audio and subtitles downlaod in progress.\nPlease wait")
if download_audio(youtube_url) != 0:
    print_banner("Download failure")

lrc_filename = filename_prefix + ".en.lrc"
txt_filename = filename_prefix + ".en.plaintext-subtitle.txt"
lrc2txt(lrc_filename, txt_filename)

print_banner("Opening subtitles with notepad...")
open_file_with_notepad(txt_filename)

