// static/js/progress.js (updated to re-enable Generate button on completion/cancel)
let pollInterval;

function initGlobalProgress() {
    $.get('/get-state/', function(state) {
        if (state.isActive && state.taskId) {
            $('#globalProgress').removeClass('d-none');
            $('#generateBtn').prop('disabled', true);  // Disable if task is active on load
            startPolling(state.taskId);
            $('#cancelBtn').off('click').on('click', function() {
                cancelTask(state.taskId);
            });
        }
    });
}

function startPolling(taskId) {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(function() {
        $.get(`/status/${taskId}/`, function(response) {
            const progress = response.progress;
            $('#progressBar').css('width', `${progress}%`).attr('aria-valuenow', progress).text(`${progress}%`);
            if (response.status === 'done' || response.status === 'canceled') {
                clearInterval(pollInterval);
                updateState({isActive: false, taskId: null});
                $('#globalProgress').addClass('d-none');
                $('#generateBtn').prop('disabled', false);  // Re-enable Generate button
                alert('Task completed or canceled!');
            }
        });
    }, 5000);  // Poll every 5 seconds
}

function cancelTask(taskId) {
    $.post('/cancel-task/', JSON.stringify({task_id: taskId}), function() {
        clearInterval(pollInterval);
        updateState({isActive: false, taskId: null});
        $('#globalProgress').addClass('d-none');
        $('#generateBtn').prop('disabled', false);  // Re-enable on cancel
    }, 'json');
}

function updateState(data) {
    $.post('/update-state/', JSON.stringify(data), function() {
        console.log('State updated');
    }, 'json');
}