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
                container.html(`<div class="border border-dark rounded p-3 mt-2 mb-2">${response.html}</div>`);
            }
        });
        $(this).prop('disabled', true);
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
                container.html(`<div class="border border-dark rounded p-3 mt-2 mb-2">${response.html}</div>`);
                $(this).hide();
            },
            error: function(xhr) {
                container.html('<div class="text-danger">Erreur lors de l’envoi du formulaire.</div>');
                $(this).show();
            }
        });
    });
});
function updateRating(value) {
    // Mise à jour de la valeur cachée lorsque l'utilisateur clique sur une étoile
    document.getElementById('rating-value').value = value;
}