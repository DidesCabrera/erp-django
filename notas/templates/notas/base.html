<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Notas{% endblock %}</title>

    {% load static %}
    <link rel="stylesheet" href="{% static 'notas/css/tokens.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/base.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/layout.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/utilities.css' %}">

    
    <link rel="stylesheet" href="{% static 'notas/css/components/page.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/page_detail.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/modal_create.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/toast.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/main_header.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/header_list.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/header_detail.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/card_mini_dpm.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/card_child.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/card_father.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/card_title.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/dash_kpi.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/table.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/card_foods_aggregation.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/alloc-bar.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/alloc-cell.css' %}">
    
    <link rel="stylesheet" href="{% static 'notas/css/components/actions.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/breadcrumbs.css' %}">
    
    <link rel="stylesheet" href="{% static 'notas/css/components/food_picker.css' %}">
    <link rel="stylesheet" href="{% static 'notas/css/components/picker_list.css' %}">

</head>

<body>
<div class="container">

    <!-- ======== HEADER ===================================== -->
    <header>
        <div class="header">
            <div class="main-header">

                <!-- ===== FIRST ROW ===== -->
                <div class="header-first-row">
                    <img src="{% static 'img/logo_negro2.png' %}" alt="Logo" class="brand-logo">

                    <div class="user">
                        <div>
                            <p>
                                Mi peso corporal:
                                <button class="btn-weight" onclick="openWeightModal()">
                                    {{ current_weight }}
                                </button> kg
                            </p>
                        </div>

                        {% if request.user.is_authenticated %}
                        <div class="label-rol">
                            {% if request.user.profile.role == "member" %}Member{% endif %}
                            {% if request.user.profile.role == "nutritionist" %}Nutri{% endif %}
                        </div>

                        <h2>
                            <a href="{% url 'profile_detail' %}">
                                {{ request.user.username }}
                            </a>
                        </h2>
                        {% endif %}
                    </div>
                </div>

                <!-- ===== SECOND ROW ===== -->
                <div class="header-second-row">

                    <div class="mn-navbar">
                        <nav>

                            <a href="{% url 'project_view' %}"
                                class="nav-tab nav-tab--project {% if header.nav_context == 'project' %}is-active{% endif %}">
                                <span class="nav-text">Proyecto</span>
                                <div class="nav-indicator"></div>
                            </a>

                            <a href="{% url 'elemental_context' %}"
                                class="nav-tab nav-tab--elemental {% if ui.header.nav_context == 'nutrition' %}is-active{% endif %}">
                                <span class="nav-text">Elementales Nutricion</span>
                                <div class="nav-indicator"></div>
                            </a>

                        </nav>
                    </div>
                
                    <div class="my-navbar">
                        <nav>

                            <a href="{% url 'dailyplan_list' %}"
                                class="nav-tab nav-tab--dailyplan {% if ui.header.nav_context == 'dailyplan' %}is-active{% endif %}">
                                <span class="nav-text">Planes Diarios</span>
                                <div class="nav-indicator"></div>
                            </a>
                            
                            <a href="{% url 'meal_list' %}"
                                class="nav-tab nav-tab--meal {% if ui.header.nav_context == 'meal' %}is-active{% endif %}">
                                <span class="nav-text">Comidas</span>
                                <div class="nav-indicator"></div>
                            </a>
                            
                            <a href="{% url 'food_list' %}"
                                class="nav-tab nav-tab--food {% if vm.header.nav_context == 'food' %}is-active{% endif %}">
                                <span class="nav-text">Alimentos</span>
                                <div class="nav-indicator"></div>
                            </a>

                            <a href="{% url 'inbox_list' %}"
                                class="nav-tab nav-tab--inbox {% if vm.header.nav_context == 'inbox' %}is-active{% endif %}">
                                <span class="nav-text">Notificaciones</span>
                                <div class="nav-indicator"></div>
                            </a>
                        
                         
                        </nav>
                    </div>
                
                </div>
                

            </div>
        </div>
    </header>


    <!-- ========= MODAL PESO ====================== -->
    <div id="weightModal" class="modal hidden">
        <div class="modal-content">

            <h3>Registrar un nuevo peso corporal</h3>

            <form method="post" action="{% url 'weight_register' %}">
                {% csrf_token %}

                <label>Peso (kg)</label>
                <input id="weightInput" type="number" step="0.1" name="weight" required>

                <div class="modal-actions">
                    <button type="submit" class="btn-primary">Confirmar</button>
                    <button type="button" onclick="closeWeightModal()">Cancelar</button>
                </div>
            </form>

        </div>
    </div>

    <script>
        function openWeightModal(){
            const modal = document.getElementById('weightModal');
            modal.classList.remove('hidden');

            // focus automático
            const input = document.getElementById('weightInput');
            if (input) input.focus();
        }

        function closeWeightModal(){
            document.getElementById('weightModal').classList.add('hidden');
        }
    </script>


    <!-- ========= MENSAJES DJANGO ================= -->
    {% if messages %}
    <div class="toast-container">
        {% for message in messages %}
            <div class="toast">
                <span>{{ message }}</span>
                <button class="toast-close" onclick="this.parentElement.remove()">×</button>
            </div>
        {% endfor %}
    </div>
    {% endif %}




    <!-- ======== CONTENT ========================== -->
    <main>
        {% block content %}{% endblock %}
    </main>

</div>
</body>
</html>
