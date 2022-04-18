# Flag Downloader

This is a program which will download images for each country
flag listed at [flagcdn.com](https://www.flagcdn.com) (approx.
300 flags). The program is configured to download these flags
at size 40 from the cdn. The point of the program is to
demonstrate the difference between doing these jobs
sequentially, vs. with `threading` or `multiprocessing`. The
time to download is printed when finished. The program is
meant to demonstrate the effectiveness of threading in
IO-bound situations.

The different ways to download flags are represented by
multiple implementations of an abstract `FlagDowloader`
interface.

You can configure the download location for the flags and the
download method with constants at the top of `flags.py`.

This project was created with Python 3.8.
