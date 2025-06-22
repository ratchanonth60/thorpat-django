/**
 * ฟังก์ชันสำหรับสร้าง Area Chart (กราฟพื้นที่) ด้วย ApexCharts
 * @param {HTMLElement} chartElement - The div element to render the chart in.
 * @param {string[]} labels - The labels for the x-axis.
 * @param {number[]} data - The data points for the series.
 */
function createAreaChart(chartElement, labels, data) {
    const options = {
        chart: {
            height: 350,
            type: 'area',
            toolbar: {
                show: false,
            },
        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            curve: 'smooth'
        },
        series: [{
            name: 'Total Sales',
            data: data
        }],
        xaxis: {
            type: 'category',
            categories: labels,
        },
        fill: {
            type: 'gradient',
            gradient: {
                shadeIntensity: 1,
                opacityFrom: 0.7,
                opacityTo: 0.9,
                stops: [0, 90, 100]
            }
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return "$ " + val.toFixed(2)
                }
            }
        },
        theme: {
            mode: document.documentElement.classList.contains('dark') ? 'dark' : 'light'
        }
    };

    const chart = new ApexCharts(chartElement, options);
    chart.render();
}

/**
 * ฟังก์ชันสำหรับสร้าง Doughnut Chart (กราฟโดนัท) ด้วย ApexCharts
 * @param {HTMLElement} chartElement - The div element to render the chart in.
 * @param {string[]} labels - The labels for each slice.
 * @param {number[]} data - The data for each slice.
 */
function createDoughnutChart(chartElement, labels, data) {
    const options = {
        series: data,
        chart: {
            type: 'donut',
            height: 320,
        },
        labels: labels,
        plotOptions: {
          pie: {
            donut: {
              labels: {
                show: true,
                total: {
                  showAlways: true,
                  show: true,
                  label: 'Total Orders',
                }
              }
            }
          }
        },
        responsive: [{
            breakpoint: 480,
            options: {
                chart: {
                    width: 250
                },
                legend: {
                    position: 'bottom'
                }
            }
        }],
        theme: {
            mode: document.documentElement.classList.contains('dark') ? 'dark' : 'light'
        }
    };

    const chart = new ApexCharts(chartElement, options);
    chart.render();
}

/**
 * ฟังก์ชันสำหรับสร้าง Pie Chart (กราฟวงกลม) ด้วย ApexCharts
 * @param {HTMLElement} chartElement - The div element to render the chart in.
 * @param {string[]} labels - The labels for each slice.
 * @param {number[]} data - The data for each slice.
 */
function createPieChart(chartElement, labels, data) {
    const options = {
        series: data,
        chart: {
            type: 'donut', // ใช้ donut เพื่อความสวยงาม
            height: 320,
        },
        labels: labels,
        responsive: [{
            breakpoint: 480,
            options: {
                chart: {
                    width: 250
                },
                legend: {
                    position: 'bottom'
                }
            }
        }],
        theme: {
            mode: document.documentElement.classList.contains('dark') ? 'dark' : 'light'
        }
    };

    const chart = new ApexCharts(chartElement, options);
    chart.render();
}

/**
 * ฟังก์ชันสำหรับค้นหาและวาดกราฟภายใน container ที่กำหนด
 * @param {HTMLElement} container - The element to search for charts within.
 */
function initializeChartsInContainer(container) {
    // Sales Chart (Area)
    const areaChartEl = container.querySelector('#bar-chart');
    if (areaChartEl) {
        const barDataElement = document.getElementById('bar-chart-data');
        if (barDataElement) {
            const chartData = JSON.parse(barDataElement.textContent);
            if (chartData && chartData.labels.length > 0) {
               createAreaChart(areaChartEl, chartData.labels, chartData.data);
            }
        }
    }

    // Order Status Chart (Doughnut)
    const doughnutChartEl = container.querySelector('#doughnut-chart');
    if (doughnutChartEl) {
        const doughnutDataElement = document.getElementById('doughnut-chart-data');
        if (doughnutDataElement) {
            const doughnutChartData = JSON.parse(doughnutDataElement.textContent);
            if (doughnutChartData && doughnutChartData.labels.length > 0) {
                createDoughnutChart(doughnutChartEl, doughnutChartData.labels, doughnutChartData.data);
            }
        }
    }

    // Products by Category Chart (Pie/Donut)
    const pieChartEl = container.querySelector('#pie-chart-categories');
    if (pieChartEl) {
        const categoryDataElement = document.getElementById('category-chart-data');
        if (categoryDataElement) {
            const categoryChartData = JSON.parse(categoryDataElement.textContent);
            if (categoryChartData && categoryChartData.labels.length > 0) {
               createPieChart(pieChartEl, categoryChartData.labels, categoryChartData.data);
            }
        }
    }
}

// เพิ่ม Event Listener ให้รอฟังสัญญาณจาก HTMX
document.body.addEventListener('htmx:afterSwap', function(event) {
    console.log("HTMX content swapped, initializing ApexCharts in:", event.detail.target);
    initializeChartsInContainer(event.detail.target);
});

