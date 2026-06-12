from datetime import date, timedelta
from django.db.models import Count, Q, Sum, Avg, F
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter

from employees.models import Employe
from presences.models import Presence
from conges.models import Conge
from justification.models import Justification

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION DU CACHE
# ═══════════════════════════════════════════════════════════════
CACHE_DASHBOARD_TIMEOUT = 300  # 5 minutes
CACHE_KEY_DASHBOARD = 'dashboard_stats_{user_id}'
CACHE_KEY_EMPLOYES = 'dashboard_employes_stats'

# Mapping manuel des statuts
STATUT_LABELS = {
    'PRESENT': 'Présent',
    'ABSENT': 'Absent',
    'RETARD': 'Retard',
    'CONGE': 'Congé',
    'JOUR_FERIE': 'Jour férié',
    'REPOS': 'Repos',
}


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Statistiques complètes du dashboard RH",
        description="Retourne les KPIs, graphiques et activités récentes (avec cache 5min)"
    )
    def get(self, request):
        # 1. VÉRIFICATION DU CACHE
        cache_key = CACHE_KEY_DASHBOARD.format(user_id=request.user.id)
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            response = Response(cached_data, status=status.HTTP_200_OK)
            response['X-Cache'] = 'HIT'
            return response

        # 2. CALCUL DES DONNÉES
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)

        # --- KPIs Employés ---
        total_employes = Employe.objects.filter(is_active=True).count()
        nouveaux_ce_mois = Employe.objects.filter(
            date_joined__month=today.month,
            date_joined__year=today.year,
            is_active=True
        ).count()

        # --- KPIs Présences Aujourd'hui ---
        presences_today = Presence.objects.filter(date=today)
        presents = presences_today.filter(statut='PRESENT').count()
        absents = presences_today.filter(statut='ABSENT').count()
        retards = presences_today.filter(statut='RETARD').count()
        taux_presence = round((presents / total_employes * 100), 1) if total_employes else 0

        # --- KPIs Semaine ---
        presences_semaine = Presence.objects.filter(date__gte=week_start, date__lte=today)
        semaine_presents = presences_semaine.filter(statut='PRESENT').count()
        semaine_absents = presences_semaine.filter(statut='ABSENT').count()
        semaine_retards = presences_semaine.filter(statut='RETARD').count()
        total_semaine = presences_semaine.count()
        taux_semaine = round((semaine_presents / total_semaine * 100), 1) if total_semaine else 0

        # --- KPIs Mois ---
        presences_mois = Presence.objects.filter(date__gte=month_start, date__lte=today)
        mois_presents = presences_mois.filter(statut='PRESENT').count()
        mois_absents = presences_mois.filter(statut='ABSENT').count()
        mois_retards = presences_mois.filter(statut='RETARD').count()
        total_mois = presences_mois.count()
        taux_mois = round((mois_presents / total_mois * 100), 1) if total_mois else 0

        # --- KPIs Année ---
        presences_annee = Presence.objects.filter(date__gte=year_start, date__lte=today)
        annee_presents = presences_annee.filter(statut='PRESENT').count()
        annee_absents = presences_annee.filter(statut='ABSENT').count()
        annee_retards = presences_annee.filter(statut='RETARD').count()
        total_annee = presences_annee.count()
        taux_annee = round((annee_presents / total_annee * 100), 1) if total_annee else 0

        # --- Graphique Semaine (Jour par jour) ---
        presences_semaine_detail = []
        for i in range(5):  # Lundi à Vendredi
            jour = week_start + timedelta(days=i)
            p_day = Presence.objects.filter(date=jour)
            presences_semaine_detail.append({
                'jour': jour.strftime('%a'),
                'date': jour.strftime('%d/%m'),
                'presents': p_day.filter(statut='PRESENT').count(),
                'absents': p_day.filter(statut='ABSENT').count(),
                'retards': p_day.filter(statut='RETARD').count(),
            })

        # --- Graphique Évolution Mensuelle (12 mois) ---
        evolution_mensuelle = []
        for i in range(12):
            mois_cible = today.month - i
            annee_cible = today.year
            while mois_cible <= 0:
                mois_cible += 12
                annee_cible -= 1
            
            debut_mois = date(annee_cible, mois_cible, 1)
            if mois_cible == 12:
                fin_mois = date(annee_cible + 1, 1, 1) - timedelta(days=1)
            else:
                fin_mois = date(annee_cible, mois_cible + 1, 1) - timedelta(days=1)
            
            p_mois = Presence.objects.filter(date__gte=debut_mois, date__lte=fin_mois)
            evolution_mensuelle.insert(0, {
                'mois': debut_mois.strftime('%b %Y'),
                'presents': p_mois.filter(statut='PRESENT').count(),
                'absents': p_mois.filter(statut='ABSENT').count(),
                'retards': p_mois.filter(statut='RETARD').count(),
            })

        # --- Répartition Statut (Camembert) --- ✅ CORRIGÉ
        repartition_statut = list(
            presences_today.values('statut')
            .annotate(total=Count('id'))
        )
        stat_counts = {item['statut']: item['total'] for item in repartition_statut}
        
        # On force la présence des 3 statuts pour éviter que le graphique ne casse
        repartition_statut_formatee = [
            {
                'label': STATUT_LABELS.get('PRESENT', 'Présent'),
                'value': stat_counts.get('PRESENT', 0),
                'statut': 'PRESENT'
            },
            {
                'label': STATUT_LABELS.get('ABSENT', 'Absent'),
                'value': stat_counts.get('ABSENT', 0),
                'statut': 'ABSENT'
            },
            {
                'label': STATUT_LABELS.get('RETARD', 'Retard'),
                'value': stat_counts.get('RETARD', 0),
                'statut': 'RETARD'
            }
        ]

        # --- KPIs Congés & Justifications ---
        conges_en_attente = Conge.objects.filter(statut='EN_ATTENTE').count()
        conges_approuves = Conge.objects.filter(statut='APPROUVE', date_debut__gte=today).count()
        conges_par_type = list(Conge.objects.values('type_conge').annotate(total=Count('id')).order_by('-total'))

        justifs_en_attente = Justification.objects.filter(statut='EN_ATTENTE').count()
        justifs_validees = Justification.objects.filter(statut='VALIDEE').count()
        justifs_rejetees = Justification.objects.filter(statut='REJETEE').count()

        # --- Activités Récentes --- ✅ CORRIGÉ (tri par vraie date)
        activites = []
        
        dernieres_presences = Presence.objects.select_related('employe').order_by('-date')[:5]
        for p in dernieres_presences:
            activites.append({
                'type': 'presence',
                'icon': 'bi-clock-history',
                'text': f"{p.employe.prenom} {p.employe.nom} - {p.get_statut_display()}",
                'time': p.date.strftime('%d/%m/%Y'),
                '_sort_key': p.date,
            })
        
        dernieres_conges = Conge.objects.select_related('employe').order_by('-date_demande')[:3]
        for c in dernieres_conges:
            activites.append({
                'type': 'conge',
                'icon': 'bi-calendar-check',
                'text': f"Congé de {c.employe.prenom} {c.employe.nom}",
                'time': c.date_demande.strftime('%d/%m/%Y'),
                '_sort_key': c.date_demande,
            })

        # Tri par date réelle
        activites = sorted(activites, key=lambda x: x['_sort_key'], reverse=True)[:8]
        
        # Suppression de la clé de tri avant envoi
        for a in activites:
            del a['_sort_key']

        # 3. CONSTRUCTION DE LA RÉPONSE
        response_data = {
            'kpis': {
                'total_employes': total_employes,
                'nouveaux_ce_mois': nouveaux_ce_mois,
                'presents_aujourdhui': presents,
                'absents_aujourdhui': absents,
                'retards_aujourdhui': retards,
                'taux_presence': taux_presence,
                'semaine_presents': semaine_presents,
                'semaine_absents': semaine_absents,
                'semaine_retards': semaine_retards,
                'taux_semaine': taux_semaine,
                'mois_presents': mois_presents,
                'mois_absents': mois_absents,
                'mois_retards': mois_retards,
                'taux_mois': taux_mois,
                'annee_presents': annee_presents,
                'annee_absents': annee_absents,
                'annee_retards': annee_retards,
                'taux_annee': taux_annee,
                'conges_en_attente': conges_en_attente,
                'conges_approuves': conges_approuves,
                'justifs_en_attente': justifs_en_attente,
                'justifs_validees': justifs_validees,
                'justifs_rejetees': justifs_rejetees,
                'alertes': conges_en_attente + justifs_en_attente,
            },
            'presences_semaine': presences_semaine_detail,
            'evolution_mensuelle': evolution_mensuelle,
            'repartition_statut': repartition_statut_formatee,
            'conges_par_type': conges_par_type,
            'activites_recentes': activites,
        }

        # 4. SAUVEGARDE EN CACHE
        cache.set(cache_key, response_data, CACHE_DASHBOARD_TIMEOUT)
        
        response = Response(response_data, status=status.HTTP_200_OK)
        response['X-Cache'] = 'MISS'
        return response


class DashboardEmployesStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Stats détaillées des employés")
    def get(self, request):
        cached_data = cache.get(CACHE_KEY_EMPLOYES)
        
        if cached_data is not None:
            response = Response(cached_data, status=status.HTTP_200_OK)
            response['X-Cache'] = 'HIT'
            return response
        
        total = Employe.objects.count()
        actifs = Employe.objects.filter(is_active=True).count()
        inactifs = total - actifs
        
        par_role = list(
            Employe.objects.values('role')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        
        month_start = date.today().replace(day=1)
        top_absents = list(
            Presence.objects.filter(statut='ABSENT', date__gte=month_start)
            .values('employe__nom', 'employe__prenom')
            .annotate(total_absences=Count('id'))
            .order_by('-total_absences')[:5]
        )
        
        response_data = {
            'total': total,
            'actifs': actifs,
            'inactifs': inactifs,
            'par_role': par_role,
            'top_absents_mois': top_absents,
        }
        
        cache.set(CACHE_KEY_EMPLOYES, response_data, CACHE_DASHBOARD_TIMEOUT)
        
        response = Response(response_data, status=status.HTTP_200_OK)
        response['X-Cache'] = 'MISS'
        return response


class ClearDashboardCacheView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Vider le cache du dashboard")
    def post(self, request):
        cache.delete_pattern('dashboard_stats_*')
        cache.delete(CACHE_KEY_EMPLOYES)
        
        return Response({
            'detail': 'Cache du dashboard vidé avec succès.',
            'timestamp': date.today().isoformat()
        }, status=status.HTTP_200_OK)