document.addEventListener('DOMContentLoaded', function () {
    // 1. หา element ที่จำเป็นทั้งหมด
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle');

    // 2. ฟังก์ชันหลักสำหรับจัดการ Layout
    function updateLayout() {
        if (!sidebar || !mainContent) return;

        const isMobile = window.innerWidth < 768; // 768px คือ breakpoint 'md'

        if (isMobile) {
            // --- จัดการ Layout สำหรับ Mobile ---
            sidebar.classList.add('hidden'); // ซ่อน sidebar เป็นค่าเริ่มต้น
            mainContent.style.marginLeft = '0px'; // ไม่มี margin ซ้าย
        } else {
            // --- จัดการ Layout สำหรับ Desktop ---
            sidebar.classList.remove('hidden'); // แสดง sidebar เสมอ
            const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
            
            if (isCollapsed) {
                sidebar.classList.add('sidebar-collapsed');
                sidebar.style.width = '5rem'; // w-20
                mainContent.style.marginLeft = '5rem'; // ml-20
            } else {
                sidebar.classList.remove('sidebar-collapsed');
                sidebar.style.width = '16rem'; // w-64
                mainContent.style.marginLeft = '16rem'; // ml-64
            }
        }
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            const isCurrentlyCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
            localStorage.setItem('sidebarCollapsed', !isCurrentlyCollapsed);
            updateLayout();
        });
    }

    if (mobileSidebarToggle) {
        mobileSidebarToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('hidden');
        });
    }

    updateLayout();
    window.addEventListener('resize', updateLayout);

    // --- โค้ดที่เพิ่มเข้ามาสำหรับ Action Menu Dropdown ---
    function closeAllActionMenus() {
        document.querySelectorAll('.action-menu').forEach(function(menu) {
            menu.classList.add('hidden');
        });
    }

    // Event delegation for dynamically added action menus
    document.body.addEventListener('click', function(event) {
        const button = event.target.closest('.action-menu-button');
        if (button) {
            event.stopPropagation();
            const menuId = button.dataset.menuId;
            const targetMenu = document.getElementById(menuId);
            
            const isVisible = !targetMenu.classList.contains('hidden');
            
            closeAllActionMenus(); // ปิดเมนูอื่นก่อน
            
            if (!isVisible) {
                targetMenu.classList.remove('hidden');
            }
        } else {
            // ถ้าคลิกนอกเมนู ให้ปิดเมนูทั้งหมด
            if (!event.target.closest('.action-menu')) {
                closeAllActionMenus();
            }
        }
    });
});
