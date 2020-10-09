# -*- coding: utf-8 -*-
from adsapi import app


if __name__ == '__main__':
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.run(host='0.0.0.0', port=8888, use_evalex=False, threaded=False)
