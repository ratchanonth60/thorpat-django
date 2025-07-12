function updateQuantity(button, change) {
  const form = button.closest("form");
  const quantityInput = form.querySelector('input[name="quantity"]');
  if (!quantityInput) return;

  let currentValue = parseInt(quantityInput.value, 10);
  let newValue = currentValue + change;

  // Ensure quantity is at least 1
  if (newValue < 1) {
    newValue = 1;
  }

  // Only update if value actually changes to avoid unnecessary requests
  if (newValue !== currentValue) {
    quantityInput.value = newValue;
    // Trigger HTMX request on the form to update the line item
    htmx.trigger(form, "submit");
  }
}
