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
                title: 'MS - Engr AVR',
                start: '2025-07-15'
            },
            {
                title: 'PASOA - Gym',
                start: '2025-07-16'
            },
            {
                title: 'CS - DOST Lab',
                start: '2025-07-17'
            }
        ]
    });
    calendar.render();
});