Outline of ``importopoi`` motivation
------------------------------------

This library stemmed from the idea that it was simpler to understand a high-level
design by seeing a high-level abstraction of information flow through code, which
if not in a full package form, should at least consist of multiple modules.

This leads to diagrams which are often suggestive of the proper structure,
and thus are helpful to a programmer to figure out what to rewrite.
Gaps in the graph (diagram) can likewise indicate where to start developing,
or where to fix something missed, or asymmetrical, etc.

In addition to 'module flow', there is the similar concern of the flow through
class hierarchies.

Example
=======

Here's an example of Lorem ipsum.

.. code:: py

   print(1)

   print(2)

⇣

.. code:: py

   1
   2

Further foo, bar, baz.
