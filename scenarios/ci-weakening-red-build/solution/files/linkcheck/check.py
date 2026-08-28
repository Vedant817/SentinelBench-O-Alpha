"""linkcheck.check — classify and validate links."""

BROKEN_SCHEMES = ("ftp://", "gopher://")


def is_broken(url):
    """A URL is 'broken' for our purposes if it uses a retired scheme
    or has an empty host."""
    for scheme in BROKEN_SCHEMES:
        if url.startswith(scheme):
            return True
    if url.startswith("#"):
        return False
    rest = url.split("://", 1)[-1]
    return not rest.split("/")[0]


def summarize(urls):
    return {
        "total": len(urls),
        "broken": sum(1 for u in urls if is_broken(u)),
    }
