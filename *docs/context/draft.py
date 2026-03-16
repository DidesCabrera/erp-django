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
                    <th><i data-lucide="box" class="add-row-icon"></i></th>
              
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

      Me gustaría que el div de la izquierda sea de un ancho de 300px en desktop y 100% en mobil

      Aculmente lo intente pero al parece hay otro elemento que lo hace ser de 371. Entonces no se como hacerlo

      Sospecho que son los elementos que tiene dentro


      