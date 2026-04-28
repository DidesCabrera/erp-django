entregame estos archivos refactorizados

grid meal edit

<div
    class="data-grid data-grid--meals data-grid--meals-edit js-dpm-sortable"
    data-reorder-url="{% url 'dailyplanmeal_reorder' items.0.main_id %}"
>

    <div class="data-grid-header data-grid-header--meals-edit">
        <div class="data-grid-col data-grid-col--drag"></div>
        <div class="data-grid-col data-grid-col--name">Comidas</div>
        <div class="data-grid-col data-grid-col--kcal">Kcal</div>
        <div class="data-grid-col data-grid-col--macro">P</div>
        <div class="data-grid-col data-grid-col--macro">C</div>
        <div class="data-grid-col data-grid-col--macro">F</div>
        <div class="data-grid-col data-grid-col--alloc">P kcal%</div>
        <div class="data-grid-col data-grid-col--alloc">C kcal%</div>
        <div class="data-grid-col data-grid-col--alloc">F kcal%</div>
        <div class="data-grid-col data-grid-col--action"></div>
        <div class="data-grid-col data-grid-col--action"></div>
        <div class="data-grid-col data-grid-col--action"></div>
    </div>

    {% for row in items %}
        <div class="data-grid-row data-grid-row--meals-edit">

            <div class="data-grid-cell data-grid-cell--name">
                <div class="truncate">{{ row.rel.name }}</div>
            </div>

            <div class="data-grid-cell data-grid-cell--kcal">
                <div class="cell-kcal">{{ row.rel.total_kcal|floatformat:0 }}</div>
            </div>

            <div class="data-grid-cell data-grid-cell--macro">
                {{ row.rel.g_protein|floatformat:1 }}
            </div>

            <div class="data-grid-cell data-grid-cell--macro">
                {{ row.rel.g_carbs|floatformat:1 }}
            </div>

            <div class="data-grid-cell data-grid-cell--macro">
                {{ row.rel.g_fat|floatformat:1 }}
            </div>

            <div class="data-grid-cell data-grid-cell--alloc">
                {% include "components/grid_alloc_item.html" with value=row.rel.alloc_protein kind="protein" %}
            </div>

            <div class="data-grid-cell data-grid-cell--alloc">
                {% include "components/grid_alloc_item.html" with value=row.rel.alloc_carbs kind="carbs" %}
            </div>

            <div class="data-grid-cell data-grid-cell--alloc">
                {% include "components/grid_alloc_item.html" with value=row.rel.alloc_fat kind="fat" %}
            </div>

            <div class="data-grid-cell data-grid-cell--action">
                <button
                    type="button"
                    class="edit-meal-btn"
                    data-dpm-id="{{ row.rel.id }}"
                    data-meal-id="{{ row.child_id }}"
                    data-meal-name="{{ row.rel.name }}"
                    data-protein="{{ row.rel.g_protein }}"
                    data-carbs="{{ row.rel.g_carbs }}"
                    data-fat="{{ row.rel.g_fat }}"
                    data-kcal="{{ row.rel.total_kcal }}"
                    data-hour="{{ row.rel.hour }}"
                    data-note="{{ row.rel.note }}"
                >
                    <i data-lucide="refresh-cw" class="table-icon"></i>
                </button>
            </div>

            <div class="data-grid-cell data-grid-cell--action">
                <form method="post" action="{% url 'dailyplanmeal_remove' row.child_id row.rel.id %}">
                    {% csrf_token %}
                    <input type="hidden" name="return_to" value="{{ request.path }}?panel=edit">
                    <button type="submit">
                        <i data-lucide="trash" class="table-icon"></i>
                    </button>
                </form>
            </div>

        </div>
    {% empty %}
        <div class="data-grid-empty">
            No meals added yet.
        </div>
    {% endfor %}

</div>



grid_meals_mobile_edit


<div class="data-grid data-grid--mobile-meals-edit">

    <div class="data-grid-header data-grid-header--mobile-meals-edit">
        <div class="data-grid-col data-grid-col--name">Comidas</div>
        <div class="data-grid-col data-grid-col--replace"></div>
        <div class="data-grid-col data-grid-col--delete"></div>
    </div>

    {% for row in items %}
        <div class="data-grid-row data-grid-row--mobile-meals-edit">

            <div class="data-grid-cell data-grid-cell--name">
                <div class="truncate">{{ row.rel.name }}</div>
            </div>

            <div class="data-grid-cell data-grid-cell--replace">
                <button
                    type="button"
                    class="edit-meal-btn"
                    data-dpm-id="{{ row.rel.id }}"
                    data-meal-id="{{ row.child_id }}"
                    data-meal-name="{{ row.rel.name }}"
                    data-protein="{{ row.rel.g_protein }}"
                    data-carbs="{{ row.rel.g_carbs }}"
                    data-fat="{{ row.rel.g_fat }}"
                    data-kcal="{{ row.rel.total_kcal }}"
                    data-hour="{{ row.rel.hour }}"
                    data-note="{{ row.rel.note }}"
                >
                    <i data-lucide="refresh-cw" class="table-icon"></i>
                </button>
            </div>

            <div class="data-grid-cell data-grid-cell--delete">
                <form method="post" action="{% url 'dailyplanmeal_remove' row.child_id row.rel.id %}">
                    {% csrf_token %}
                    <button type="submit">
                        <i data-lucide="trash" class="table-icon"></i>
                    </button>
                </form>
            </div>

        </div>
    {% empty %}
        <div class="data-grid-empty">
            No meals added yet.
        </div>
    {% endfor %}

</div>




data grid css

.data-grid {
    width: 100%;
    padding: 6px 10px;
}

.data-grid-header,
.data-grid-row {
    display: grid;
    align-items: center;
    gap: 0px;
}

.data-grid-row:last-of-type {
    border-bottom: none;
}

.data-grid-header--foods,
.data-grid-row--foods {
    grid-template-columns:
        minmax(180px, 1.8fr)
        minmax(56px, 0.7fr)
        minmax(56px, 0.7fr)
        minmax(56px, 0.7fr)
        minmax(56px, 0.7fr)
        minmax(56px, 0.7fr)
        minmax(90px, 1fr)
        minmax(90px, 1fr)
        minmax(90px, 1fr);
}

.data-grid-header--foods-edit,
.data-grid-row--foods-edit {
    grid-template-columns:
        minmax(160px, 1.8fr)
        minmax(56px, 0.7fr)
        minmax(56px, 0.7fr)
        minmax(56px, 0.7fr)
        minmax(56px, 0.7fr)
        minmax(56px, 0.7fr)
        minmax(90px, 1fr)
        minmax(90px, 1fr)
        minmax(90px, 1fr)
        40px
        40px;
}

.data-grid-header--meals,
.data-grid-row--meals {
    grid-template-columns:
        minmax(180px, 1.6fr)
        minmax(60px, 0.65fr)
        minmax(60px, 0.65fr)
        minmax(60px, 0.65fr)
        minmax(60px, 0.65fr)
        minmax(90px, 1fr)
        minmax(90px, 1fr)
        minmax(90px, 1fr);
}

.data-grid-header--meals-edit,
.data-grid-row--meals-edit {
    grid-template-columns:
        minmax(150px, 1.6fr)
        minmax(60px, 0.65fr)
        minmax(60px, 0.65fr)
        minmax(60px, 0.65fr)
        minmax(60px, 0.65fr)
        minmax(90px, 1fr)
        minmax(90px, 1fr)
        minmax(90px, 1fr)
        40px
        40px;
}

@media (max-width: 980px) {
    .data-grid-row--meals-edit {
        grid-template-columns: 1fr;
        gap: 10px;
    }
}

.data-grid-col {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: rgb(95, 95, 95);
    padding-bottom: 8px;
}

.data-grid-row {
    border-bottom: 1px solid var(--color-border-1);
    margin-bottom: 0;
}

.data-grid-cell {
    min-width: 0;
    font-size: 13px;
    font-weight: 400;
    color: rgb(27, 27, 27);
}

.data-grid-cell--name {
    font-weight: 600;
    padding: 8px 0 8px 4px;
}

.data-grid-col--name {
    padding: 0px 0 8px 4px;
}

.data-grid-cell--time,
.data-grid-cell--qty,
.data-grid-cell--kcal,
.data-grid-cell--macro {
    white-space: nowrap;
}

.data-grid-col--time,
.data-grid-col--qty,
.data-grid-col--kcal,
.data-grid-col--macro,
.data-grid-cell--time,
.data-grid-cell--qty,
.data-grid-cell--kcal,
.data-grid-cell--macro {
    text-align: center;
}

.data-grid-cell--alloc {
    min-width: 0;
    margin-right: 8px;
}

.alloc-cell--grid {
    width: 100%;
    min-width: 0;
}

.data-grid-empty {
    padding: 14px 16px;
    border: 1px solid var(--color-border-1);
    border-radius: 10px;
    font-size: 13px;
    color: rgb(70, 70, 70);
}

@media (max-width: 980px) {


    .data-grid-row--foods,
    .data-grid-row--meals {
        grid-template-columns: 1fr;
        gap: 8px;
    }

    .data-grid-cell {
        display: flex;
        gap: 8px;
    }
}


.data-grid-cell--action {
    display: flex;
    align-items: center;
    justify-content: center;
}

.data-grid-cell--action button {
    background: transparent;
    border: none;
    padding: 0;
}

.data-grid-cell--action form {
    margin: 0;
}

@media (max-width: 980px) {
    .data-grid-row--foods-edit {
        grid-template-columns: 1fr;
        gap: 10px;
    }

    .data-grid-cell--action {
        justify-content: flex-start;
    }
}







.data-grid-desktop-cells {
    display: contents;
}


@media (max-width: 980px) {


    .data-grid-mobile-chip {
        font-size: 12px;
        font-weight: 500;
        color: rgb(60, 60, 60);
    }

    .data-grid-mobile-macro {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: rgb(60, 60, 60);
    }

    .data-grid-mobile-macro span {
        font-weight: 500;
        color: rgb(95, 95, 95);
    }

    .data-grid-mobile-macro strong {
        font-weight: 500;
    }

    .alloc-cell--grid {
        width: 100%;
        min-width: 0;
    }
}




.meal-row-desktop {
    display: contents;
}

.meal-row-mobile {
    display: none;
}

.block-mobile-grid-tabs {
    display: none;
}

@media (max-width: 980px) {
    .data-grid-header--meals {
        display: none;
    }

    .block-mobile-grid-tabs {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 10px;
    }

    .btn-mobile-grid-tab {
        height: 28px;
        padding: 0 10px;
        border: 1px solid var(--color-border-1);
        background: transparent;
        border-radius: 999px;
        font-size: 12px;
        cursor: pointer;
    }

    .btn-mobile-grid-tab.is-active {
        background: var(--color-bg-3);
    }

    .data-grid-row--meals {
        grid-template-columns: 1fr;
        gap: 0;
    }

    .meal-row-desktop {
        display: none;
    }

    .card-table-meals[data-mobile-view="menu"] .meal-row-mobile--menu {
        display: block;
    }

    .card-table-meals[data-mobile-view="macros"] .meal-row-mobile--macros {
        display: block;
    }

    .card-table-meals[data-mobile-view="alloc"] .meal-row-mobile--alloc {
        display: block;
    }

    .meal-row-mobile-menu {
        display: grid;
        grid-template-columns: 56px 1fr;
        gap: 10px;
        align-items: center;
    }

    .meal-row-mobile-time {
        font-size: 12px;
        color: rgb(95, 95, 95);
        white-space: nowrap;
    }

    .meal-row-mobile-name {
        font-size: 13px;
        font-weight: 400;
        color: rgb(27, 27, 27);
    }

    .meal-row-mobile-metrics {
        display: flex;
        flex-wrap: wrap;
        gap: 8px 10px;
        margin-top: 6px;
    }

    .meal-row-mobile-kcal {
        font-size: 12px;
        color: rgb(60, 60, 60);
    }

    .meal-row-mobile-macro {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: rgb(60, 60, 60);
    }

    .meal-row-mobile-macro span {
        color: rgb(95, 95, 95);
        font-weight: 500;
    }

    .meal-row-mobile-macro strong {
        font-weight: 500;
    }

    .meal-row-mobile-allocs {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-top: 6px;
    }

    .meal-row-mobile-alloc-row {
        display: grid;
        grid-template-columns: 54px 1fr;
        gap: 8px;
        align-items: center;
    }

    .meal-row-mobile-alloc-label {
        font-size: 11px;
        font-weight: 600;
        color: rgb(95, 95, 95);
        text-transform: uppercase;
    }

    .meal-row-mobile-alloc-row .alloc-cell--grid {
        width: 100%;
        min-width: 0;
    }
}


.data-grid-header--mobile-macros,
.data-grid-row--mobile-macros {
    grid-template-columns:
        minmax(140px, 1.8fr)
        minmax(30px, 1fr)
        minmax(30px, 1fr)
        minmax(30px, 1fr)
        minmax(30px, 1fr);
}

.data-grid-header--mobile-alloc,
.data-grid-row--mobile-alloc {
    grid-template-columns:
        minmax(140px, 1.8fr)
        minmax(40px, 1fr)
        minmax(40px, 1fr)
        minmax(40px, 1fr);
    gap: 6px;
}


.data-grid-header--mobile-foods-qty,
.data-grid-row--mobile-foods-qty {
    grid-template-columns:
        minmax(150px, 1.8fr)
        40px;
}

.data-grid-header--mobile-foods-macros,
.data-grid-row--mobile-foods-macros {
    grid-template-columns:
        minmax(140px, 1.8fr)
        minmax(30px, 1fr)
        minmax(30px, 1fr)
        minmax(30px, 1fr)
        minmax(30px, 1fr)
}

.data-grid-header--mobile-foods-alloc,
.data-grid-row--mobile-foods-alloc {
    grid-template-columns:
        minmax(140px, 1.8fr)
        minmax(40px, 1fr)
        minmax(40px, 1fr)
        minmax(40px, 1fr);
    gap: 6px;
}

.data-grid-header--menu,
.data-grid-row--menu {
    grid-template-columns:
        minmax(110px, 0.7fr)
        minmax(180px, 2.1fr);
    gap: 8px;
}

.data-grid-row--menu {
    align-items: start;
}

.data-grid--menu .data-grid-cell--meal{
    font-weight: 600;
    padding: 9px 0px 9px 4px;

}

.data-grid--menu .data-grid-col--meal {
    font-weight: 600;
    padding: 0 0px 9px 4px;
}

.data-grid--menu .data-grid-cell--foods {
    line-height: 1.35;
}


.data-grid-header--foods-aggregation,
.data-grid-row--foods-aggregation {
    grid-template-columns: 1fr;
}

.data-grid--foods-aggregation .data-grid-cell--foods {
    line-height: 1.35;
}

.data-grid-cell--foods{
    padding: 8px 0;
}

.data-grid--menu .data-grid-cell--meal {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.data-grid--menu .data-grid-meal-name {
    font-weight: 600;
    line-height: 1.2;
}

.data-grid--menu .data-grid-meal-hour {
    font-size: 12px;
    line-height: 1.1;
    font-weight: 400;
    opacity: 0.75;
}

@media (max-width: 980px) {
    .data-grid-header--mobile-macros .data-grid-col--kcal,
    .data-grid-header--mobile-macros .data-grid-col--macro,
    .data-grid-row--mobile-macros .data-grid-cell--kcal,
    .data-grid-row--mobile-macros .data-grid-cell--macro,

    .data-grid-header--mobile-foods-macros .data-grid-col--kcal,
    .data-grid-header--mobile-foods-macros .data-grid-col--macro,
    .data-grid-row--mobile-foods-macros .data-grid-cell--kcal,
    .data-grid-row--mobile-foods-macros .data-grid-cell--macro,

    .data-grid-header--mobile-foods-qty .data-grid-col--qty,
    .data-grid-row--mobile-foods-qty .data-grid-cell--qty,

    .data-grid-col--time,
    .data-grid-cell--time {
        text-align: center;
        justify-content: center;
    }

    .data-grid-cell--alloc {
        margin-right: 0px;
    }
}

.data-grid-header--mobile-foods-edit,
.data-grid-row--mobile-foods-edit {
    grid-template-columns:
        minmax(160px, 1.8fr)
        minmax(40px, 0.4fr)
        minmax(40px, 0.4fr);
}

.data-grid-header--mobile-meals-edit,
.data-grid-row--mobile-meals-edit {
    grid-template-columns:
        minmax(160px, 1.8fr)
        minmax(40px, 0.4fr)
        minmax(40px, 0.4fr);
}

.data-grid-cell--edit,
.data-grid-cell--replace,
.data-grid-cell--delete {
    display: flex;
    align-items: center;
    justify-content: center;
}

.data-grid-cell--edit form,
.data-grid-cell--replace form,
.data-grid-cell--delete form {
    margin: 0;
}

.data-grid-cell--edit button,
.data-grid-cell--replace button,
.data-grid-cell--delete button,
.data-grid-cell--edit form button,
.data-grid-cell--replace form button,
.data-grid-cell--delete form button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    padding: 0;
    
}