/**
 * =========================================
 * OWNER DASHBOARD JS
 * FINAL STABLE VERSION
 * =========================================
 */

document.addEventListener('DOMContentLoaded', function () {

    // =====================================
    // REALTIME CLOCK
    // =====================================
    function initClock() {

        function updateClock() {

            const now = new Date();

            const clockEl =
                document.getElementById(
                    'owner-clock'
                );

            const dateEl =
                document.getElementById(
                    'owner-date'
                );

            if (clockEl) {

                clockEl.textContent =
                    now.toLocaleTimeString(
                        'id-ID',
                        {
                            hour12: false
                        }
                    );
            }

            if (dateEl) {

                dateEl.textContent =
                    now.toLocaleDateString(
                        'id-ID',
                        {
                            weekday: 'long',
                            day: 'numeric',
                            month: 'long',
                            year: 'numeric'
                        }
                    );
            }
        }

        updateClock();

        setInterval(
            updateClock,
            1000
        );
    }

    // =====================================
    // CARD ANIMATION
    // =====================================
    function initCardAnimation() {

        const cards =
            document.querySelectorAll(
                '.stat-card'
            );

        if (!cards.length) return;

        cards.forEach(
            (card, index) => {

                card.style.opacity = '0';

                card.style.transform =
                    'translateY(20px)';

                setTimeout(() => {

                    card.style.transition =
                        'all .45s ease';

                    card.style.opacity = '1';

                    card.style.transform =
                        'translateY(0)';

                }, index * 80);
            }
        );
    }

    // =====================================
    // SAFE PARSE CHART DATA
    // =====================================
    function getChartData() {

        const chartDataEl =
            document.getElementById(
                'chart-data'
            );

        if (!chartDataEl) {

            console.warn(
                '[OWNER JS] chart-data not found'
            );

            return null;
        }

        try {

            return JSON.parse(
                chartDataEl.textContent
            );

        } catch (error) {

            console.error(
                '[OWNER JS] JSON parse failed',
                error
            );

            return null;
        }
    }

    // =====================================
    // REVENUE CHART
    // =====================================
    function initRevenueChart(data) {

        const canvas =
            document.getElementById(
                'revenueChart'
            );

        if (!canvas) return;

        const labels =
            Array.isArray(data.labels)
                ? data.labels
                : [];

        const safeValues =
            Array.isArray(data.values)
                ? data.values.map(
                    value => Number(value || 0)
                )
                : [];

        const maxValue =
            Math.max(
                ...safeValues,
                1000
            );

        const ctx =
            canvas.getContext('2d');

        const gradient =
            ctx.createLinearGradient(
                0,
                0,
                0,
                320
            );

        gradient.addColorStop(
            0,
            'rgba(255,255,255,0.35)'
        );

        gradient.addColorStop(
            1,
            'rgba(255,255,255,0.02)'
        );

        if (
            window.revenueChartInstance
        ) {

            window.revenueChartInstance.destroy();
        }

        window.revenueChartInstance =
            new Chart(ctx, {

                type: 'line',

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label: 'Omzet',

                            data: safeValues,

                            borderColor:
                                '#ffffff',

                            backgroundColor:
                                gradient,

                            borderWidth: 3,

                            fill: true,

                            tension: 0.45,

                            cubicInterpolationMode:
                                'monotone',

                            spanGaps: true,

                            pointRadius: 4,

                            pointHoverRadius: 7,

                            pointBackgroundColor:
                                '#ffffff',

                            pointBorderColor:
                                'rgba(255,255,255,0.5)',

                            pointBorderWidth: 2
                        }
                    ]
                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    layout: {

                        padding: {

                            top: 10,

                            right: 15,

                            bottom: 10,

                            left: 10
                        }
                    },

                    animation: {

                        duration: 900,

                        easing:
                            'easeInOutQuart'
                    },

                    plugins: {

                        legend: {

                            display: true,

                            position: 'top',

                            labels: {

                                color:
                                    '#ffffff',

                                usePointStyle: true,

                                pointStyle: 'circle',

                                padding: 10
                            }
                        },

                        tooltip: {

                            backgroundColor:
                                '#1e293b',

                            titleColor:
                                '#ffffff',

                            bodyColor:
                                '#ffffff',

                            cornerRadius: 12,

                            padding: 14,

                            displayColors: false,

                            callbacks: {

                                label:
                                    function (context) {

                                        return (
                                            'Rp ' +
                                            Number(
                                                context.parsed.y
                                            ).toLocaleString(
                                                'id-ID'
                                            )
                                        );
                                    }
                            }
                        }
                    },

                    scales: {

                        x: {

                            grid: {

                                display: false
                            },

                            ticks: {

                                color:
                                    'rgba(255,255,255,0.82)',

                                maxRotation: 0,

                                minRotation: 0
                            },

                            border: {

                                display: false
                            }
                        },

                        y: {

                            beginAtZero: true,

                            suggestedMax:
                                maxValue * 1.2,

                            grid: {

                                color:
                                    'rgba(255,255,255,0.08)'
                            },

                            ticks: {

                                color:
                                    'rgba(255,255,255,0.72)',

                                callback:
                                    function (value) {

                                        return (
                                            'Rp ' +
                                            Number(value)
                                                .toLocaleString(
                                                    'id-ID'
                                                )
                                        );
                                    }
                            },

                            border: {

                                display: false
                            }
                        }
                    }
                }
            });
    }

// =====================================
// PARETO CHART - OPTIMIZED VERSION
// =====================================
function initParetoChart(data) {
    const canvas = document.getElementById('paretoChart');
    if (!canvas) return;

    const pareto = Array.isArray(data.pareto) ? data.pareto : [];

    // 1. Persiapan Label (Truncation lebih agresif agar tidak penuh)
    const labels = pareto.map(item => {
        const name = item.name || '';
        return name.length > 8 ? name.substring(0, 8) + '..' : name;
    });

    // 2. Persiapan Data & Kalkulasi Kumulatif
    // Rumus: $$Cumulative\% = \frac{\sum Revenue_i}{Total Revenue} \times 100$$
    const values = pareto.map(item => Number(item.revenue || 0));
    const totalRevenue = values.reduce((sum, value) => sum + value, 0);

    let cumulative = 0;
    const cumulativePercentages = values.map(value => {
        cumulative += value;
        return totalRevenue > 0 ? (cumulative / totalRevenue) * 100 : 0;
    });

    const maxValue = Math.max(...values, 1000);

    // 3. Konfigurasi Visual (Gradient)
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 340);
    gradient.addColorStop(0, 'rgba(255,255,255,0.92)');
    gradient.addColorStop(1, 'rgba(255,255,255,0.25)');

    if (window.paretoChartInstance) {
        window.paretoChartInstance.destroy();
    }

    // 4. Inisialisasi Chart.js
    window.paretoChartInstance = new Chart(ctx, {
        data: {
            labels: labels,
            datasets: [
                {
                    type: 'bar',
                    label: 'Revenue Produk',
                    data: values,
                    backgroundColor: gradient,
                    borderRadius: 12,
                    borderSkipped: false,
                    barThickness: 34,
                    maxBarThickness: 40,
                    categoryPercentage: 0.7,
                    barPercentage: 0.8,
                    yAxisID: 'y',
                    // Ikon kotak untuk bar di legend
                    pointStyle: 'rectRounded' 
                },
                {
                    type: 'line',
                    label: 'Kumulatif %',
                    data: cumulativePercentages,
                    borderColor: '#ffffff',
                    backgroundColor: '#ffffff',
                    borderWidth: 3,
                    tension: 0.38,
                    fill: false,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    yAxisID: 'y1',
                    // Ikon lingkaran untuk line di legend
                    pointStyle: 'circle'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            layout: {
                // Tambah padding bawah agar label miring tidak terpotong
                padding: { top: 0, right: 25, bottom: 25, left: 10 }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#ffffff',
                        usePointStyle: true, // Mengambil pointStyle dari tiap dataset
                        padding: 12,
                        font: { size: 12, weight: '600' }
                    }
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    padding: 14,
                    cornerRadius: 12,
                    callbacks: {
                        title: (context) => pareto[context[0].dataIndex]?.name || '',
                        label: (context) => {
                            if (context.dataset.type === 'line') {
                                return `Kumulatif: ${Number(context.parsed.y).toFixed(1)}%`;
                            }
                            return `Revenue: Rp ${Number(context.parsed.y).toLocaleString('id-ID')}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    offset: true,
                    grid: { display: false },
                    ticks: {
                        color: 'rgba(255,255,255,0.82)',
                        font: { size: 9 },
                        autoSkip: true,      // Menghindari tumpang tindih otomatis
                        maxTicksLimit: 12,   // Membatasi jumlah label yang muncul
                        maxRotation: 45,     // Rotasi label agar tidak tabrakan
                        minRotation: 45,
                        padding: 10
                    },
                    border: { display: false }
                },
                y: {
                    beginAtZero: true,
                    suggestedMax: maxValue * 1.15,
                    grid: { color: 'rgba(255,255,255,0.08)' },
                    ticks: {
                        color: 'rgba(255,255,255,0.72)',
                        callback: (value) => 'Rp ' + value.toLocaleString('id-ID')
                    },
                    border: { display: false }
                },
                y1: {
                    position: 'right',
                    min: 0,
                    max: 120,
                    grid: { drawOnChartArea: false },
                    ticks: {
                        stepSize: 20,
                        color: '#ffffff',
                        callback: (value) => value + '%'
                    },
                    border: { display: false }
                }
            }
        }
    });
}
    // =====================================
    // DSS PROGRESS
    // =====================================
    function initDssProgress() {

        const bars =
            document.querySelectorAll(
                '.dss-progress'
            );

        if (!bars.length) return;

        bars.forEach(bar => {

            const target =
                bar.dataset.width || '0%';

            bar.style.width = '0%';

            setTimeout(() => {

                bar.style.width =
                    target;

            }, 300);
        });
    }

    // =====================================
    // SIDEBAR MOBILE
    // =====================================
    function initSidebar() {

        const sidebar =
            document.getElementById(
                'sidebarWrapper'
            );

        const overlay =
            document.getElementById(
                'sidebarOverlay'
            );

        const toggleBtn =
            document.getElementById(
                'sidebarToggle'
            );

        if (
            !sidebar ||
            !overlay ||
            !toggleBtn
        ) return;

        toggleBtn.addEventListener(
            'click',
            function () {

                sidebar.classList.toggle(
                    'active'
                );

                overlay.classList.toggle(
                    'active'
                );
            }
        );

        overlay.addEventListener(
            'click',
            function () {

                sidebar.classList.remove(
                    'active'
                );

                overlay.classList.remove(
                    'active'
                );
            }
        );
    }

    // =====================================
    // TOOLTIP
    // =====================================
    function initTooltips() {

        const tooltipTriggerList =
            [].slice.call(
                document.querySelectorAll(
                    '[data-bs-toggle="tooltip"]'
                )
            );

        tooltipTriggerList.map(
            function (tooltipTriggerEl) {

                return new bootstrap.Tooltip(
                    tooltipTriggerEl
                );
            }
        );
    }
    // =====================================
// INVENTORY MODAL HANDLERS
// =====================================
function initModalHandlers() {

    const addProductModalEl =
        document.getElementById(
            'addProductModal'
        );

    const restockModalEl =
        document.getElementById(
            'restockModal'
        );

    const adjustModalEl =
        document.getElementById(
            'adjustModal'
        );

    if (
        addProductModalEl
    ) {

        window.addProductModal =
            new bootstrap.Modal(
                addProductModalEl
            );
    }

    if (
        restockModalEl
    ) {

        window.restockModal =
            new bootstrap.Modal(
                restockModalEl
            );
    }

    if (
        adjustModalEl
    ) {

        window.adjustModal =
            new bootstrap.Modal(
                adjustModalEl
            );
    }
}

    // =====================================
    // INVENTORY BUTTONS
    // =====================================
    function bindInventoryButtons() {

        document.addEventListener(
            'click',
            function(event) {

                const addBtn =
                    event.target.closest(
                        '.btn-add-product'
                    );

                if (addBtn) {

                    event.preventDefault();

                    if (
                        window.addProductModal
                    ) {

                        window.addProductModal.show();
                    }

                    return;
                }

                const restockBtn =
                    event.target.closest(
                        '.btn-restock'
                    );

                if (restockBtn) {

                    event.preventDefault();

                    const productId =
                        restockBtn.dataset.id;
                    const productInput =
                        document.getElementById(
                         'restockProductId'
                        );

                    const productNameInput =
                        document.getElementById(
                            'restockProductName'
                        );

                    if (productInput) {

                        productInput.value =
                            productId || '';
                    }

                    if (productNameInput) {

                        productNameInput.value =
                            restockBtn.dataset.name || '';
                    }

                    if (
                        window.restockModal
                    ) {

                        window.restockModal.show();
                    }

                    return;
                }

                const adjustBtn =
                    event.target.closest(
                        '.btn-adjust'
                    );

                if (adjustBtn) {

                    event.preventDefault();

                    const productId =
                        adjustBtn.dataset.id;

                    const adjustInput =
                        document.getElementById(
                            'adjustProductId'
                        );

                    const adjustNameInput =
                        document.getElementById(
                            'adjustProductName'
                        );

                    if (adjustInput) {

                        adjustInput.value =
                            productId || '';
                    }

                    if (adjustNameInput) {

                        adjustNameInput.value =
                            adjustBtn.dataset.name || '';
                    }

                    if (
                        adjustInput
                    ) {

                        adjustInput.value =
                            productId || '';
                    }

                    if (
                        window.adjustModal
                    ) {

                        window.adjustModal.show();
                    }

                    return;
                }

                const deleteBtn =
                    event.target.closest(
                        '.btn-delete-product'
                    );

                if (deleteBtn) {

                    const confirmDelete =
                        confirm(
                            'Hapus produk ini?'
                        );

                    if (
                        !confirmDelete
                    ) {

                        event.preventDefault();
                    }

                    return;
                }
            }
        );
    }

    // =====================================
    // INVENTORY FORM ACTIONS
    // =====================================
    function initInventoryActions() {

        const inventoryForms =
            document.querySelectorAll(
                'form'
            );

        if (
            !inventoryForms.length
        ) return;

        inventoryForms.forEach(form => {

            form.addEventListener(
                'submit',
                function() {

                    const submitBtn =
                        form.querySelector(
                            'button[type="submit"]'
                        );

                    if (
                        submitBtn
                    ) {

                        submitBtn.disabled =
                            true;

                        submitBtn.innerHTML =
                            'Processing...';
                    }
                }
            );
        });
    }

    // =====================================
    // INIT ALL
    // =====================================
    const chartData =
        getChartData();

    initClock();

    initCardAnimation();

    initSidebar();

    initTooltips();

    initDssProgress();

    if (chartData) {

    initRevenueChart(
        chartData
    );

    initParetoChart(
        chartData
    );
}

// =====================================
// INVENTORY INIT
// =====================================
initModalHandlers();

bindInventoryButtons();

initInventoryActions();

});

// =====================================
// DSS BAR ANIMATION
// =====================================
window.addEventListener('load', () => {

    document
        .querySelectorAll('.dss-bar')
        .forEach((bar) => {

            const width =
                bar.dataset.width || 0;

            requestAnimationFrame(() => {

                bar.style.width =
                    `${width}%`;
            });
        });
});