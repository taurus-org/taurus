.. currentmodule:: {{ info['modulename'] }}

:mod:`{{info['modulename']}}`
{{ '=' * (info['modulename']|count + 7 ) }}

.. automodule:: {{info['modulename']}}

{% if info['submodules']|count >0 %}
.. rubric:: Modules

.. toctree::
    :maxdepth: 1
{% for sm in info['submodulenames'] %}
    {{ sm }} <{{ info['basemodulename'] }}/{{ sm }}>
{% endfor %}
{% endif %}
    
{% if info['localenumerationnames']|count >0 %}
.. rubric:: Enumerations

{% for c in info['localenumerationnames'] %}
	* :obj:`{{ c }}`
{% endfor %}
{% endif %}

{% if info['localclassnames']|count >0 %}
.. rubric:: Classes

.. toctree::
    :hidden:
{% for c in info['localclassnames'] %}
    {{ info['basemodulename'] }}/_{{ c }}.rst
{% endfor %}

.. hlist::
    :columns: 2
{% for c in info['localclassnames'] %}
    * :class:`{{ c }}`
{% endfor %}
{% endif %}

{% if info['localfunctionnames']|count >0 %}
.. rubric:: Functions

{% for f in info['localfunctionnames'] %}
.. autofunction:: {{ f }}
{% endfor %}
{% endif %}

{% if info['externalmembers']|count >0 %}
.. rubric:: External Members

.. hlist::
    :columns: 2
{% for m in info['externalmembers'] %}
    * :obj:`{{ m }}`
{% endfor %}
{% endif %}