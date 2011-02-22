.. currentmodule:: {{ info['modulename'] }}

All Classes for :mod:`{{ info['modulename'] }}`
{{ '=' * (info['modulename']|count + 24 ) }}

.. hlist::
    :columns: 2
{% for c in classes %}
    * :class:`~{{ c }}`
{% endfor %}
