Tengo esta parte de html

<a href="{% url 'dailyplan_list' %}"
    class="nav-tab nav-tab--personal tab-list {% if request.resolver_match.url_name == 'dailyplan_list' %}is-active{% endif %}">
    <i data-lucide="bookmark" class="sidebar-leading-icon"></i>
    <span class="nav-text">
        Mi Libreria
        <div class="nav-indicator"></div>
    </span>    
</a>

y esta estilizado asi...


.nav-tab {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  padding: 3px 8px;
  margin-top: 5px;
  color: inherit;
  cursor: pointer;
  user-select: none;
}

.nav-tab.tab-list {
  margin-top: 2px;
}

Me gustaría que el icono y el span esten uno al lado de otro ambos al lado izquierdfo.