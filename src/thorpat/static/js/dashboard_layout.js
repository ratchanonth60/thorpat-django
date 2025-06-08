document.addEventListener('DOMContentLoaded', function () {
    // 1. หา element ที่จำเป็นทั้งหมด
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const sidebarToggle = document.getElementById('sidebar-toggle'); // ปุ่มพับ/กาง (Desktop)
    const mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle'); // ปุ่ม Hamburger (Mobile)

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

    // 3. ผูก Event Listeners

    // ปุ่มพับ/กาง (Desktop)
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            const isCurrentlyCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
            // สลับค่าและจำไว้ใน localStorage
            localStorage.setItem('sidebarCollapsed', !isCurrentlyCollapsed);
            // อัปเดต Layout
            updateLayout();
        });
    }

    // ปุ่ม Hamburger (Mobile)
    if (mobileSidebarToggle) {
        mobileSidebarToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('hidden');
        });
    }

    // 4. เรียกใช้ฟังก์ชันตอนเริ่มต้น และเมื่อปรับขนาดจอ
    updateLayout();
    window.addEventListener('resize', updateLayout);
});
