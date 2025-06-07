document.addEventListener('DOMContentLoaded', function () {
    // Make sure chartTranslations is defined in the HTML template before this script is loaded
    // e.g., <script> const chartTranslations = { revenue: "{% trans 'Revenue' %}", ... }; </script>

    const revenueCtx = document.getElementById('monthlyRevenueChart')?.getContext('2d');
    if (revenueCtx && typeof chartTranslations !== 'undefined' && chartTranslations.revenue) {
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                datasets: [{
                    label: chartTranslations.revenue, // Using translated label
                    data: [1200, 1900, 3000, 5000, 2300, 3200],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.4,
                    fill: true,
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
        });
    }

    const salesCtx = document.getElementById('dailySalesChart')?.getContext('2d');
    if (salesCtx && typeof chartTranslations !== 'undefined' && chartTranslations.sales) {
        new Chart(salesCtx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: chartTranslations.sales, // Using translated label
                    data: [12, 19, 30, 50, 23, 32, 45],
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
        });
    }

    const ageCtx = document.getElementById('ageDistributionChart')?.getContext('2d');
    if (ageCtx && typeof chartTranslations !== 'undefined' && chartTranslations.customers) {
        new Chart(ageCtx, {
            type: 'bar',
            data: {
                labels: ['18-24', '25-34', '35-44', '45-54', '55+'],
                datasets: [{
                    label: chartTranslations.customers, // Using translated label
                    data: [3, 7, 10, 8, 2],
                    backgroundColor: 'rgba(153, 102, 255, 0.6)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } }, indexAxis: 'x' }
        });
    }
});
