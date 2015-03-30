.. currentmodule:: taurus.core

.. _scheme-template:

=====================

Scheme template

=====================

As was describe in the charter before, the core has been designed to provide models

for many libraries. With the scheme template we look for offer a basic scheme skeleton that let the developers create easily new modules for new schemes.

All the Taurus module should follow this rules::

. Must be organized into a folder which name must be like the scheme (lower name).
. The name of the differents files should start with the scheme name (lower name).
. Every module need a empty file, __taurus_plugin__,that identifique the directory as a scheme directory.

=====================

Scheme files

=====================

The model are composed by a tuple of files (attribute, configuration, database, device, factory and validator) some of them could be dummy file. This files must inherit from the corresponding abstract Taurus class, letting manage the different members using  the corresponding abstract class go with a valid model, preserving the scheme-agnostic code.

::

For example, to access a TangoDevice we can use a TaurusDevice(“tango://a/b/c”).

=====================

How to ...

=====================

The idea is to have a dummy module for a new scheme simply by copying the directory **(1)** into the taurus core directory and following the indicated replacements.

. Rename all the files XXXFile by schemeFile
. Edit each file and do the indicated replacements (XXX -> scheme and YYY -> Scheme).

***1***  TAURUS_PATH/doc/source/example/new_scheme/template

::

**Note:** An important aspect to be considered is that these files not provided a new valid module, it is just a template that must be completed.



(:download:`Source code <examples/new_scheme_template/XXXvalidator.py>`)

.. literalinclude:: XXXvalidator.py

  :language: python

  :linenos:

(:download:`Source code <examples/new_scheme_template/XXXfactory.py>`)

.. literalinclude:: XXXfactory.py

  :language: python

  :linenos:

(:download:`Source code <examples/new_scheme_template/XXXdatabase.py>`)

.. literalinclude:: XXXdatabase.py

  :language: python

  :linenos:

(:download:`Source code <examples/new_scheme_template/XXXdevice.py>`)

.. literalinclude:: XXXdevice.py

  :language: python

  :linenos:

(:download:`Source code <examples/new_scheme_template/XXXattribute.py>`)

.. literalinclude:: XXXattribute.py

  :language: python

  :linenos:

(:download:`Source code <examples/new_scheme_template/XXXconfiguration.py>`)

.. literalinclude:: XXXconfiguration.py

  :language: python
  :linenos:
