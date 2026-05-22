document.addEventListener("DOMContentLoaded", () => {
    const ctx = document.getElementById('chart').getContext('2d');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Inicio', 'Validación', 'Build', 'Deploy', 'Running'],
            datasets: [{
                label: 'Ciclo de vida del microservicio',
                data: [10, 30, 50, 70, 100],
                borderColor: 'white',
                borderWidth: 3,
                fill: false,
                tension: 0.3
            }]
        },
        options: {
            plugins: {
                legend: { labels: { color: 'white' } }
            },
            scales: {
                x: { ticks: { color: 'white' } },
                y: { ticks: { color: 'white' } }
            }
        }
    });
});
