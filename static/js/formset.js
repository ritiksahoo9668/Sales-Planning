/**
 * Dynamic Django inline formset add/remove rows.
 */
(function () {
    function updateManagementForm(prefix, container) {
        const totalForms = document.getElementById('id_' + prefix + '-TOTAL_FORMS');
        if (!totalForms) return;
        const rows = container.querySelectorAll('.formset-row:not(.d-none)');
        totalForms.value = rows.length;
    }

    function cloneRow(container, prefix) {
        const rows = container.querySelectorAll('.formset-row');
        if (!rows.length) return;
        const lastRow = rows[rows.length - 1];
        const newRow = lastRow.cloneNode(true);

        const totalForms = document.getElementById('id_' + prefix + '-TOTAL_FORMS');
        const index = parseInt(totalForms.value, 10);

        newRow.querySelectorAll('input, select, textarea, label').forEach(function (el) {
            if (el.name) {
                el.name = el.name.replace(new RegExp(prefix + '-\\d+-'), prefix + '-' + index + '-');
            }
            if (el.id) {
                el.id = el.id.replace(new RegExp(prefix + '-\\d+-'), prefix + '-' + index + '-');
            }
            if (el.htmlFor) {
                el.htmlFor = el.htmlFor.replace(new RegExp(prefix + '-\\d+-'), prefix + '-' + index + '-');
            }
        });

        newRow.querySelectorAll('input:not([type=checkbox]), textarea').forEach(function (el) {
            el.value = '';
        });
        newRow.querySelectorAll('select').forEach(function (el) {
            el.selectedIndex = 0;
        });
        newRow.querySelectorAll('input[type=checkbox]').forEach(function (el) {
            if (el.name.indexOf('-DELETE') !== -1) {
                el.checked = false;
            }
        });
        newRow.classList.remove('deleted');

        container.appendChild(newRow);
        totalForms.value = index + 1;
    }

    document.addEventListener('click', function (e) {
        const btn = e.target.closest('.add-formset-row');
        if (!btn) return;
        e.preventDefault();
        const target = document.querySelector(btn.dataset.target);
        const prefix = btn.dataset.prefix;
        if (target && prefix) {
            cloneRow(target, prefix);
        }
    });

    document.addEventListener('change', function (e) {
        if (e.target.type === 'checkbox' && e.target.name && e.target.name.indexOf('-DELETE') !== -1) {
            const row = e.target.closest('.formset-row');
            if (row) {
                row.classList.toggle('deleted', e.target.checked);
            }
        }
    });
})();
