{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

{% block methods %}
{% if methods %}
.. rubric:: Methods

.. autosummary::
   :toctree: .
   :nosignatures:

   {% for item in methods %}
   ~{{ objname }}.{{ item }}
   {%- endfor %}

{% endif %}
{% endblock %}

{% block attributes %}
{% if attributes %}
.. rubric:: Attributes

.. autosummary::
   :toctree: .
   :nosignatures:

   {% for item in attributes %}
   ~{{ objname }}.{{ item }}
   {%- endfor %}

{% endif %}
{% endblock %}
