``python-lsp-pylama``
=====================

``python-lsp-pylama`` is a plugin for `python-lsp-server` that makes it aware
of ``pylama``.

Install
-------

In the same `virtualenv` as `python-lsp-server`:

.. code-block::

    > python -m pip install python-lsp-pylama

And then in your configuration for ``python-lsp-server``:

.. code-block::

    settings = {
        pylsp = {
            plugins = {
                pylama = { enabled = true },
            }
        }
    }
