from django.contrib.contenttypes.models import ContentType
from RH.models import RH
from notification.models import Notification


def notifier_tous_les_rh(type_notif, titre, message, lien=''):
  
    rhs = RH.objects.filter(is_active=True)
    content_type = ContentType.objects.get_for_model(RH)
    
    notifications_creees = []
    for rh in rhs:
        notif = Notification.objects.create(
            content_type=content_type,
            object_id=rh.pk,
            type_notif=type_notif,
            titre=titre,
            message=message,
            lien=lien,
        )
        notifications_creees.append(notif)
    
    return notifications_creees


def notifier_rh_sur_contrat_expiration(contrat):
    """
    Notifie tous les RH qu'un contrat arrive à expiration.
    """
    from datetime import date
    
    aujourdhui = date.today()
    jours_restants = (contrat.date_fin - aujourdhui).days if contrat.date_fin else None
    
    if jours_restants is None:
        return []
    
    if jours_restants < 0:
        # Contrat déjà expiré
        titre = f"🚨 Contrat EXPIRÉ - {contrat.employe.nom} {contrat.employe.prenom}"
        message = (
            f"Le contrat de {contrat.employe.nom} {contrat.employe.prenom} "
            f"(poste: {contrat.poste.intitule}, type: {contrat.type_contrat}) "
            f"a expiré le {contrat.date_fin.strftime('%d/%m/%Y')}. "
            f"Action requise : clôturer ou renouveler ce contrat."
        )
        type_notif = Notification.TypeNotification.CONTRAT_EXPIRE
    else:
        # Contrat expirant bientôt
        titre = f"⚠️ Contrat expire dans {jours_restants} jour(s)"
        message = (
            f"Le contrat de {contrat.employe.nom} {contrat.employe.prenom} "
            f"(poste: {contrat.poste.intitule}, type: {contrat.type_contrat}) "
            f"expire le {contrat.date_fin.strftime('%d/%m/%Y')}. "
            f"Il reste {jours_restants} jour(s) avant expiration."
        )
        type_notif = Notification.TypeNotification.CONTRAT_EXPIRE_SOON
    
    lien = f"/contrats/{contrat.id}"
    
    return notifier_tous_les_rh(
        type_notif=type_notif,
        titre=titre,
        message=message,
        lien=lien,
    )