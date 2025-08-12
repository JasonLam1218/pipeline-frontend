// static/js/list.js
$(document).ready(function() {
    // jsTree init with checkbox for multi-select, disabling three_state to prevent parent propagation
    $('#tree').jstree({
        'core': {
            'data': {
                'url': '/get_blobs/',
                'data': function(node) {
                    return { 'prefix': node.id === '#' ? '' : node.id };
                }
            }
        },
        'checkbox': {
            'three_state': false,  // Disable partial checks on parents
            'cascade': ''  // No cascading selection up/down
        },
        'plugins': ['checkbox', 'types'],
        'types': {
            'dir': { 'icon': 'jstree-folder' },
            'file': { 'icon': 'jstree-file' }
        }
    });

    // Enable/disable download button based on selection (enable for 1+ files)
    $('#tree').on('changed.jstree', function(e, data) {
        let selected = data.selected;  // Array of IDs (strings)
        // Filter out any directories
        selected = selected.filter(id => !id.endsWith('/'));
        const downloadBtn = $('#downloadBtn');
        // Enable download if at least one file is selected
        if (selected.length >= 1) {
            downloadBtn.prop('disabled', false);
        } else {
            downloadBtn.prop('disabled', true);
        }
    });

    // Generate button handler
    $('#generateBtn').on('click', function() {
        let selected = $('#tree').jstree(true).get_selected();  // Array of IDs (strings)
        // For generate, allow dirs but limit total selections to 10
        if (selected.length > 10) {
            alert('You can select a maximum of 10 items for generation.');
            return;
        }
        if (selected.length === 0) {
            alert('No paths selected');
            return;
        }
        // Disable Generate button to prevent multiple tasks
        $('#generateBtn').prop('disabled', true);
        $.post('/generate/', JSON.stringify({paths: selected}), function(response) {
            if (response.task_id) {
                onGenerateSuccess(response.task_id);  // From progress.js
            }
        }).fail(function() {
            // Re-enable on failure
            $('#generateBtn').prop('disabled', false);
        });
    });

    // Download button handler (now supports multiple files via ZIP)
    $('#downloadBtn').on('click', async function() {
        let selected = $('#tree').jstree(true).get_selected();  
        selected = selected.filter(id => !id.endsWith('/'));
        if (selected.length < 1) return;  // Safety check
        try {
            const response = await fetch('/download-file/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({filenames: selected})  // Send array of filenames
            });
            if (!response.ok) {
                throw new Error('Download failed with status: ' + response.status);
            }
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = selected.length === 1 ? selected[0].split('/').pop() : 'files.zip';  // ZIP for multi, original name for single
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            // Reset: Disable button after download
            $('#downloadBtn').prop('disabled', true);
        } catch (error) {
            console.error('Download error:', error);
        }
    });
});

// Expose onGenerateSuccess if not in progress.js, or include it here if preferred
function onGenerateSuccess(taskId) {
    updateState({isActive: true, taskId: taskId});
    $('#globalProgress').removeClass('d-none');
    startPolling(taskId);
    $('#cancelBtn').on('click', function() { cancelTask(taskId); });
    // Re-enable Generate button only after task completion/cancel (handle in status polling)
}