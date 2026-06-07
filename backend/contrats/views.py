import io
from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from notification.models import Notification
from .models import Contrat
from .serializers import ContratSerializer
from RH.models import RH
from administrateur.models import Administrateur
from employees.models import Employe
from .permissions import IsRhOnlyUserRole, IsRhOrAdminUserRole


class ContratListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsRhOnlyUserRole()]

    @extend_schema(summary="Liste des contrats", responses={200: ContratSerializer(many=True)}, 
        parameters=[OpenApiParameter(name='employe', description="Filtrer par ID (RH/Admin uniquement)", required=False, type=int)]
    )
    def get(self, request):
        if isinstance(request.user, RH) or isinstance(request.user, Administrateur):
            ps = Contrat.objects.select_related('employe', 'poste').all().order_by('-date_debut')
            employe_id = request.query_params.get('employe')
            if employe_id:
                ps = ps.filter(employe_id=employe_id)
                
        elif isinstance(request.user, Employe):
            ps = Contrat.objects.select_related('employe', 'poste').filter(employe=request.user).order_by('-date_debut')
            
        else:
            return Response(
                {"detail": "Type d'utilisateur non autorisé à l'accès contractuel."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ContratSerializer(ps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Créer un contrat (RH uniquement)", request=ContratSerializer, responses={201: ContratSerializer})
    def post(self, request):
        serializer = ContratSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContratDetailUpdateDeleteAPIView(APIView):
    def get_permissions(self):
        return [IsRhOnlyUserRole()]

    def get_object(self, id):
        try: return Contrat.objects.get(id=id)
        except Contrat.DoesNotExist: return None

    @extend_schema(summary="Modifier un contrat (RH uniquement)", request=ContratSerializer, responses={200: ContratSerializer})
    def put(self, request, id):
        contrat = self.get_object(id)
        if not contrat: 
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ContratSerializer(contrat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Clôturer un contrat (RH uniquement)")
    def delete(self, request, id):
        contrat = self.get_object(id)
        if not contrat: 
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        nom_employe = f"{contrat.employe.nom} {contrat.employe.prenom}"
        type_contrat = contrat.type_contrat
        
        # Clôturer le contrat
        contrat.statut = 'TERMINE'
        contrat.save()
        
        rhs = RH.objects.filter(is_active=True).exclude(id=request.user.id)
        for rh in rhs:
            Notification.envoyer(
                destinataire=rh,
                type_notif=Notification.TypeNotification.CONTRAT_CLOTURE,
                titre=f"📋 Contrat clôturé - {nom_employe}",
                message=(
                    f"{request.user.nom} {request.user.prenom} a clôturé le contrat "
                    f"de {nom_employe} (type: {type_contrat})."
                ),
                lien=f"/contrats/{contrat.id}"
            )
        
        return Response({
            "detail": "Le contrat a bien été marqué comme terminé.",
            "notifications_envoyees": rhs.count()
        }, status=status.HTTP_200_OK)

class GenererContratPDFView(APIView):
    permission_classes = [IsRhOrAdminUserRole]

    def get(self, request, id):
        try:
            contrat = Contrat.objects.select_related('employe', 'poste').get(id=id)
        except Contrat.DoesNotExist:
            return Response({"detail": "Contrat introuvable."}, status=status.HTTP_404_NOT_FOUND)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, spaceAfter=30)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], alignment=TA_JUSTIFY, leading=16, spaceAfter=12)

        story.append(Paragraph(f"<b>CONTRAT DE TRAVAIL ({contrat.type_contrat})</b>", title_style))
        story.append(Spacer(1, 15))
        
        intro = f"Entre les soussignés, la société <b>RH_Manager</b> d'une part, et Monsieur/Madame <b>{contrat.employe.nom} {contrat.employe.prenom}</b>, il a été convenu le présent contrat de travail."
        story.append(Paragraph(intro, body_style))
        story.append(Paragraph(f"<b>Article 1 - Poste :</b> Embauché en qualité de <b>{contrat.poste.intitule}</b>.", body_style))
        story.append(Paragraph(f"<b>Article 2 - Durée :</b> Débute le <b>{contrat.date_debut}</b>.", body_style))
        
        if contrat.type_contrat != 'CDI' and contrat.date_fin:
            story.append(Paragraph(f"Il prendra fin le <b>{contrat.date_fin}</b>.", body_style))

        story.append(Paragraph(f"<b>Article 3 - Rémunération :</b> Salaire mensuel de <b>{contrat.salaire_base} €</b>.", body_style))
        story.append(Spacer(1, 40))
        story.append(Paragraph("Fait en double exemplaire, le ____________________.", body_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph("<b>Signature Employeur &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Signature Employé</b>", body_style))

        doc.build(story)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"Contrat_{contrat.employe.nom}.pdf")
