const { app, BrowserWindow, dialog } = require('electron');
const fs = require('fs');
const path = 'AppElectronJS/cache_doi.json';


function confirmDeleteFile() {
    const response = dialog.showMessageBoxSync(mainWindow, {
        type: 'warning',
        title: 'Confirmation',
        message: 'Êtes-vous sûr de vouloir supprimer le fichier cache_doi.json ?',
        buttons: ['Annuler', 'Supprimer'],
        defaultId: 0, // "Annuler" est sélectionné par défaut
        cancelId: 0 // Si l'utilisateur ferme la fenêtre, ça annule
    });

    if (response === 1) { // Si l'utilisateur clique sur "Supprimer"
        deleteFile();
    }
}

function deleteFile() {
    if (fs.existsSync(path)) {
        fs.unlink(path, (err) => {
            if (err) {
                dialog.showErrorBox('Erreur', 'Impossible de supprimer le fichier.');
            } else {
                dialog.showMessageBoxSync(mainWindow, {
                    type: 'info',
                    title: 'Succès',
                    message: 'Le fichier a été supprimé avec succès.'
                });
            }
        });
    } else {
        dialog.showMessageBoxSync(mainWindow, {
            type: 'warning',
            title: 'Fichier introuvable',
            message: "Le fichier n'existe pas."
        });
    }
}
