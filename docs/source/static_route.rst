Static Route
============

.. toctree::
   :maxdepth: 3
   :caption: Contents:

.. click:: riocli.static_route:static_route
   :prog: rio static-route
   :nested: full

Rate limiting
-------------

With SDK v0.12.0 or later and a backend supporting StaticRoute rate limits,
``rio apply`` accepts the following manifest. ``rio static-route inspect``
includes the rate limit returned by the backend.

.. code-block:: yaml

   apiVersion: api.rapyuta.io/v2
   kind: StaticRoute
   metadata:
     name: limited-route
   spec:
     sourceIPRange: [121.2.38.2/32]
     rateLimit:
       average: 100
       period: 1m
       burst: 20

``average`` is required and must be an integer from 1 to 1,000,000. ``period``
is an optional positive Go duration string (for example, ``1m`` or ``500ms``);
the backend defaults it to ``1s``. ``burst`` is an optional non-negative int64;
the backend defaults an omitted or zero burst to ``average``. The CLI preserves
supplied values and leaves defaults to the server.

Limits apply to HTTP/HTTPS traffic per client IP and per Traefik instance.
To disable limiting, reapply with ``rateLimit: null`` or omit ``rateLimit``.
Existing deployments need a restart or reapply to copy updated route settings.
