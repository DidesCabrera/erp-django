ESTE ES EL HTML DE PICKER MEAL ....


N<!-- FORM -->
<form method="post"
      action="{% url 'dailyplan_add_meal' main_id %}"
      id="dp-form">

  {% csrf_token %}

  <div class="page-add">

    <!-- SEARCH - PICKER-->
    <div class="add-title">
      <i data-lucide="plus" class="add-row-icon"></i>
      <i data-lucide="salad" class="add-row-icon"></i>
      <h4 id="meal-form-title">Agrega una Comida</h4>
    </div>

    <div class="add-row">

      <div id="meal-picker" class="selector">
        <input
          type="text"
          id="meal-search"
          placeholder="Escribe la comida…"
          autocomplete="off"
        />
        <ul id="meal-list" class="selector-list"></ul>
      </div>
      
      <input type="hidden" id="dp-selected-meal-id" name="meal_id">
      
      <div class="btn-create-picker">
        <a href="{% url 'create_meal_for_dailyplan' main_id %}"
        class="btn btn-sm btn-outline-primary">
        o Crear nueva Comida
        </a>
      </div>

    </div>

    <!-- PREVIEW :::::::::::::::::::::::::::::::::::::::::::::::-->
    <div id="dp-preview" style="display:none;">

      <div class="picker-layout card">
    
        <!-- LEFT : MEAL INFO -->
        <div class="picker-section picker-meal-info">
          {% include "components/card_picker_meal.html" %}
        </div>
    
    
    
        <!-- RIGHT : IMPACT -->
        <div class="picker-section picker-impact">
    
          <div data-scope="day-preview">

            <h3>Preview</h3>
            <div class="preview-picker">
              <table class="table-foods table-preview-picker">

                <thead>
                  <tr>
                    <th>
                      <i data-lucide="box" class="add-row-icon"></i>
                    </th>
                    <th>
                      <i data-lucide="plus" class="add-row-icon"></i>
                      <i data-lucide="salad" class="add-row-icon"></i>
                    </th>
              
                    <th>
                      <i data-lucide="equal" class="add-row-icon"></i>
                      <i data-lucide="clipboard-list" class="add-row-icon"></i>
                    </th>
              
                    <th></th> <!-- NUEVA COLUMNA PPK -->
              
                    <th></th> <!-- ALLOC -->
              
                  </tr>
                </thead>
              
              
                <tbody>
              
                  <!-- KCAL -->
                  <tr>
              
                    <td class="kcal-col">Kcal</td>
              
                    <td class="impact-positive">
                      +<span id="dp-meal-kcal" data-role="impact-meal-kcal"></span>
                    </td>
              
                    <td>
                      <span id="dp-prev-kcal" data-role="prev-kcal"></span>
                    </td>
              
                    <td></td> <!-- PPK VACIO -->
              
                    <td></td>
              
                  </tr>
              
              
                  <!-- PROTEIN -->
                  <tr>
              
                    <td class="grams-col">Protein</td>
              
                    <td class="impact-positive">
                      +<span id="dp-meal-protein" data-role="impact-meal-protein"></span>g
                    </td>
              
                    <td>
                      <span id="dp-prev-protein" data-role="prev-protein"></span>g
                    </td>
              
                    <!-- NUEVA COLUMNA PPK -->
                    <td>
                      <span
                        class="ppk-inline"
                        data-role="prev-ppk"
                      ></span>
                    </td>
              
                    <td
                      class="alloc-cell"
                      id="dp-prev-alloc-protein-cell"
                      data-role="prev-alloc-protein"
                    >
              
                      <div class="alloc-bar alloc-bar--protein"></div>
              
                      <span
                        class="alloc-text"
                        id="dp-prev-alloc-protein-text"
                        data-role="prev-alloc-protein-text"
                      ></span>
              
                    </td>
              
                  </tr>
              
              
                  <!-- CARBS -->
                  <tr>
              
                    <td class="grams-col">Carbs</td>
              
                    <td class="impact-positive">
                      +<span id="dp-meal-carbs" data-role="impact-meal-carbs"></span>g
                    </td>
              
                    <td>
                      <span id="dp-prev-carbs" data-role="prev-carbs"></span>g
                    </td>
              
                    <td></td> <!-- PPK VACIO -->
              
                    <td
                      class="alloc-cell"
                      id="dp-prev-alloc-carbs-cell"
                      data-role="prev-alloc-carbs"
                    >
              
                      <div class="alloc-bar alloc-bar--carbs"></div>
              
                      <span
                        class="alloc-text"
                        id="dp-prev-alloc-carbs-text"
                        data-role="prev-alloc-carbs-text"
                      ></span>
              
                    </td>
              
                  </tr>
              
              
                  <!-- FAT -->
                  <tr>
              
                    <td class="grams-col">Fat</td>
              
                    <td class="impact-positive">
                      +<span id="dp-meal-fat" data-role="impact-meal-fat"></span>g
                    </td>
              
                    <td>
                      <span id="dp-prev-fat" data-role="prev-fat"></span>g
                    </td>
              
                    <td></td> <!-- PPK VACIO -->
              
                    <td
                      class="alloc-cell"
                      id="dp-prev-alloc-fat-cell"
                      data-role="prev-alloc-fat"
                    >
              
                      <div class="alloc-bar alloc-bar--fat"></div>
              
                      <span
                        class="alloc-text"
                        id="dp-prev-alloc-fat-text"
                        data-role="prev-alloc-fat-text"
                      ></span>
              
                    </td>
              
                  </tr>
              
                </tbody>
              
              </table>
            </div>
          </div>
    
        </div>
    
    
      </div>
      
      <!-- BOTONES =================================== -->
      <div class="actions-row">

        <!-- ⚪ CANCEL -->
        <button type="button" id="btn-cancel-meal-edit" class="btn-cancel-picker">
          Cancelar
        </button>
  
        <!-- 🔵 ADD MODE -->
        <button type="submit" id="btn-add-meal" class="btn-add-picker">
          Agregar Comida al Plan
        </button>
  
        <!-- 🟠 EDIT MODE -->
        <button type="submit" id="btn-update-meal" style="display:none;" class="btn-update-picker">
          Reemplazar Comida en Plan
        </button>
  
      </div>
      
    </div>

  </div>

</form>

{% load static %}

<script>
  window.MEAL_PICKER_MEALS = {{ meals_json|safe }};
  window.MEAL_PICKER_CONTEXT = {{ meal_picker_context|safe }};
  window.dailyplanInitialMeal = {{ selected_meal_id|default:"null" }};
</script>

<script type="module" src="{% static 'notas/js/meal_picker.js' %}"></script>
<script type="module" src="{% static 'notas/js/meal_math.js' %}"></script>
<script type="module" src="{% static 'notas/js/meal_preview.js' %}"></script>
  


NECESITO CAMBIER EL LAYOUT DEL PICKER FOOD EN BASE AL DE PICKER MEAL. 
ME GUSTARÍA PARTIR POR LO SIGUIENTE. SEPERAR LAS SECCIONES IZQUIERDA Y DERECHA, SIGUIENDO LA MISMA IDEA
PORDIRAS REALIZANDO CONSERVANDO LOS ID Y CLASES QUE USA EL JS DE FOOD. PARA QUE SIGA FUNCIONANDO. TE DEJO EL CODIGO
DE PICKER FOOD PARA QUE LO REFACTORICES COMPLETO.

<div class="page-add">

    <!-- SEARCH + PICKER -->
    <div class="add-title">
        <i data-lucide="plus" class="add-row-icon"></i>
        <i data-lucide="carrot" class="add-row-icon"></i>
        <h4 id="food-form-title">Agrega un Alimento</h4>
    </div>
    
    <div class="add-row">
        <div id="food-picker" class="selector">
            <input
            type="text"
            id="food-search"
            placeholder="Escribe el alimento…"
            autocomplete="off"
            />
            <ul id="food-list" class="selector-list"></ul>
        </div>
    </div>
  
    <!-- PREVIEW + FORM -->
    <form
      method="post"
      action="{% url 'add_food_to_meal' main_id %}"
      id="form-preview"
      data-meal-id="{{ main_id }}"
      >
      {% csrf_token %}
  
      <!-- Hidden fields required by backend -->
      <input type="hidden" name="food_id" id="selected-food-id">
      <input type="hidden" name="quantity" id="selected-food-quantity">
      <input type="hidden" id="food-picker-mode" value="add">
      <input type="hidden" name="return_to" value="{{ request.path }}">


      <!-- Edit mode controls -->
      <input type="hidden" id="editing-mealfood-id">
      <input type="hidden" id="editing-original-quantity">


      <!-- FOOD PREVIEW =================================== -->
      <div id="food-preview" style="display:none;">

        <div class="table-items picker">

            <table class="table-foods preview table1" id="table-foods-preview">
                <thead>
                    <tr>
                        <th class="food-name-col">
                            <p class="h3-table2">INFORMACIÓN ALIMENTO</p>
                        </th>
                        <th class="kcal-col-food-table">Kcal</th>
                        <th class="grams-col-food-table">P g</th>
                        <th class="grams-col-food-table">C g</th>
                        <th class="grams-col-food-table">F g</th>
                        <th class="alloc-col alloc-col-food-table">P %kcal</th>
                        <th class="alloc-col alloc-col-food-table">C %kcal</th>
                        <th class="alloc-col alloc-col-food-table">F %kcal</th>
                    </tr>
                </thead>
    
                <tbody>
                    <!-- BASE -->
                    <tr>
                        <td>
                            <p id="preview-name" class="h3-table"></p><span>100g</span>
                        </td>
                        <td><span id="base-kcal"></span></td>
                        <td><span id="base-protein"></span></td>
                        <td><span id="base-carbs"></span></td>
                        <td><span id="base-fat"></span></td>
            
                        <td class="alloc-cell" id="base-alloc-protein-cell">
                            <div class="alloc-bar alloc-bar--protein"></div>
                            <span class="alloc-text" id="base-alloc-protein-text"></span>
                        </td>
            
                        <td class="alloc-cell" id="base-alloc-carbs-cell">
                            <div class="alloc-bar alloc-bar--carbs"></div>
                            <span class="alloc-text" id="base-alloc-carbs-text"></span>
                        </td>
            
                        <td class="alloc-cell" id="base-alloc-fat-cell">
                            <div class="alloc-bar alloc-bar--fat"></div>
                            <span class="alloc-text" id="base-alloc-fat-text"></span>
                        </td>
                    </tr>
                </tbody>
            </table>
            


            <td>Aporte Porción</td>
            <div class="qty-preview">
                <label>
                <input
                    type="number"
                    id="food-quantity"
                    value="100"
                    min="0"
                >
                </label>
            </div>





            <table class="table-foods preview">
                <thead>
                    <tr>
                        <th class="food-name-col">
                            <i data-lucide="box" class="add-row-icon"></i>
                        </th>
                        <th>
                            <i data-lucide="plus" class="add-row-icon"></i>
                            <i data-lucide="carrot" class="add-row-icon"></i>
                        </th>
                    
                        <th>
                            <i data-lucide="equal" class="add-row-icon"></i>
                            <i data-lucide="salad" class="add-row-icon"></i>
                        </th>
                        <th></th>
                    </tr>
                </thead>

                <tbody>

                    <!-- KCAL -->
                    <tr>
                        <td>Kcal</td>
                        <td><span id="qty-kcal"></span></td>
                        <td><span id="meal-prev-kcal"></span></td>
                        <td></td>
                    </tr>

                    <!-- PROTEIN -->
                    <tr>
                        <td>P g</td>
                        <td><span id="qty-protein"></span></td>
                        <td>
                            <span id="meal-prev-protein"></span>
                            <span data-role="prev-ppk">1,6 g/kg</span>
                        </td>

                        <td class="alloc-cell" id="meal-prev-alloc-protein-cell">
                            <div class="alloc-bar alloc-bar--protein"></div>
                            <span class="alloc-text" id="meal-prev-alloc-protein-text"></span>
                        </td>
                    </tr>

                    <!-- CARBS -->
                    <tr>
                        <td>C g</td>
                        <td><span id="qty-carbs"></span></td>
                        <td><span id="meal-prev-carbs"></span></td>

                        <td class="alloc-cell" id="meal-prev-alloc-carbs-cell">
                            <div class="alloc-bar alloc-bar--carbs"></div>
                            <span class="alloc-text" id="meal-prev-alloc-carbs-text"></span>
                        </td>
                    </tr>

                    <!-- FAT -->
                    <tr>
                        <td>F g</td>
                        <td><span id="qty-fat"></span></td>
                        <td><span id="meal-prev-fat"></span></td>

                        <td class="alloc-cell" id="meal-prev-alloc-fat-cell">
                            <div class="alloc-bar alloc-bar--fat"></div>
                            <span class="alloc-text" id="meal-prev-alloc-fat-text"></span>
                        </td>
                    </tr>

                </tbody>
            </table>

        </div>
    
        <!-- BOTONES =================================== -->
        <div class="actions-row">
    
            <!-- 🔵 BOTÓN PARA AGREGAR (ADD MODE) -->
            <button type="submit" id="btn-add-food" class="btn-add-picker">
            Add food to meal
            </button>

            <!-- 🟠 BOTÓN PARA GUARDAR CAMBIOS (EDIT MODE) -->
            <button type="submit" id="btn-update-food" style="display:none;" class="btn-update-picker">
            Save changes
            </button>
        
            <!-- ⚪ CANCELAR EDICIÓN -->
            <button type="button" id="btn-cancel-edit" class="btn-cancel-picker">
            Cancel
            </button>

    
        </div>
    
      </div>
    
    </form>
  
  </div>
  

  <!-- JS DATA -->
  {% load static %}
  <script>
    window.FOOD_PICKER_FOODS = {{ foods_json|safe }};
    window.FOOD_PICKER_CONTEXT = {{ food_picker_context|safe }};
  </script>


  <script type="module" src="{% static 'notas/js/food_math.js' %}"></script>
  <script type="module" src="{% static 'notas/js/food_picker.js' %}"></script>
  <script type="module" src="{% static 'notas/js/food_preview.js' %}"></script>
