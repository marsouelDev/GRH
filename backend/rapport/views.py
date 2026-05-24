import openpyxl
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from .models import Rapport
from .serializers import RapportSerializer
from justification.permissions import IsRhOrAdminRole  

class RapportListCreateView(APIView):
    """
    GET  /rapports/ -> Lister tous les rapports de l'entreprise (RH/Admin uniquement)
    POST /rapports/ -> Générer un nouveau rapport avec calcul SQL automatisé (RH/Admin uniquement)
    """
    def get_permissions(self):
        return [IsRhOrAdminRole()]

    @extend_schema(
        summary="Liste des rapports", 
        responses=RapportSerializer(many=True),
        parameters=[OpenApiParameter(name='type', description="Filtrer par type de rapport (ex: PRESENCES)", required=False, type=str)]
    )
    def get(self, request):
        qs = Rapport.objects.all()
        type_rapport = request.query_params.get('type')
        if type_rapport: 
            qs = qs.filter(type_rapport=type_rapport)
        return Response(RapportSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Générer un rapport (RH/Admin)", request=RapportSerializer, responses=RapportSerializer)
    def post(self, request):
        serializer = RapportSerializer(data=request.data)
        if serializer.is_valid():
            rapport = serializer.save(genere_par=request.user)
            rapport.genererDonnees()
            return Response(RapportSerializer(rapport).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RapportDetailView(APIView):
   
    def get_permissions(self):
        return [IsRhOrAdminRole()]

    def get_object(self, pk):
        try: return Rapport.objects.get(pk=pk)
        except Rapport.DoesNotExist: return None

    @extend_schema(summary="Détail d'un rapport", responses=RapportSerializer)
    def get(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({"detail": "Rapport introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response(RapportSerializer(obj).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Supprimer un rapport", responses=None)
    def delete(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({"detail": "Rapport introuvable."}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({"detail": "Rapport supprimé définitivement."}, status=status.HTTP_204_NO_CONTENT)


class RapportRegeneView(APIView):
    
    def get_permissions(self):
        return [IsRhOrAdminRole()]

    @extend_schema(summary="Regénérer les données du rapport", responses=RapportSerializer)
    def put(self, request, pk):
        try:
            rapport = Rapport.objects.get(pk=pk)
        except Rapport.DoesNotExist:
            return Response({"detail": "Rapport introuvable."}, status=status.HTTP_404_NOT_FOUND)
        
        rapport.genererDonnees()
        return Response(RapportSerializer(rapport).data, status=status.HTTP_200_OK)


class ExportRapportExcelView(APIView):
   
    def get_permissions(self):
        return [IsRhOrAdminRole()]

    @extend_schema(summary="Exporter le rapport en Excel")
    def get(self, request, pk):
        try:
            rapport = Rapport.objects.get(pk=pk)
        except Rapport.DoesNotExist:
            return Response({"detail": "Rapport introuvable."}, status=status.HTTP_404_NOT_FOUND)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Données du Rapport"

        # Entête du tableur
        ws.append([f"Rapport : {rapport.titre}"])
        ws.append([f"Type : {rapport.get_type_rapport_display()}"])
        ws.append([f"Période : {rapport.date_debut or 'Début'} au {rapport.date_fin or 'Fin'}"])
        ws.append([]) 

        ws.append(["Indicateur", "Valeur"])
        for cle, valeur in rapport.donnees.items():
            if isinstance(valeur, list):
                # Extraction sécurisée par clés nommées pour la liste par_role
                for item in valeur:
                    role_nom = item.get('role', 'Inconnu')
                    role_total = item.get('total', 0)
                    ws.append([f"{cle.replace('_', ' ').capitalize()} ({role_nom})", role_total])
            else:
                ws.append([cle.replace('_', ' ').capitalize(), valeur])

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="rapport_{pk}.xlsx"'
        wb.save(response)
        return response


class ExportRapportPdfView(APIView):
    
    def get_permissions(self):
        return [IsRhOrAdminRole()]

    @extend_schema(summary="Exporter le rapport en PDF")
    def get(self, request, pk):
        try:
            rapport = Rapport.objects.get(pk=pk)
        except Rapport.DoesNotExist:
            return Response({"detail": "Rapport introuvable."}, status=status.HTTP_404_NOT_FOUND)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="rapport_{pk}.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        styles = getSampleStyleSheet()

        story.append(Paragraph(f"<b>Bilan RH : {rapport.titre}</b>", styles["Title"]))
        story.append(Spacer(1, 15))
        story.append(Paragraph(f"<b>Type de bilan :</b> {rapport.get_type_rapport_display()}", styles["Normal"]))
        story.append(Paragraph(f"<b>Période d'analyse :</b> {rapport.date_debut or 'Début'} au {rapport.date_fin or 'Fin'}", styles["Normal"]))
        story.append(Paragraph(f"<b>Généré le :</b> {rapport.date_creation.strftime('%d/%m/%Y à %H:%M')}", styles["Normal"]))
        story.append(Spacer(1, 25))

        tableau_donnees = [["Indicateur / Métrique", "Valeur statistique"]]
        for cle, valeur in rapport.donnees.items():
            if isinstance(valeur, list):
                for item in valeur:
                    role_nom = item.get('role', 'Inconnu')
                    role_total = item.get('total', 0)
                    tableau_donnees.append([f"{cle.replace('_', ' ').capitalize()} ({role_nom})", str(role_total)])
            else:
                tableau_donnees.append([cle.replace('_', ' ').capitalize(), str(valeur)])

        table = Table(tableau_donnees, colWidths=[300, 180])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#4f46e5')), 
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        
        story.append(table)
        doc.build(story)
        return response
