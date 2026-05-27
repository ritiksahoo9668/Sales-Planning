/**
 * Vendor profile: sub-category filter + in-portal master create (type, category, sub-category).
 */
(function () {
    function getCsrfToken() {
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        return input ? input.value : '';
    }

    function addSelectOption(select, id, name, selectIt) {
        if (!select) return;
        let opt = Array.from(select.options).find(function (o) {
            return o.value === String(id);
        });
        if (!opt) {
            opt = document.createElement('option');
            opt.value = id;
            opt.textContent = name;
            select.appendChild(opt);
        } else {
            opt.textContent = name;
        }
        if (selectIt) {
            select.value = String(id);
        }
    }

    function initVendorForm() {
        const root = document.querySelector('.vendor-profile-form');
        const categorySelect = document.getElementById('id_vendor_category');
        const subSelect = document.getElementById('id_vendor_sub_category');
        const typeSelect = document.getElementById('id_vendor_type');
        const dataEl = document.getElementById('vendor-subcategories-data');
        const isSuperadmin = root.dataset.isSuperadmin === '1';
        const confirmModalEl = document.getElementById('vendorConfirmModal');
        const confirmModalBody = document.getElementById('vendorConfirmModalBody');
        const confirmModalOk = document.getElementById('vendorConfirmModalOk');
        const messageModalEl = document.getElementById('vendorMessageModal');
        const messageModalBody = document.getElementById('vendorMessageModalBody');

        if (!root || !categorySelect || !subSelect || !dataEl) {
            return;
        }

        let allSubs = [];
        try {
            allSubs = JSON.parse(dataEl.textContent);
        } catch (e) {
            allSubs = [];
        }

        const emptySubLabel = '— Select vendor sub category —';

        function rebuildSubOptions(categoryId, preserveValue) {
            const filtered = categoryId
                ? allSubs.filter(function (s) {
                    return String(s.category_id) === String(categoryId);
                })
                : [];

            const prev = preserveValue ? subSelect.value : '';
            subSelect.innerHTML = '';
            const emptyOpt = document.createElement('option');
            emptyOpt.value = '';
            emptyOpt.textContent = emptySubLabel;
            subSelect.appendChild(emptyOpt);

            filtered.forEach(function (s) {
                const opt = document.createElement('option');
                opt.value = s.id;
                opt.textContent = s.name;
                subSelect.appendChild(opt);
            });

            if (preserveValue && prev) {
                const ok = filtered.some(function (s) {
                    return String(s.id) === String(prev);
                });
                if (ok) subSelect.value = prev;
            }

            subSelect.disabled = !categoryId;
        }

        categorySelect.addEventListener('change', function () {
            rebuildSubOptions(categorySelect.value, false);
        });
        rebuildSubOptions(categorySelect.value, true);

        function showError(panel, msg) {
            const err = panel.querySelector('.vendor-master-error');
            if (err) {
                err.textContent = msg;
                err.classList.remove('d-none');
            }
        }

        function clearError(panel) {
            const err = panel.querySelector('.vendor-master-error');
            if (err) {
                err.textContent = '';
                err.classList.add('d-none');
            }
        }

        async function postMaster(url, body) {
            const fd = new FormData();
            Object.keys(body).forEach(function (k) {
                fd.append(k, body[k]);
            });
            const resp = await fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCsrfToken() },
                body: fd,
                credentials: 'same-origin',
            });
            const data = await resp.json();
            if (!resp.ok || !data.ok) {
                throw new Error(data.error || 'Could not save.');
            }
            return data;
        }

        function showMessageModal(message) {
            if (!messageModalEl || !messageModalBody || !window.bootstrap) {
                return;
            }
            messageModalBody.textContent = message;
            const modal = bootstrap.Modal.getOrCreateInstance(messageModalEl);
            modal.show();
        }

        function showConfirmModal(message) {
            return new Promise(function (resolve) {
                if (!confirmModalEl || !confirmModalBody || !confirmModalOk || !window.bootstrap) {
                    resolve(false);
                    return;
                }

                confirmModalBody.textContent = message;
                const modal = bootstrap.Modal.getOrCreateInstance(confirmModalEl);
                let settled = false;
                const onConfirm = function () {
                    if (settled) return;
                    settled = true;
                    confirmModalOk.removeEventListener('click', onConfirm);
                    resolve(true);
                    modal.hide();
                };
                const onHide = function () {
                    if (settled) return;
                    settled = true;
                    confirmModalEl.removeEventListener('hidden.bs.modal', onHide);
                    confirmModalOk.removeEventListener('click', onConfirm);
                    resolve(false);
                };

                confirmModalOk.addEventListener('click', onConfirm);
                confirmModalEl.addEventListener('hidden.bs.modal', onHide);
                modal.show();
            });
        }

        if (isSuperadmin) {
            document.querySelectorAll('.vendor-master-toggle').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    const target = document.querySelector(btn.dataset.target);
                    if (target) {
                        bootstrap.Collapse.getOrCreateInstance(target).toggle();
                    }
                });
            });

            document.querySelectorAll('.vendor-master-cancel').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    const target = document.querySelector(btn.dataset.target);
                    if (!target) return;
                    const input = target.querySelector('.vendor-master-name');
                    const err = target.querySelector('.vendor-master-error');
                    if (input) input.value = '';
                    if (err) {
                        err.textContent = '';
                        err.classList.add('d-none');
                    }
                    bootstrap.Collapse.getOrCreateInstance(target).hide();
                });
            });

            document.querySelectorAll('.vendor-master-save').forEach(function (btn) {
                btn.addEventListener('click', async function () {
                    const panel = btn.closest('.collapse');
                    const input = panel.querySelector('.vendor-master-name');
                    const name = (input.value || '').trim();
                    clearError(panel);
                    if (!name) {
                        showError(panel, 'Enter a name.');
                        return;
                    }

                    const kind = btn.dataset.master;
                    btn.disabled = true;
                    try {
                        if (kind === 'type') {
                            const data = await postMaster(root.dataset.urlType, { name: name });
                            addSelectOption(typeSelect, data.id, data.name, true);
                        } else if (kind === 'category') {
                            const data = await postMaster(root.dataset.urlCategory, { name: name });
                            addSelectOption(categorySelect, data.id, data.name, true);
                            categorySelect.dispatchEvent(new Event('change'));
                        } else if (kind === 'subcategory') {
                            const catId = categorySelect.value;
                            if (!catId) {
                                showError(panel, 'Select a vendor category first.');
                                return;
                            }
                            const data = await postMaster(root.dataset.urlSubcategory, {
                                name: name,
                                category_id: catId,
                            });
                            allSubs.push({
                                id: data.id,
                                name: data.name,
                                category_id: data.category_id,
                            });
                            rebuildSubOptions(catId, false);
                            subSelect.value = String(data.id);
                        }
                        input.value = '';
                        bootstrap.Collapse.getOrCreateInstance(panel, { toggle: false }).hide();
                    } catch (e) {
                        showError(panel, e.message);
                    } finally {
                        btn.disabled = false;
                    }
                });
            });

            document.querySelectorAll('.vendor-master-delete').forEach(function (btn) {
                btn.addEventListener('click', async function () {
                    const kind = btn.dataset.master;
                    let selectedId = '';
                    let url = '';
                    let selectedName = '';

                    if (kind === 'type') {
                        selectedId = typeSelect.value;
                        selectedName = typeSelect.options[typeSelect.selectedIndex]?.text || '';
                        url = root.dataset.urlTypeDelete;
                    } else if (kind === 'category') {
                        selectedId = categorySelect.value;
                        selectedName = categorySelect.options[categorySelect.selectedIndex]?.text || '';
                        url = root.dataset.urlCategoryDelete;
                    } else if (kind === 'subcategory') {
                        selectedId = subSelect.value;
                        selectedName = subSelect.options[subSelect.selectedIndex]?.text || '';
                        url = root.dataset.urlSubcategoryDelete;
                    }

                    if (!selectedId) {
                        showMessageModal('Please select a value to delete.');
                        return;
                    }
                    const confirmed = await showConfirmModal('Delete "' + selectedName + '"?');
                    if (!confirmed) {
                        return;
                    }

                    btn.disabled = true;
                    try {
                        await postMaster(url, { id: selectedId });
                        if (kind === 'type') {
                            typeSelect.querySelector('option[value="' + selectedId + '"]')?.remove();
                            typeSelect.value = '';
                        } else if (kind === 'category') {
                            categorySelect.querySelector('option[value="' + selectedId + '"]')?.remove();
                            allSubs = allSubs.filter(function (s) {
                                return String(s.category_id) !== String(selectedId);
                            });
                            categorySelect.value = '';
                            rebuildSubOptions('', false);
                        } else if (kind === 'subcategory') {
                            allSubs = allSubs.filter(function (s) {
                                return String(s.id) !== String(selectedId);
                            });
                            rebuildSubOptions(categorySelect.value, false);
                        }
                    } catch (e) {
                        showMessageModal(e.message || 'Delete failed.');
                    } finally {
                        btn.disabled = false;
                    }
                });
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVendorForm);
    } else {
        initVendorForm();
    }
})();
