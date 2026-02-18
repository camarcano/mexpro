/**
 * Hitter leaderboard AG Grid initialization.
 */
document.addEventListener('DOMContentLoaded', function() {
    MexProGrid.init('hitterGrid', '/stats/api/hitting-leaderboard', {
        onCellClicked: function(event) {
            // Only navigate if clicking on the name column
            if (event.colDef.field === 'name') {
                const batterId = event.data.batter_id;
                const name = event.data.name;
                if (batterId) {
                    window.location.href = '/hitters/' + batterId;
                } else if (name) {
                    window.location.href = '/hitters/by-name/' + encodeURIComponent(name);
                }
            }
        },
        defaultColDef: {
            sortable: true,
            filter: true,
            resizable: true,
            minWidth: 50,
        },
    });
});
