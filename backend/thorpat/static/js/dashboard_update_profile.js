// src/static/js/dashboard_update_profile.js
document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'update-profile-form-container' &&
        event.detail.xhr.status >= 200 && event.detail.xhr.status < 300) { // Check for successful swap

        const triggeredEvents = JSON.parse(event.detail.xhr.getResponseHeader('HX-Trigger') || '{}');
        if (triggeredEvents && triggeredEvents.showMessage) {
            // Replace with a more sophisticated notification system if available
            alert(triggeredEvents.showMessage.message);
        }
    }
});
