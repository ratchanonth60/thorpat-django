// src/static/js/htmx_csrf_config.js
document.body.addEventListener('htmx:configRequest', function(evt) {
    if (evt.detail.verb === 'post' || evt.detail.verb === 'put' || evt.detail.verb === 'patch' || evt.detail.verb === 'delete') {
        let csrfToken = null;
        // Try to get CSRF token from meta tag first
        const csrfMetaTag = document.querySelector('meta[name="csrf-token"]');
        if (csrfMetaTag) {
            csrfToken = csrfMetaTag.content;
        } else {
            // Fallback to input field if meta tag not found
            const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (csrfInput) {
                csrfToken = csrfInput.value;
            }
        }

        if (csrfToken) {
            evt.detail.headers['X-CSRFToken'] = csrfToken;
        } else {
            console.warn("CSRF token not found for HTMX request. Ensure a meta tag <meta name=\"csrf-token\" content=\"{{ csrf_token }}\"> or a Django CSRF input is present.");
        }
    }
});
