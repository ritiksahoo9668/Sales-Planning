"""Bootstrap 5 widget attribute helpers for Django forms."""


def add_bootstrap_classes(form):
    for field in form.fields.values():
        widget = field.widget
        if hasattr(widget, 'input_type'):
            if widget.input_type in ('checkbox', 'radio'):
                widget.attrs.setdefault('class', 'form-check-input')
            elif widget.input_type == 'file':
                widget.attrs.setdefault('class', 'form-control')
            else:
                widget.attrs.setdefault('class', 'form-control')
        elif widget.__class__.__name__ == 'Select':
            widget.attrs.setdefault('class', 'form-select')
        else:
            widget.attrs.setdefault('class', 'form-control')
