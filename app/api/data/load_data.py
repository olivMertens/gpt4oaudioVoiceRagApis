def get_incidents_data():
    return [
        {
            "id": 1,
            "incident_id": "INC1001",
            "title": "Connexion impossible à mon compte",
            "description": "L'utilisateur ne parvient pas à se connecter malgré plusieurs tentatives. Vérifiez le serveur d'authentification ou réinitialisez votre mot de passe.",
            "status": "open",
            "severity": "critical",
            "faq": "FAQ: Problème de connexion - Assurez-vous que vos identifiants sont corrects et essayez de réinitialiser votre mot de passe si nécessaire.",
            "name": "Jean Leclerc"
        },
        {
            "id": 2,
            "incident_id": "INC1002",
            "title": "Problema de acceso a la cuenta",
            "description": "El usuario experimenta dificultades al iniciar sesión. Se recomienda revisar la configuración de seguridad y posibles bloqueos temporales.",
            "status": "in-progress",
            "severity": "high",
            "faq": "FAQ: Problema de acceso - Verifica tu contraseña y comprueba que tu cuenta no esté bloqueada temporalmente.",
            "name": "Carlos García"
        },
        {
            "id": 3,
            "incident_id": "INC1003",
            "title": "Erreur lors de la réinitialisation du mot de passe",
            "description": "L'email de réinitialisation du mot de passe n'est pas reçu. Vérifiez votre dossier spam et l'exactitude de votre adresse email.",
            "status": "resolved",
            "severity": "medium",
            "faq": "FAQ: Réinitialisation de mot de passe - Consultez vos spams et assurez-vous que votre adresse email est bien enregistrée.",
            "name": "Élodie Dupont"
        },
        {
            "id": 4,
            "incident_id": "INC1004",
            "title": "Fallo en el pago en línea",
            "description": "El usuario informa que la transacción fue rechazada sin motivo aparente. Revisar los datos de pago y la conexión con el banco es recomendable.",
            "status": "open",
            "severity": "critical",
            "faq": "FAQ: Error en el pago - Verifica los detalles de tu tarjeta y confirma que tu banco no haya bloqueado la transacción.",
            "name": "María Fernández"
        },
        {
            "id": 5,
            "incident_id": "INC1005",
            "title": "Problème de synchronisation des notifications",
            "description": "Les notifications arrivent avec du retard, ce qui affecte la réactivité des utilisateurs. Vérifiez la connexion internet et la configuration de l'application.",
            "status": "investigating",
            "severity": "low",
            "faq": "FAQ: Retard de notifications - Assurez-vous d'une bonne connexion et mettez à jour l'application pour une synchronisation optimale.",
            "name": "Lucie Martin"
        },
        {
            "id": 6,
            "incident_id": "INC1006",
            "title": "Fehler bei der Aktualisierung des Benutzerprofils",
            "description": "Der Benutzer meldet, dass die aktualisierten Kontodaten nicht gespeichert werden. Überprüfen Sie die Serververbindung und stellen Sie sicher, dass alle erforderlichen Felder korrekt ausgefüllt sind.",
            "status": "open",
            "severity": "critical",
            "faq": "FAQ: Kontoverwaltung - Überprüfen Sie Ihre Eingaben und stellen Sie sicher, dass alle Felder korrekt ausgefüllt sind.",
            "name": "Lukas Müller"
        },
        {
            "id": 7,
            "incident_id": "INC1007",
            "title": "Two-Factor Authentication Failure",
            "description": "The user is not receiving the authentication code required to complete the login process. Verify the registered phone number and ensure the authentication service is online.",
            "status": "open",
            "severity": "high",
            "faq": "FAQ: Two-Factor Authentication - Verify your phone number and check if the authentication service is operational.",
            "name": "Oliver Smith"
        },
        {
            "id": 8,
            "incident_id": "INC1008",
            "title": "Systemaktualisierung fehlgeschlagen",
            "description": "Der Benutzer konnte das Systemupdate nicht abschließen. Prüfen Sie die Internetverbindung und stellen Sie sicher, dass genügend Speicherplatz vorhanden ist.",
            "status": "in-progress",
            "severity": "medium",
            "faq": "FAQ: Systemupdate - Stellen Sie sicher, dass Ihre Internetverbindung stabil ist und ausreichend Speicherplatz vorhanden ist.",
            "name": "Sofia Schmidt"
        },
        {
            "id": 9,
            "incident_id": "INC1009",
            "title": "Error loading profile information",
            "description": "Users report that their profile information is not loading correctly, leaving account details incomplete. Check the network connection and try refreshing the page.",
            "status": "investigating",
            "severity": "high",
            "faq": "FAQ: Profile Loading Error - Check your network connection and attempt a page refresh.",
            "name": "Charlotte Wilson"
        },
        {
            "id": 10,
            "incident_id": "INC1010",
            "title": "Dokumenten-Upload fehlgeschlagen",
            "description": "Der Benutzer berichtet, dass beim Hochladen von Dokumenten ein Fehler auftritt. Überprüfen Sie die Dateigröße und das Format, um den Upload erfolgreich abzuschließen.",
            "status": "resolved",
            "severity": "low",
            "faq": "FAQ: Dokumenten-Upload - Stellen Sie sicher, dass die Datei den Systemanforderungen bezüglich Größe und Format entspricht.",
            "name": "Maximilian Becker"
        }
    ]