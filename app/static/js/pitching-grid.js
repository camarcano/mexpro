/**
 * Pitcher leaderboard AG Grid initialization.
 */
document.addEventListener('DOMContentLoaded', function() {
    MexProGrid.init('pitcherGrid', '/stats/api/pitching-leaderboard', {
        onRowClicked: function(event) {
            const pitcherId = event.data.pitcher_id;
            const name = event.data.name;
            if (pitcherId) {
                window.location.href = '/pitchers/' + pitcherId;
            } else if (name) {
                window.location.href = '/pitchers/by-name/' + encodeURIComponent(name);
            }
        },
        getRowStyle: function(params) {
            return { cursor: 'pointer' };
        },
    });
});
