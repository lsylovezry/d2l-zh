# Notes

- Real packet capture requires root or `CAP_NET_RAW`.
- If `--iface any` is used, socket is not explicitly bound.
- For strict load testing without packet I/O bottleneck, use `--dry-run`.
