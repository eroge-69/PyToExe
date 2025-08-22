import base64
import zipfile
import os
from io import BytesIO

# Création du contenu Excel
excel_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <Styles>
    <Style ss:ID="Default" ss:Name="Normal">
      <Alignment ss:Vertical="Center"/>
      <Font ss:FontName="Calibri" ss:Size="11" ss:Color="#000000"/>
    </Style>
    <Style ss:ID="Title">
      <Font ss:FontName="Calibri" ss:Size="16" ss:Bold="1"/>
      <Alignment ss:Horizontal="Center"/>
    </Style>
    <Style ss:ID="Header">
      <Font ss:FontName="Calibri" ss:Size="12" ss:Bold="1" ss:Color="#FFFFFF"/>
      <Interior ss:Color="#4472C4" ss:Pattern="Solid"/>
      <Alignment ss:Horizontal="Center"/>
    </Style>
    <Style ss:ID="Input">
      <Font ss:FontName="Calibri" ss:Size="11"/>
      <Interior ss:Color="#BDD7EE" ss:Pattern="Solid"/>
    </Style>
    <Style ss:ID="Calculation">
      <Font ss:FontName="Calibri" ss:Size="11"/>
      <Interior ss:Color="#E2EFDA" ss:Pattern="Solid"/>
    </Style>
    <Style ss:ID="Result">
      <Font ss:FontName="Calibri" ss:Size="11" ss:Bold="1"/>
      <Interior ss:Color="#FFE699" ss:Pattern="Solid"/>
    </Style>
  </Styles>

  <Worksheet ss:Name="Calcul Glissement">
    <Table>
      <Column ss:Width="120"/>
      <Column ss:Width="80"/>
      <Column ss:Width="40"/>
      <Column ss:Width="120"/>
      <Column ss:Width="80"/>
      <Column ss:Width="40"/>
      
      <Row>
        <Cell ss:StyleID="Title" ss:MergeAcross="5"><Data ss:Type="String">CALCUL DE GLISSEMENT D'UN RADIER - EUROCODE 7</Data></Cell>
      </Row>
      <Row/>
      
      <Row>
        <Cell ss:StyleID="Header" ss:MergeAcross="5"><Data ss:Type="String">CHARGEMENTS CARACTÉRISTIQUES</Data></Cell>
      </Row>
      <Row>
        <Cell><Data ss:Type="String">Effort vertical V_k</Data></Cell>
        <Cell ss:StyleID="Input"><Data ss:Type="Number">500</Data></Cell>
        <Cell><Data ss:Type="String">kN</Data></Cell>
        <Cell><Data ss:Type="String">Effort horizontal H_k</Data></Cell>
        <Cell ss:StyleID="Input"><Data ss:Type="Number">100</Data></Cell>
        <Cell><Data ss:Type="String">kN</Data></Cell>
      </Row>
      <Row/>
      
      <Row>
        <Cell ss:StyleID="Header" ss:MergeAcross="5"><Data ss:Type="String">GÉOMÉTRIE DU RADIER</Data></Cell>
      </Row>
      <Row>
        <Cell><Data ss:Type="String">Longueur L</Data></Cell>
        <Cell ss:StyleID="Input"><Data ss:Type="Number">5</Data></Cell>
        <Cell><Data ss:Type="String">m</Data></Cell>
        <Cell><Data ss:Type="String">Largeur B</Data></Cell>
        <Cell ss:StyleID="Input"><Data ss:Type="Number">3</Data></Cell>
        <Cell><Data ss:Type="String">m</Data></Cell>
      </Row>
      <Row>
        <Cell><Data ss:Type="String">Épaisseur</Data></Cell>
        <Cell ss:StyleID="Input"><Data ss:Type="Number">0.3</Data></Cell>
        <Cell><Data ss:Type="String">m</Data></Cell>
        <Cell><Data ss:Type="String">Poids béton</Data></Cell>
        <Cell ss:StyleID="Input"><Data ss:Type="Number">25</Data></Cell>
        <Cell><Data ss:Type="String">kN/m³</Data></Cell>
      </Row>
      <Row/>
      
      <Row>
        <Cell ss:StyleID="Header" ss:MergeAcross="5"><Data ss:Type="String">CARACTÉRISTIQUES DU SOL</Data></Cell>
      </Row>
      <Row>
        <Cell><Data ss:Type="String">Angle φ'</Data></Cell>
        <Cell ss:StyleID="Input"><Data ss:Type="Number">30</Data></Cell>
        <Cell><Data ss:Type="String">°</Data></Cell>
        <Cell><Data ss:Type="String">Cohésion c'</Data></Cell>
        <Cell ss:StyleID="Input"><Data ss:Type="Number">5</Data></Cell>
        <Cell><Data ss:Type="String">kPa</Data></Cell>
      </Row>
      <Row>
        <Cell><Data ss:Type="String">Poids volumique γ</Data></Cell>
        <Cell ss:StyleID="Input"><Data ss:Type="Number">18</Data></Cell>
        <Cell><Data ss:Type="String">kN/m³</Data></Cell>
      </Row>
      <Row/>
      
      <Row>
        <Cell ss:StyleID="Header" ss:MergeAcross="5"><Data ss:Type="String">COEFFICIENTS PARTIELS EC7</Data></Cell>
      </Row>
      <Row>
        <Cell><Data ss:Type="String">γ_φ (frottement)</Data></Cell>
        <Cell ss:StyleID="Input"><Data ss:Type="Number">1.25</Data></Cell>
        <Cell><Data ss:Type="String">-</Data></Cell>
        <Cell><Data ss:Type="String">γ_c (cohésion)</Data></Cell>
        <Cell ss:StyleID="Input"><Data ss:Type="Number">1.25</Data></Cell>
        <Cell><Data ss:Type="String">-</Data></Cell>
      </Row>
      <Row>
        <Cell><Data ss:Type="String">γ_R;h (glissement)</Data></Cell>
        <Cell ss:StyleID="Input"><Data ss:Type="Number">1.1</Data></Cell>
        <Cell><Data ss:Type="String">-</Data></Cell>
      </Row>
      <Row/>
      
      <Row>
        <Cell ss:StyleID="Header" ss:MergeAcross="5"><Data ss:Type="String">CALCULS ET RÉSULTATS</Data></Cell>
      </Row>
      <Row>
        <Cell><Data ss:Type="String">Aire fondation A</Data></Cell>
        <Cell ss:StyleID="Calculation"><Data ss:Type="Formula">=B11*B12</Data></Cell>
        <Cell><Data ss:Type="String">m²</Data></Cell>
        <Cell><Data ss:Type="String">Poids propre W</Data></Cell>
        <Cell ss:StyleID="Calculation"><Data ss:Type="Formula">=B19*B13*B14</Data></Cell>
        <Cell><Data ss:Type="String">kN</Data></Cell>
      </Row>
      <Row>
        <Cell><Data ss:Type="String">Charge verticale V_d</Data></Cell>
        <Cell ss:StyleID="Calculation"><Data ss:Type="Formula">=1.35*(B4+B20)</Data></Cell>
        <Cell><Data ss:Type="String">kN</Data></Cell>
        <Cell><Data ss:Type="String">Charge horizontale H_d</Data></Cell>
        <Cell ss:StyleID="Calculation"><Data ss:Type="Formula">=1.5*B5</Data></Cell>
        <Cell><Data ss:Type="String">kN</Data></Cell>
      </Row>
      <Row>
        <Cell><Data ss:Type="String">Angle φ'_d pondéré</Data></Cell>
        <Cell ss:StyleID="Calculation"><Data ss:Type="Formula">=ATAN(TAN(RADIANS(B16))/B23)</Data></Cell>
        <Cell><Data ss:Type="String">rad</Data></Cell>
        <Cell><Data ss:Type="String">Cohésion c'_d</Data></Cell>
        <Cell ss:StyleID="Calculation"><Data ss:Type="Formula">=B17/B24</Data></Cell>
        <Cell><Data ss:Type="String">kPa</Data></Cell>
      </Row>
      <Row>
        <Cell><Data ss:Type="String">Résistance R_d</Data></Cell>
        <Cell ss:StyleID="Result"><Data ss:Type="Formula">=(B21*TAN(B25)+B26*B19)/B25</Data></Cell>
        <Cell><Data ss:Type="String">kN</Data></Cell>
        <Cell><Data ss:Type="String">Effort H_d</Data></Cell>
        <Cell ss:StyleID="Calculation"><Data ss:Type="Formula">=B22</Data></Cell>
        <Cell><Data ss:Type="String">kN</Data></Cell>
      </Row>
      <Row/>
      
      <Row>
        <Cell ss:StyleID="Header" ss:MergeAcross="5"><Data ss:Type="String">VÉRIFICATION FINALE</Data></Cell>
      </Row>
      <Row>
        <Cell><Data ss:Type="String">Coefficient sécurité FS</Data></Cell>
        <Cell ss:StyleID="Result"><Data ss:Type="Formula">=B27/B22</Data></Cell>
        <Cell><Data ss:Type="String">-</Data></Cell>
        <Cell><Data ss:Type="String">Statut</Data></Cell>
        <Cell ss:StyleID="Result"><Data ss:Type="Formula">=SI(B27>=B22;"OK - STABLE";"NON VERIFIE")</Data></Cell>
        <Cell><Data ss:Type="String">-</Data></Cell>
      </Row>
    </Table>
  </Worksheet>
</Workbook>"""

# Encodage en base64
encoded = base64.b64encode(excel_content.encode('utf-8')).decode('utf-8')

print(f"Voici votre fichier Excel encodé en base64:")
print(encoded)