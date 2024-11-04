# SERVER SIDE FOR ESP DATA COLLECTION

This repository contains:
- configs for deployment to EC2 instance over [terraform code](https://github.com/bespsm/esp-data-collection-tf) (folders: *grafana_cfg*, *script*)
- configs for local deployment over *docker compose* (folders: *docker*)

To deploy server side infrastructure locally (tested on Ubuntu 22.04), run:
```
docker compose up -d
```

License
=======

MIT License, see [LICENSE](LICENSE).