document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenuContainer = document.getElementById('mobile-menu-container');
    const iconMenu = document.getElementById('icon-menu');
    const iconClose = document.getElementById('icon-close');

    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', () => {
            const isExpanded = mobileMenuButton.getAttribute('aria-expanded') === 'true' || false;
            mobileMenuButton.setAttribute('aria-expanded', String(!isExpanded));
            if (mobileMenuContainer) mobileMenuContainer.classList.toggle('hidden');
            if (iconMenu) iconMenu.classList.toggle('hidden');
            if (iconClose) iconClose.classList.toggle('hidden');
        });
    }
});
