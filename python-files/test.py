{% extends "base.html" %}
{% block content %}
<h2>{{rtype | capitalize}} Report</h2>

{% if rtype == "inventory" %}
<table class="table table-bordered">
  <tr><th>SKU</th><th>Qty</th><th>Value</th></tr>
  {% for r in data %}
  <tr><td>{{r.sku}}</td><td>{{r.qty}}</td><td>{{r.value}}</td></tr>
  {% endfor %}
</table>

{% elif rtype == "sales" %}
<table class="table table-bordered">
  <tr><th>SKU</th><th>Qty Sold</th><th>Revenue</th></tr>
  {% for r in data %}
  <tr><td>{{r.sku}}</td><td>{{r.qty}}</td><td>{{r.revenue}}</td></tr>
  {% endfor %}
</table>

{% elif rtype == "expenses" %}
<table class="table table-bordered">
  <tr><th>Date</th><th>Amount</th><th>Description</th></tr>
  {% for e in data %}
  <tr><td>{{e.date}}</td><td>{{e.amount}}</td><td>{{e.description}}</td></tr>
  {% endfor %}
</table>

{% elif rtype == "pl" %}
<ul>
  <li>Revenue: {{data.revenue}}</li>
  <li>COGS: {{data.cogs}}</li>
  <li>Expenses: {{data.expenses}}</li>
  <li><b>Net Profit: {{data.net}}</b></li>
</ul>
{% endif %}
{% endblock %}
