/**
 * Live search / role filter for Business Partners list (no full page reload).
 */
(function () {
    const form = document.getElementById('party-filter-form');
    const searchInput = document.getElementById('party-search-input');
    const roleSelect = document.getElementById('party-role-filter');
    const statusSelect = document.getElementById('party-status-filter');
    const perPageSelect = document.getElementById('party-per-page');
    const resultsEl = document.getElementById('party-list-results');

    if (!form || !resultsEl) {
        return;
    }

    const SEARCH_DELAY_MS = 300;
    let searchTimer = null;
    let activeController = null;

    function listUrl() {
        const params = new URLSearchParams(new FormData(form));
        const base = form.getAttribute('action') || window.location.pathname;
        const qs = params.toString();
        return qs ? base + '?' + qs : base;
    }

    function fetchResults(url) {
        if (activeController) {
            activeController.abort();
        }
        activeController = new AbortController();

        resultsEl.classList.add('opacity-50');

        return fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            credentials: 'same-origin',
            signal: activeController.signal,
        })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error('Request failed');
                }
                return response.text();
            })
            .then(function (html) {
                resultsEl.innerHTML = html;
                if (window.history && window.history.replaceState) {
                    window.history.replaceState(null, '', url);
                }
            })
            .catch(function (err) {
                if (err.name !== 'AbortError') {
                    form.submit();
                }
            })
            .finally(function () {
                resultsEl.classList.remove('opacity-50');
                activeController = null;
            });
    }

    function scheduleSearch() {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(function () {
            fetchResults(listUrl());
        }, SEARCH_DELAY_MS);
    }

    if (searchInput) {
        searchInput.addEventListener('input', scheduleSearch);
    }

    function onFilterChange() {
        clearTimeout(searchTimer);
        fetchResults(listUrl());
    }

    if (roleSelect) {
        roleSelect.addEventListener('change', onFilterChange);
    }

    if (statusSelect) {
        statusSelect.addEventListener('change', onFilterChange);
    }

    if (perPageSelect) {
        perPageSelect.addEventListener('change', onFilterChange);
    }

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        clearTimeout(searchTimer);
        fetchResults(listUrl());
    });

    resultsEl.addEventListener('click', function (event) {
        const link = event.target.closest('a.page-link');
        if (!link || !resultsEl.contains(link)) {
            return;
        }
        event.preventDefault();
        const href = link.getAttribute('href');
        if (!href || href === '#') {
            return;
        }
        // Resolve against /parties/ path — origin-only breaks ?page=2 links (loads / instead).
        const url = new URL(href, window.location.origin + window.location.pathname);
        fetchResults(url.pathname + url.search);
    });
})();
