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
    },

The options also include ``args`` which are a list of strings that are added to the
command line arguments used for ``pylama``.

Note that if you have `noseOfYeti <https://noseofyeti.readthedocs.io/en/latest/>`_
installed, then it will know how to transform any ``spec`` coding tests so that it may
run ``pylama`` over them.
