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
        events: [
            {
                title: 'BSIT - Engr AVR',
                start: '2025-07-15'
            },
            {
                title: 'DOMT - Gym',
                start: '2025-07-16'
            },
            {
                title: 'BSEDM - DOST Lab',
                start: '2025-07-17'
            }
        ]
    });
    calendar.render();
});