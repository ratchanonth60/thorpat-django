document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle');
    const userMenuButton = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');

    if (mobileSidebarToggle && sidebar) {
        mobileSidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('hidden');
        });
    }

    if (userMenuButton && userMenu) {
        userMenuButton.addEventListener('click', (event) => {
            event.stopPropagation();
            const isExpanded = userMenuButton.getAttribute('aria-expanded') === 'true';
            userMenuButton.setAttribute('aria-expanded', String(!isExpanded));
            userMenu.classList.toggle('hidden');
        });

        document.addEventListener('click', function(event) {
            if (userMenu && !userMenu.classList.contains('hidden') && !userMenuButton.contains(event.target) && !userMenu.contains(event.target)) {
                userMenu.classList.add('hidden');
                userMenuButton.setAttribute('aria-expanded', 'false');
            }
        });
    }
});
