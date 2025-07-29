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
                const startDate = new Date(event.start);
                const endDate = new Date(event.end);
                const optionsDate = { year: 'numeric', month: 'long', day: 'numeric' };
                const optionsTime = { hour: '2-digit', minute: '2-digit', hour12: true };

                const formattedDate = startDate.toLocaleDateString(undefined, optionsDate);
                const formattedStartTime = startDate.toLocaleTimeString(undefined, optionsTime).replace(/^0/, '');
                const formattedEndTime = endDate.toLocaleTimeString(undefined, optionsTime).replace(/^0/, '');

                card.innerHTML = `
                    <div class="card bg-black text-white border border-warning shadow-sm h-100">
                        <div class="card-body">
                            <h5 class="card-title text-warning">${event.title}</h5>
                            <p class="card-text mb-1">Reserved: <strong>${event.venue}</strong></p>
                            <p class="card-text mb-0"><small>${formattedDate}</small></p>
                            <p class="card-text"><small>${formattedStartTime} - ${formattedEndTime}</small></p>
                        </div>
                    </div>
                `;
                container.appendChild(card)
            });
        })
        .catch(error => console.error('Error loading recennt events:', error));
});