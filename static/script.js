document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth', 
        height: 600,
        themeSystem: 'bootstrap5',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth, timeGridWeek'
        },
        events: '/get_events'
    });
    calendar.render();

    fetch('/recent_events')
        .then(response => response.json())
        .then(events => {
            const container = document.getElementById('recent-events-container');
            container.innerHTML = '';

            events.forEach(event => {
                const card = document.createElement('div');
                card.className = 'col';
                card.innerHTML = `
                    <div class="card bg-black text-white border border-warning shadow-sm h-100">
                        <div class="card-body">
                            <h5 class="card-title text-warning">${event.title}</h5>
                            <p class="card-text mb-1">Reserved: <strong>${event.venue}</strong></p>
                            <p class="card-text"><small>${new Date(event.start).toLocaleDateString(undefined, {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric'
                            })}</small></p>
                        </div>
                    </div>
                `;
                container.appendChild(card)
            });
        })
        .catch(error => console.error('Error loading recennt events:', error));
});