// Quand le document est chargé (prêt à l'emploi)
$(document).ready(function() {
// Gestion du clic sur le bouton "Créer une critique"
    $('.review-button').on('click', function() {
        const url = $(this).data('url'); // Récupère l'URL du formulaire à charger (via l'attribut data-url)

         // Extrait l'ID du ticket à partir de l'URL grâce à une expression régulière
        const ticketId = url.match(/ticket\/(\d+)\//)[1];

         // Sélectionne le conteneur HTML correspondant à ce ticket (où insérer le formulaire)
        const container = $('#review-form-' + ticketId);

        // Si le formulaire est déjà chargé (contenu non vide), on le montre ou le cache en cliquant à nouveau
        if (container.children().length > 0) {
            container.toggle();
            return;
        }

        // Sinon, envoie une requête AJAX GET pour charger le formulaire depuis le serveur
        $.ajax({
            url: url, // URL du formulaire
            type: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest'}, // Indique que c'est une requête AJAX
            success: function(response) {
            // Injecte le formulaire reçu dans le conteneur, entouré d'un cadre visuel
                container.html(`<div class="border border-dark rounded p-3 mt-2 mb-2">${response.html}</div>`);
            }
        });
        // Désactive le bouton après le clic pour éviter des clics multiples
        $(this).prop('disabled', true);
    });
    // Gestion de l'envoi AJAX du formulaire de critique
    $(document).on('submit', '.ajax-review-form', function(e) {
        e.preventDefault();// Empêche le rechargement de la page lors de la soumission classique du formulaire

        const form = $(this);// Sélectionne le formulaire soumis

        // Détermine l'URL d'action du formulaire
        // Soit depuis l'attribut data-url du conteneur parent, soit depuis l'attribut action du formulaire
        const action = form.closest('[id^="review-form-"]').data('url') || form.closest('form').attr('action');
        // Trouve le conteneur du formulaire pour y afficher la réponse
        const container = form.closest('[id^="review-form-"]');

         // Envoie la requête AJAX POST avec les données du formulaire
        $.ajax({
            url: action, // URL d'action du formulaire
            type: 'POST',
            data: form.serialize(), // Sérialise le formulaire (convertit en chaîne URL-encoded)
            headers: {'X-Requested-With': 'XMLHttpRequest'}, // Indique une requête AJAX
            success: function(response) {

            // Remplace le formulaire par la réponse du serveur (souvent un affichage mis à jour)
                container.html(`<div class="border border-dark rounded p-3 mt-2 mb-2">${response.html}</div>`);
                $(this).hide();
            },
            error: function(xhr) {

            // Affiche un message d'erreur si la soumission échoue
                container.html('<div class="text-danger">Erreur lors de l’envoi du formulaire.</div>');
                $(this).show();
            }
        });
    });
});
// Fonction qui met à jour la note sélectionnée lorsque l'utilisateur clique sur une étoile
function updateRating(value) {
    // Remplit le champ caché 'rating-value' avec la note choisie (1 à 5)
    document.getElementById('rating-value').value = value;
}