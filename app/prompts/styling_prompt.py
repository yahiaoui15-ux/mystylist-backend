<!-- ════════════════════════════════════════════════════════════════════════════════
     PAGES 16-21: STYLING COMPLET - A3 PAYSAGE
     Copiez ce code ENTIER après la PAGE 15 (Accessoires) dans votre template
     ════════════════════════════════════════════════════════════════════════════════ -->

<!-- PAGE 16 : VOTRE PROFIL STYLISTIQUE & ARCHÉTYPES -->
<div class="page" style="page-break-before:always;">
  <div class="page-header" style="border-bottom:2px solid #9b59b6;">
    <h2 class="page-title">🎯 Votre Profil Stylistique</h2>
    <span class="page-number">Page 16 / 21</span>
  </div>

  <!-- BLOC 1: Essence Stylistique -->
  <div style="background:linear-gradient(135deg, #f0ecf9 0%, #f8f4ff 100%); padding:25px; border-radius:12px; border-left:5px solid #9b59b6; margin-bottom:25px;">
    <h3 style="color:#9b59b6; margin:0 0 15px 0; font-size:22px; font-weight:700;">✨ Votre Essence Stylistique</h3>
    
    <p style="color:#2c3e50; font-size:14px; line-height:1.8; margin:0 0 15px 0;">
      {{style.essenceShort | default: "Votre style personnel reflète une harmonie unique entre votre silhouette, vos couleurs naturelles et votre personnalité."}}
    </p>
    
    <div style="background:white; padding:15px; border-radius:8px; border-left:3px solid #e91e63;">
      <p style="color:#666; font-size:13px; line-height:1.6; margin:0; font-style:italic;">
        💡 Conseil: Gardez cette essence à l'esprit lors de vos achats. Elle vous aide à ignorer les tendances qui ne vous conviennent pas.
      </p>
    </div>
  </div>

  <!-- BLOC 2: Lecture Psycho-Stylistique -->
  <div style="background:#f8f9fa; padding:20px; border-radius:10px; margin-bottom:25px;">
    <h3 style="color:#2c3e50; margin:0 0 12px 0; font-size:18px; font-weight:700;">👁️ Ce que votre style dit de vous</h3>
    <p style="color:#555; font-size:12px; line-height:1.7; margin:0;">
      {{style.psychoStylisticReading | default: "Votre style reflète vos choix conscients et votre personnalité profonde. Chaque pièce que vous choisissez raconte une histoire."}}
    </p>
  </div>

  <!-- BLOC 3: Archétype Principal -->
  <div style="background:white; padding:20px; border-radius:10px; box-shadow:0 3px 12px rgba(0,0,0,0.08); border-left:5px solid #9b59b6;">
    <h3 style="color:#9b59b6; margin:0 0 15px 0; font-size:18px; font-weight:700;">👗 Votre Archétype Principal</h3>
    
    {% if style.primaryArchetype %}
      <div style="display:flex; align-items:flex-start; gap:15px;">
        <div style="width:70px; height:70px; border-radius:999px; background:#9b59b6; color:white; display:flex; align-items:center; justify-content:center; font-size:32px; flex-shrink:0;">
          {{style.primaryArchetype.icon | default: '👗'}}
        </div>
        <div style="flex:1;">
          <h4 style="color:#9b59b6; margin:0 0 8px 0; font-size:16px; font-weight:700;">
            {{style.primaryArchetype.name | default: "Votre style"}}
          </h4>
          <p style="color:#555; font-size:12px; line-height:1.6; margin:0;">
            {{style.primaryArchetype.description | default: "Cet archétype incarne votre style naturel dominant."}}
          </p>
        </div>
      </div>
    {% endif %}
  </div>

  <div class="page-footer" style="margin-top:30px;">
    <span class="footer-brand">my-stylist.io©</span>
    <span class="footer-contact">contact@my-stylist.io</span>
  </div>
</div>

<!-- PAGE 17 : LES 5 ARCHÉTYPES + MIX & MATCH FORMULAS -->
<div class="page" style="page-break-before:always;">
  <div class="page-header" style="border-bottom:2px solid #9b59b6;">
    <h2 class="page-title">🌈 Vos Archétypes & Mix & Match</h2>
    <span class="page-number">Page 17 / 21</span>
  </div>

  <!-- Les 5 Archétypes -->
  <div style="margin-bottom:25px;">
    <h3 style="color:#388e3c; margin:0 0 15px 0; font-size:18px; font-weight:700;">Les 4 Archétypes qui vous Complètent</h3>
    
    {% if style.archetypes %}
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
        {% for archetype in style.archetypes limit:4 %}
          <div style="background:#f0f7f4; padding:14px; border-radius:10px; border-left:3px solid #4caf50;">
            <h4 style="color:#388e3c; margin:0 0 6px 0; font-size:13px; font-weight:700;">{{archetype.name}}</h4>
            <p style="color:#555; font-size:11px; line-height:1.5; margin:0;">
              {{archetype.description}}
            </p>
          </div>
        {% endfor %}
      </div>
    {% endif %}
  </div>

  <!-- Mix & Match Formulas -->
  <div>
    <h3 style="color:#2c3e50; margin:0 0 15px 0; font-size:18px; font-weight:700;">🧩 Mix & Match: Vos 3 Formulas Gagnantes</h3>
    
    {% if style.mix_and_match_formulas %}
      {% for formula in style.mix_and_match_formulas limit:3 %}
        <div style="background:{% if forloop.index == 1 %}#e8f5e9{% elsif forloop.index == 2 %}#f3e5f5{% else %}#ffe8f0{% endif %}; padding:15px; border-radius:10px; margin-bottom:12px; border-left:5px solid {% if forloop.index == 1 %}#4caf50{% elsif forloop.index == 2 %}#ba68c8{% else %}#e83e8c{% endif %};">
          
          <h4 style="color:{% if forloop.index == 1 %}#388e3c{% elsif forloop.index == 2 %}#6a1b9a{% else %}#d63384{% endif %}; margin:0 0 8px 0; font-size:14px; font-weight:700;">
            {{formula.title}}
          </h4>
          
          <p style="color:#666; font-size:11px; margin:0 0 10px 0; font-style:italic;">
            {{formula.context}}
          </p>
          
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;">
            <div>
              <p style="color:{% if forloop.index == 1 %}#388e3c{% elsif forloop.index == 2 %}#6a1b9a{% else %}#d63384{% endif %}; font-weight:700; margin:0 0 4px 0; font-size:10px;">BASIQUES:</p>
              <p style="color:#555; font-size:10px; margin:0; line-height:1.5;">
                {% for item in formula.base_items %}{{item}}{% if forloop.last %}{% else %}<br>{% endif %}{% endfor %}
              </p>
            </div>
            <div>
              <p style="color:{% if forloop.index == 1 %}#388e3c{% elsif forloop.index == 2 %}#6a1b9a{% else %}#d63384{% endif %}; font-weight:700; margin:0 0 4px 0; font-size:10px;">STATEMENTS:</p>
              <p style="color:#555; font-size:10px; margin:0; line-height:1.5;">
                {% for item in formula.statement_items %}{{item}}{% if forloop.last %}{% else %}<br>{% endif %}{% endfor %}
              </p>
            </div>
          </div>
          
          <div style="background:white; padding:8px; border-radius:6px;">
            <p style="color:#555; font-size:10px; margin:0; font-style:italic;">
              💡 {{formula.styling_tip}}
            </p>
          </div>
        </div>
      {% endfor %}
    {% endif %}
  </div>

  <div class="page-footer" style="margin-top:30px;">
    <span class="footer-brand">my-stylist.io©</span>
    <span class="footer-contact">contact@my-stylist.io</span>
  </div>
</div>

<!-- PAGE 18 : CAPSULE WARDROBE - BASIQUES -->
<div class="page" style="page-break-before:always;">
  <div class="page-header" style="border-bottom:2px solid #9b59b6;">
    <h2 class="page-title">👔 Garde-Robe Capsule: Les Basiques</h2>
    <span class="page-number">Page 18 / 21</span>
  </div>

  <div style="background:#f0f4f8; padding:15px; border-radius:10px; margin-bottom:20px; border-left:4px solid #17a2b8;">
    <p style="margin:0; color:#2c3e50; font-size:12px; line-height:1.6;">
      <strong>Les pièces essentielles:</strong> Ces couleurs neutres forment la fondation indestructible de votre garde-robe. 
      Investissez dans la QUALITÉ (coton bio, laine fine) plutôt que la quantité. Budget estimé première phase: 200-300€
    </p>
  </div>

  {% if style.capsule_wardrobe.basics %}
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px;">
      {% for basic in style.capsule_wardrobe.basics limit:6 %}
        <div style="background:white; padding:12px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.08); border:1px solid #ecf0f1;">
          <div style="background:#f5f5f5; width:100%; height:70px; border-radius:8px; margin-bottom:10px; display:flex; align-items:center; justify-content:center; font-size:28px;">
            {% if forloop.index == 1 %}👕{% elsif forloop.index == 2 %}👖{% elsif forloop.index == 3 %}🩳{% elsif forloop.index == 4 %}🧥{% elsif forloop.index == 5 %}👠{% else %}👜{% endif %}
          </div>
          <h4 style="color:#2c3e50; margin:0 0 5px 0; font-size:12px; font-weight:700;">{{basic.name}}</h4>
          <p style="color:#7f8c8d; font-size:10px; line-height:1.4; margin:0 0 6px 0;">
            {{basic.description}}
          </p>
          <p style="color:#999; font-size:9px; margin:0; font-weight:600;">💰 {{basic.price_range}}</p>
        </div>
      {% endfor %}
    </div>
  {% endif %}

  <div style="background:#e8f5e9; padding:12px; border-radius:10px; margin-top:15px; border-left:4px solid #4caf50;">
    <p style="margin:0; color:#388e3c; font-size:11px; line-height:1.5;">
      <strong>✅ Avec ces 6 basiques:</strong> Vous avez la fondation solide. Chaque pièce se porte seule ou en combo. Une fois achetées, c'est fini pour 1-2 ans!
    </p>
  </div>

  <div class="page-footer" style="margin-top:30px;">
    <span class="footer-brand">my-stylist.io©</span>
    <span class="footer-contact">contact@my-stylist.io</span>
  </div>
</div>

<!-- PAGE 19 : CAPSULE WARDROBE - STATEMENTS -->
<div class="page" style="page-break-before:always;">
  <div class="page-header" style="border-bottom:2px solid #9b59b6;">
    <h2 class="page-title">✨ Garde-Robe Capsule: Les Statements</h2>
    <span class="page-number">Page 19 / 21</span>
  </div>

  <div style="background:#fff5e6; padding:15px; border-radius:10px; margin-bottom:20px; border-left:4px solid #f39c12;">
    <p style="margin:0; color:#2c3e50; font-size:12px; line-height:1.6;">
      <strong>Les pièces déclaratives:</strong> Ces pièces COLORÉES expriment votre personnalité unique. 
      Combinez 1 statement avec un basique neutre = tenue complète et harmonieuse! Budget: 150-250€ pour 6 pièces
    </p>
  </div>

  {% if style.capsule_wardrobe.statements %}
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px;">
      {% for statement in style.capsule_wardrobe.statements limit:6 %}
        <div style="background:white; padding:12px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.08); border:2px solid #f39c12;">
          <div style="background:linear-gradient(135deg, #C19A6B 0%, #E2725B 100%); width:100%; height:70px; border-radius:8px; margin-bottom:10px; display:flex; align-items:center; justify-content:center; color:white; font-size:11px; font-weight:700; text-align:center;">
            Couleur {{forloop.index}}
          </div>
          <h4 style="color:#2c3e50; margin:0 0 5px 0; font-size:12px; font-weight:700;">{{statement.name}}</h4>
          <p style="color:#7f8c8d; font-size:10px; line-height:1.4; margin:0 0 6px 0;">
            {{statement.description}}
          </p>
          <p style="color:#999; font-size:9px; margin:0; font-weight:600;">💰 {{statement.price_range}}</p>
        </div>
      {% endfor %}
    </div>
  {% endif %}

  <div style="background:#f3e5f5; padding:12px; border-radius:10px; margin-top:15px; border-left:4px solid #ba68c8;">
    <p style="margin:0; color:#6a1b9a; font-size:11px; line-height:1.5;">
      <strong>✨ Formule gagnante:</strong> Chaque statement se porte avec UN basique neutre. Exemple: Chemise camel + jean noir = 1 tenue parfaite. Variez juste le statement!
    </p>
  </div>

  <div class="page-footer" style="margin-top:30px;">
    <span class="footer-brand">my-stylist.io©</span>
    <span class="footer-contact">contact@my-stylist.io</span>
  </div>
</div>

<!-- PAGE 20 : TENUES PRÊTES-À-PORTER -->
<div class="page" style="page-break-before:always;">
  <div class="page-header" style="border-bottom:2px solid #9b59b6;">
    <h2 class="page-title">👗 7 Jours de Tenues Prêtes-à-Porter</h2>
    <span class="page-number">Page 20 / 21</span>
  </div>

  <div style="background:#d1ecf1; padding:12px; border-radius:10px; margin-bottom:15px; border-left:4px solid #17a2b8;">
    <p style="margin:0; color:#2c3e50; font-size:11px; line-height:1.5;">
      <strong>🎯 Pas de prise de tête le matin!</strong> Voici 7 tenues testées. Portez-les en rotation pendant un mois, changez juste les accessoires et bijoux!
    </p>
  </div>

  {% if style.ready_to_wear_outfits %}
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
      {% for outfit in style.ready_to_wear_outfits limit:7 %}
        <div style="background:#f8f9fa; padding:11px; border-radius:8px; border-left:3px solid #9b59b6;">
          <h4 style="color:#9b59b6; margin:0 0 5px 0; font-size:11px; font-weight:700;">{{outfit.day}}</h4>
          <p style="color:#999; font-size:9px; margin:0 0 7px 0; font-style:italic;">{{outfit.context}}</p>
          <p style="color:#2c3e50; font-size:10px; line-height:1.4; margin:0;">
            {% for item in outfit.items %}{{item}}{% if forloop.last %}{% else %}<br>{% endif %}{% endfor %}
          </p>
        </div>
      {% endfor %}
    </div>
  {% endif %}

  <div style="background:#fff5e6; padding:12px; border-radius:10px; margin-top:12px; border-left:4px solid #f39c12;">
    <p style="margin:0; color:#e67e22; font-size:10px; line-height:1.5;">
      <strong>💡 ASTUCE:</strong> Vous avez 7 tenues de base. Portez-les en boucle pendant un mois entier et changez juste les bijoux/accessoires. Ensuite, vos formules gagnantes deviennent des automatismes!
    </p>
  </div>

  <div class="page-footer" style="margin-top:30px;">
    <span class="footer-brand">my-stylist.io©</span>
    <span class="footer-contact">contact@my-stylist.io</span>
  </div>
</div>

<!-- PAGE 21 : VOTRE PLAN D'ACTION 4 SEMAINES + AUDIT IA -->
<div class="page" style="page-break-before:always;">
  <div class="page-header" style="border-bottom:2px solid #9b59b6;">
    <h2 class="page-title">🚀 Plan d'Action 4 Semaines</h2>
    <span class="page-number">Page 21 / 21</span>
  </div>

  {% if style.styling_plan_4_weeks %}
    {% for week in style.styling_plan_4_weeks limit:4 %}
      <div style="background:{% if forloop.index == 1 %}#e8f5e9{% elsif forloop.index == 2 %}#fff5e6{% elsif forloop.index == 3 %}#e1f5fe{% else %}#f3e5f5{% endif %}; padding:12px; border-radius:10px; margin-bottom:10px; border-left:5px solid {% if forloop.index == 1 %}#4caf50{% elsif forloop.index == 2 %}#f39c12{% elsif forloop.index == 3 %}#0288d1{% else %}#ba68c8{% endif %};">
        
        <h4 style="color:{% if forloop.index == 1 %}#388e3c{% elsif forloop.index == 2 %}#e67e22{% elsif forloop.index == 3 %}#01579b{% else %}#6a1b9a{% endif %}; margin:0 0 8px 0; font-size:12px; font-weight:700;">
          {{week.week}}
        </h4>
        
        <p style="color:#555; font-size:10px; margin:0 0 6px 0; font-style:italic;">
          <strong>Focus:</strong> {{week.focus}}
        </p>
        
        <ul style="color:#555; font-size:9px; margin:0 0 6px 0; padding-left:14px; line-height:1.4;">
          {% for action in week.actions %}
            <li style="margin-bottom:2px;">{{action}}</li>
          {% endfor %}
        </ul>
        
        <p style="color:{% if forloop.index == 1 %}#388e3c{% elsif forloop.index == 2 %}#e67e22{% elsif forloop.index == 3 %}#01579b{% else %}#6a1b9a{% endif %}; font-size:10px; font-weight:600; margin:0;">
          💰 Budget: {{week.budget_range}}
        </p>
      </div>
    {% endfor %}
  {% endif %}

  <!-- AUDIT DE GARDE-ROBE UPSELL -->
  <div style="background:linear-gradient(135deg, #f0ecf9 0%, #f8f4ff 100%); padding:15px; border-radius:10px; border:2px solid #9b59b6; margin-top:15px;">
    <h3 style="color:#9b59b6; margin:0 0 10px 0; font-size:14px; font-weight:700;">
      {% if style.wardrobe_audit_pitch.title %}{{style.wardrobe_audit_pitch.title}}{% else %}Prochaine étape: L'audit de votre garde-robe IA{% endif %}
    </h3>
    
    <p style="color:#555; font-size:10px; line-height:1.5; margin:0 0 8px 0;">
      {% if style.wardrobe_audit_pitch.description %}{{style.wardrobe_audit_pitch.description}}{% else %}Analysez ce que vous possédez déjà et optimisez votre dressing{% endif %}
    </p>
    
    {% if style.wardrobe_audit_pitch.benefits %}
      <ul style="color:#555; font-size:9px; margin:0; padding-left:14px; line-height:1.4;">
        {% for benefit in style.wardrobe_audit_pitch.benefits limit:5 %}
          <li style="margin-bottom:2px;">{{benefit}}</li>
        {% endfor %}
      </ul>
    {% endif %}
  </div>

  <!-- RÉSUMÉ FINAL -->
  <div style="background:#f8f9fa; padding:12px; border-radius:10px; margin-top:12px; border-left:4px solid #2c3e50;">
    <p style="margin:0; color:#2c3e50; font-size:10px; line-height:1.5;">
      <strong>Votre profil complet:</strong> Saison {{colorimetry.saison_confirmee}} • Sous-ton {{colorimetry.sous_ton_detecte}} • Silhouette {{morphology_page1.bodyType}}<br>
      <strong>Budget phase 1:</strong> 450-700€ répartis sur 4 semaines<br>
      <strong>Objectif:</strong> Une garde-robe cohérente, intemporelle et facile à porter
    </p>
  </div>

  <div class="page-footer" style="margin-top:25px;">
    <span class="footer-brand">my-stylist.io©</span>
    <span class="footer-contact">contact@my-stylist.io</span>
  </div>
</div>

<!-- ════════════════════════════════════════════════════════════════════════════════
     FIN DES PAGES 16-21
     ════════════════════════════════════════════════════════════════════════════════ -->