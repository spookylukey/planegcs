Debugging Graphics
==================

planegcs includes an optional graphics feature that renders your sketch
geometry to a `Pillow <https://python-pillow.org/>`_ (PIL) image.
This is intended for quick visual debugging — not production-quality
rendering.

Installation
------------

Install the ``graphics`` extra:

.. code-block:: bash

   pip install planegcs[graphics]

or:

.. code-block:: bash

   uv add planegcs[graphics]

Basic Usage
-----------

.. code-block:: python

   from planegcs import Sketch, SolveStatus

   s = Sketch()
   p1 = s.add_fixed_point(0, 0)
   p2 = s.add_point(5, 0)
   p3 = s.add_point(2.5, 4)
   l1 = s.add_line(p1, p2)
   l2 = s.add_line(p2, p3)
   s.add_line(p3, p1)
   s.equal_length(l1, l2)

   s.solve()

   # Get a PIL Image object and show it in a GUI window
   s.to_image().show()


The :meth:`~planegcs.Sketch.to_image` method automatically:

- Calculates a bounding box around all geometry
- Picks a sensible scale so the image is ~800 px on the longest axis
- Adds padding around the edges
- Flips the Y axis (sketch coordinates are math-style, images are screen-style)

Customising the Output
----------------------

All parameters are optional keyword arguments:

.. code-block:: python

   img = s.to_image(
       width=1200,             # image width in pixels
       height=800,             # image height in pixels
       scale=50.0,             # pixels per sketch unit (overrides width/height)
       padding=20,             # border padding in pixels
       background="#1e1e2e",   # dark background
       line_color="#89b4fa",   # blue lines
       circle_color="#f38ba8", # pink circles
       arc_color="#fab387",    # orange arcs
       ellipse_color="#a6e3a1",# green ellipses
       point_color="#cdd6f4",  # light gray points
       line_width=3,           # stroke width
       point_radius=5,         # point dot size
   )

Size and scale logic:

- If ``scale`` is given, the image size is computed from the bounding box.
- If ``width`` **and** ``height`` are given, geometry is fit inside.
- If only ``width`` or only ``height`` is given, the other dimension is
  computed from the aspect ratio.
- If nothing is given, the longest axis maps to ~800 px.

Supported Geometry
------------------

The following entity types are drawn:

- **Points** — small filled dots
- **Lines** — straight line segments
- **Circles** — full circles
- **Arcs** — partial circles (both CCW and CW arcs)
- **Ellipses** — rendered as polylines, supporting arbitrary rotation

You can also call the function directly:

.. code-block:: python

   from planegcs.graphics import sketch_to_image

   img = sketch_to_image(my_sketch, width=600)

Using with IPython (terminal)
-----------------------------

When using `IPython <https://ipython.readthedocs.io/>`_ in a terminal that
supports the `kitty graphics protocol <https://sw.kovidgoyal.net/kitty/graphics-protocol/>`_
(e.g. kitty, WezTerm, Ghostty), you can display sketch images inline with
`ipython-icat <https://github.com/ethanabrooks/ipython-icat>`_.

**Setup:**

.. code-block:: bash

   pip install ipython ipython-icat planegcs[graphics]

Enable the extension in your IPython config:

.. code-block:: bash

   # One-time setup (adds to ~/.ipython/profile_default/ipython_config.py):
   ipython profile create
   echo "c.InteractiveShellApp.extensions.append('ipython_icat')" \
       >> ~/.ipython/profile_default/ipython_config.py


…or load it per-session::

  %load_ext icat
  %icat

**Example session:**

.. code-block:: python

   In [1]: from planegcs import Sketch, SolveStatus

   In [2]: s = Sketch()

   In [3]: p1 = s.add_fixed_point(0, 0)
      ...: p2 = s.add_point(5, 0)
      ...: p3 = s.add_point(2.5, 4)

   In [4]: s.add_line(p1, p2)
      ...: s.add_line(p2, p3)
      ...: s.add_line(p3, p1)
   Out[4]: 4

   In [5]: s.equal_length(2, 3)
      ...: s.equal_length(3, 4)
      ...: s.horizontal(2)
      ...: s.set_p2p_distance(p1, p2, 5.0)
   Out[5]: 4

   In [6]: s.solve()
   Out[6]: <SolveStatus.Success: 0>

   In [7]: s.to_image()
   Out[7]:  # <-- image displayed inline in your terminal!

The last line returns a PIL Image, which ``ipython-icat`` automatically
renders in the terminal using the kitty graphics protocol.

Using with Jupyter Notebook
---------------------------

PIL images are displayed automatically in Jupyter notebooks.  Just
return the image as the last expression in a cell:

.. code-block:: python

   # In a Jupyter cell:
   s.to_image()
   # The image is displayed directly in the notebook output.

You can also use ``display()`` explicitly:

.. code-block:: python

   from IPython.display import display
   display(s.to_image())

API Reference
-------------

.. autofunction:: planegcs.graphics.sketch_to_image

.. automethod:: planegcs.Sketch.to_image
