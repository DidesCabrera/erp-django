def build_form_fields(form):

    fields = []

    for field in form:

        input_type = field.field.widget.input_type

        fields.append({
            "name": field.name,
            "label": field.label,
            "field_value": field.value(),
            "type": input_type,
            "step": "any" if input_type == "number" else None,
            "errors": list(field.errors) if form.is_bound else []
        })

    return fields