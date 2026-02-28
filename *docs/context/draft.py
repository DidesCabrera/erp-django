<div class="card-title-comp">

  <div class="label-entity label-entity--{{ titulo.label|lower|cut:" " }}">
    {{ titulo.label }}
  </div>

  <div class="label-fork">#variante</div>

  <h3>{{ titulo.name }}</h3>

  <div class="label-class">
    {% for class in titulo.classes %}
      <span class="class-tag">{{ class }}</span>
    {% endfor %}
  </div>

  <div class="structural-indicators">
    <p>
      {% if titulo.structural_indicators.meals_count %}
        {{ titulo.structural_indicators.meals_count }} Comidas | 
      {% endif %}
      {{ titulo.structural_indicators.foods_count }} Alimentos
    </p>
  </div>

  <p class="btn-desplegar-tabla">Ver tabla</p>

</div>



-----

/* =========================
--------- TITLE -----------
========================= */

.card-title {
    font-size: 12px;
    width: 250px;
    padding: 4px 8px 4px 4px;
    margin-right: 5px;
}

/* Variacion para detail*/
.card-title.main {
  padding: 0px;
  width: 100%;
  margin-bottom: 15px;
}

  /* Contenedor relativo para posicionar label-fork */
.card-title-comp {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: flex-start; /* Esto hace que los hijos se ajusten a su contenido, no al ancho completo. */
    height: 100%; /* importante si quieres que tenga fondo completo */
}

.card-title-comp h3 {
  margin: 0;
  margin-bottom: 0px;
  font-size: 18px;
  font-weight: 600;
  padding: 0px;
}

.card-title-comp.mini h3 {
  color: white;
}

  /*--- LABEL ------ */
.label-entity{
  padding: 1px 6px;
  margin-bottom: 5px;
  border-radius: 3px;
  color: white;
  font-weight: 500;
  display: inline-block;
}

.label-entity.page-modal{
  margin-bottom: 10px;
}

.label-entity--meal {background-color: var(--color-meal);}
.label-entity--dailyplan {background-color: var(--color-dailyplan);}
.label-entity--program {background-color: var(--color-program);}


/* label-fork arriba derecha */
.label-fork {
  position: absolute;
  top: 0;
  right: 0;
  padding: 0px 4px; 
  font-size: 11px;
  font-weight: 300;
  opacity: 0.7;
}

.label-fork.mini {
  color:rgba(255, 255, 255, 0.9);
}


/* Classes horizontales */
.label-class {
  display: flex;
  gap: 6px;              /* espacio entre etiquetas */
  margin-bottom: 8px;
}

/* Tag individual (opcional pero limpio) */
.class-tag {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
  background: rgba(0,0,0,0.06);
}

/* Botón azul pegado a la derecha */
.btn-desplegar-tabla {
  /*margin-top: auto;    🔥 lo empuja hacia abajo */
  
  width: fit-content;
  color: #1e6bff;
  height: 12px;
  font-size: 12px;
  font-weight: 400;
  cursor: pointer;
}


.block-title-card-edit {
  display: flex;
  align-items: center;        /* ← centra verticalmente */
  justify-content: space-between; /* ← separa izquierda / derecha */
  /* width: 100%; */
}

.block-title-card-edit button{
  height: 33px;
  margin-left: 20px;
}

.structural-indicators{
  background-color: rgb(88, 88, 88);
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;

}
