# notas/actions/base.py

def link(label, url, *, enabled=True):
    return {
        "kind": "link",
        "label": label,
        "url": url,
        "enabled": enabled,
    }


def form(label, url, *, enabled=True, method="post"):
    return {
        "kind": "form",
        "label": label,
        "url": url,
        "method": method,
        "enabled": enabled,
    }
