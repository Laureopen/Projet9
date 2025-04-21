<script>
$(document).ready(function() {
    $('.review-button').on('click', function() {
        const url = $(this).data('url');
        const ticketId = url.match(/ticket\/(\d+)\//)[1];
        const container = $('#review-form-' + ticketId);

        if (container.children().length > 0) {
            container.toggle();
            return;
        }

        $.ajax({
            url: url,
            type: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            success: function(response) {
                container.html(response.html);
            }
        });
    });

    // Soumission AJAX de review
    $(document).on('submit', '.ajax-review-form', function(e) {
        e.preventDefault();

        const form = $(this);
        const action = form.closest('[id^="review-form-"]').data('url') || form.closest('form').attr('action');
        const container = form.closest('[id^="review-form-"]');

        $.ajax({
            url: action,
            type: 'POST',
            data: form.serialize(),
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            success: function(response) {
                container.html(response.html);
            },
            error: function(xhr) {
                container.html('<div class="text-danger">Erreur lors de l’envoi du formulaire.</div>');
            }
        });
    });
});
</script>

