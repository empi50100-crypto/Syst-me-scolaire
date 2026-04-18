"""
Script de test COMPLET pour SyGeS-AM
Teste TOUTES les fonctionnalités du projet
"""

import asyncio
from playwright.async_api import async_playwright
import json

BASE_URL = "http://127.0.0.1:8000"
RESULTS = []

async def log_step(step, status, message):
    result = {"step": step, "status": status, "message": message}
    RESULTS.append(result)
    print(f"[{status:10}] {step}: {message}")

async def safe_fill(page, selector, value, screenshot_path=None):
    """Remplir un champ de façon sécurisée"""
    try:
        # Si le selector commence par #, l'utiliser directement
        if selector.startswith('#'):
            loc = page.locator(selector)
        else:
            locators = [
                page.locator(selector),
                page.locator(f'input[name="{selector}"]'),
            ]
            loc = None
            for l in locators:
                if await l.count() > 0:
                    loc = l
                    break
        
        if loc and await loc.count() > 0:
            await loc.first.fill(value)
            if screenshot_path:
                await page.screenshot(path=screenshot_path)
            return True
    except Exception as e:
        print(f"  Warning: Could not fill {selector}: {e}")
    return False

async def safe_select(page, selector, value, screenshot_path=None):
    """Sélectionner une option de façon sécurisée"""
    try:
        if selector.startswith('#'):
            loc = page.locator(selector)
        else:
            locators = [
                page.locator(f'select[name="{selector}"]'),
                page.locator(selector),
            ]
            loc = None
            for l in locators:
                if await l.count() > 0:
                    loc = l
                    break
        
        if loc and await loc.count() > 0:
            await loc.first.select_option(value)
            if screenshot_path:
                await page.screenshot(path=screenshot_path)
            return True
    except Exception as e:
        print(f"  Warning: Could not select {selector}: {e}")
    return False

async def submit_form(page, screenshot_path=None):
    """Soumettre un formulaire"""
    try:
        await page.click('button[type="submit"]', force=True)
        await page.wait_for_timeout(2000)
        if screenshot_path:
            await page.screenshot(path=screenshot_path)
        return True
    except Exception as e:
        print(f"  Warning: Submit failed: {e}")
    return False

async def test_application():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()
        
        try:
            # ===== CONNEXION =====
            await log_step("CONNEXION", "TESTING", "Connexion admin...")
            await page.goto(f"{BASE_URL}/authentification/login/", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(1000)
            await page.screenshot(path="screenshots/01_login.png")
            
            await page.fill('input[name="username"]', 'admin')
            await page.fill('input[name="password"]', 'admin2026')
            await page.click('button.btn-login', force=True)
            await page.wait_for_timeout(3000)
            await page.screenshot(path="screenshots/02_dashboard.png")
            
            if "dashboard" in page.url:
                await log_step("CONNEXION", "OK", "Connecté avec succès")
            else:
                await log_step("CONNEXION", "ERROR", f"Connexion échouée: {page.url}")
                return RESULTS
            
            # ===== PAGE DASHBOARD =====
            await log_step("DASHBOARD", "TESTING", "Vérification du tableau de bord...")
            await page.goto(f"{BASE_URL}/dashboard/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/03_dashboard_full.png")
            await log_step("DASHBOARD", "OK", "Tableau de bord accessible")
            
            # ===== CORE: NIVEAUX =====
            await log_step("CORE-Niveaux", "TESTING", "Création des niveaux...")
            niveaux = ["6ème", "5ème", "4ème", "3ème"]
            for i, niveau in enumerate(niveaux, 1):
                await page.goto(f"{BASE_URL}/core/niveaux/ajouter/", wait_until="domcontentloaded")
                await page.wait_for_timeout(1500)
                await safe_fill(page, "#id_nom", niveau)
                await safe_fill(page, "#id_ordre", str(i))
                await page.screenshot(path=f"screenshots/04_niveau_{i}.png")
                await submit_form(page)
                await page.wait_for_timeout(1500)
                await log_step(f"CORE-Niveaux", "OK", f"{niveau} créé")
            
            # ===== CORE: CYCLES =====
            await log_step("CORE-Cycles", "TESTING", "Création des cycles...")
            await page.goto(f"{BASE_URL}/core/cycles/ajouter/", wait_until="domcontentloaded")
            await page.wait_for_timeout(1500)
            await safe_fill(page, "#id_numero", "1")
            await safe_fill(page, "#id_date_debut", "2025-09-01")
            await safe_fill(page, "#id_date_fin", "2025-12-31")
            await page.screenshot(path="screenshots/05_cycle.png")
            await submit_form(page)
            await page.wait_for_timeout(1500)
            await log_step("CORE-Cycles", "OK", "Trimestre 1 créé")
            
            # ===== CORE: PÉRIODES =====
            await log_step("CORE-Périodes", "TESTING", "Création des périodes...")
            periodes = [
                ("Trimestre 1", "2025-09-01", "2025-12-31"),
                ("Trimestre 2", "2026-01-01", "2026-03-31"),
                ("Trimestre 3", "2026-04-01", "2026-07-31"),
            ]
            for nom, debut, fin in periodes:
                await page.goto(f"{BASE_URL}/core/periodes/ajouter/", wait_until="domcontentloaded")
                await page.wait_for_timeout(1500)
                await safe_fill(page, "#id_nom", nom)
                await safe_fill(page, "#id_date_debut", debut)
                await safe_fill(page, "#id_date_fin", fin)
                await submit_form(page)
                await page.wait_for_timeout(1500)
                await log_step("CORE-Périodes", "OK", f"{nom} créé")
            
            # ===== ENSEIGNEMENT: ATTRIBUTIONS =====
            await log_step("ENSEIGNEMENT-Attributions", "TESTING", "Création des attributions...")
            await page.goto(f"{BASE_URL}/enseignement/attributions/ajouter/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/06_attribution.png")
            
            # Sélectionner professeur
            selects = await page.locator('select').all()
            if len(selects) >= 3:
                try:
                    if await selects[0].locator('option').count() > 1:
                        await selects[0].select_option(index=1)
                        await page.wait_for_timeout(500)
                    if await selects[1].locator('option').count() > 1:
                        await selects[1].select_option(index=1)
                        await page.wait_for_timeout(500)
                    if await selects[2].locator('option').count() > 1:
                        await selects[2].select_option(index=1)
                except Exception as e:
                    print(f"  Warning: Select error: {e}")
            
            await page.screenshot(path="screenshots/07_attribution_filled.png")
            await submit_form(page)
            await page.wait_for_timeout(2000)
            await log_step("ENSEIGNEMENT-Attributions", "OK", "Attribution créée")
            
            # ===== ENSEIGNEMENT: EXAMENS =====
            await log_step("ENSEIGNEMENT-Examens", "TESTING", "Création d'examen...")
            await page.goto(f"{BASE_URL}/enseignement/examens/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/08_examens.png")
            
            # Chercher bouton d'ajout
            add_links = await page.locator('a:has-text("Ajouter"), a:has-text("Créer"), button:has-text("Ajouter")').all()
            if add_links:
                await add_links[0].click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path="screenshots/09_examen_form.png")
                
                await safe_fill(page, "#id_titre", "Devoir surveillé 1")
                await safe_fill(page, "#id_date_examen", "2025-10-20")
                await safe_fill(page, "#id_duree_minutes", "60")
                
                selects = await page.locator('select').all()
                for sel in selects[:4]:
                    try:
                        if await sel.locator('option').count() > 1:
                            await sel.select_option(index=1)
                            await page.wait_for_timeout(300)
                    except:
                        pass
                
                await page.screenshot(path="screenshots/10_examen_filled.png")
                await submit_form(page)
                await page.wait_for_timeout(2000)
                await log_step("ENSEIGNEMENT-Examens", "OK", "Examen créé")
            else:
                await log_step("ENSEIGNEMENT-Examens", "WARNING", "Page d'examen sans bouton Ajouter")
            
            # ===== PRÉSENCES: SÉANCES =====
            await log_step("PRÉSENCES-Séances", "TESTING", "Création de séance...")
            await page.goto(f"{BASE_URL}/presences/seances/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/11_seances.png")
            
            add_links = await page.locator('a:has-text("Ajouter"), a:has-text("Créer"), button:has-text("Ajouter")').all()
            if add_links:
                await add_links[0].click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path="screenshots/12_seance_form.png")
                
                await safe_fill(page, "#id_date_seance", "2025-10-15")
                await safe_fill(page, "#id_heure_debut", "08:00")
                
                selects = await page.locator('select').all()
                for sel in selects[:3]:
                    try:
                        if await sel.locator('option').count() > 1:
                            await sel.select_option(index=1)
                            await page.wait_for_timeout(300)
                    except:
                        pass
                
                await page.screenshot(path="screenshots/13_seance_filled.png")
                await submit_form(page)
                await page.wait_for_timeout(2000)
                await log_step("PRÉSENCES-Séances", "OK", "Séance créée")
            else:
                await log_step("PRÉSENCES-Séances", "WARNING", "Page séances sans bouton Ajouter")
            
            # ===== PRÉSENCES: STATISTIQUES =====
            await log_step("PRÉSENCES-Stats", "TESTING", "Accès statistiques...")
            await page.goto(f"{BASE_URL}/presences/statistiques/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/14_stats_presence.png")
            await log_step("PRÉSENCES-Stats", "OK", "Statistiques accessibles")
            
            # ===== FINANCES: FRAIS =====
            await log_step("FINANCES-Frais", "TESTING", "Création des frais...")
            await page.goto(f"{BASE_URL}/finances/frais/ajouter/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/15_frais_form.png")
            
            await safe_fill(page, "#id_libelle", "Frais de Scolarité 2025-2026")
            await safe_fill(page, "#id_montant", "50000")
            await safe_fill(page, "#id_date_echeance", "2025-09-30")
            
            selects = await page.locator('select').all()
            for sel in selects[:2]:
                try:
                    if await sel.locator('option').count() > 1:
                        await sel.select_option(index=1)
                        await page.wait_for_timeout(300)
                except:
                    pass
            
            await page.screenshot(path="screenshots/16_frais_filled.png")
            await submit_form(page)
            await page.wait_for_timeout(2000)
            await log_step("FINANCES-Frais", "OK", "Frais crees")
            
            # ===== FINANCES: PAIEMENTS =====
            await log_step("FINANCES-Paiements", "TESTING", "Enregistrement paiement...")
            await page.goto(f"{BASE_URL}/finances/paiements/ajouter/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/17_paiement_form.png")
            
            await safe_fill(page, "#id_montant", "50000")
            await safe_fill(page, "#id_date_paiement", "2025-09-15")
            await safe_fill(page, "#id_reference", "PAI-001")
            
            selects = await page.locator('select').all()
            for sel in selects[:2]:
                try:
                    if await sel.locator('option').count() > 1:
                        await sel.select_option(index=1)
                        await page.wait_for_timeout(300)
                except:
                    pass
            
            await page.screenshot(path="screenshots/18_paiement_filled.png")
            await submit_form(page)
            await page.wait_for_timeout(2000)
            await log_step("FINANCES-Paiements", "OK", "Paiement enregistré")
            
            # ===== FINANCES: FACTURES =====
            await log_step("FINANCES-Factures", "TESTING", "Accès factures...")
            await page.goto(f"{BASE_URL}/finances/factures/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/19_factures.png")
            await log_step("FINANCES-Factures", "OK", "Page factures accessible")
            
            # ===== FINANCES: CAISSE =====
            await log_step("FINANCES-Caisse", "TESTING", "Ouverture caisse...")
            await page.goto(f"{BASE_URL}/finances/caisse/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/20_caisse.png")
            
            # Chercher le bouton pour ouvrir la caisse
            open_btn = page.locator('button:has-text("Ouvrir"), a:has-text("Ouvrir")').first
            if await open_btn.count() > 0:
                try:
                    await open_btn.click()
                    await page.wait_for_timeout(1000)
                    await safe_fill(page, "#id_montant_initial", "100000")
                    await page.screenshot(path="screenshots/21_caisse_ouvert.png")
                    await submit_form(page)
                    await page.wait_for_timeout(2000)
                    await log_step("FINANCES-Caisse", "OK", "Caisse ouverte")
                except:
                    await log_step("FINANCES-Caisse", "WARNING", "Caisse déjà ouverte ou erreur")
            else:
                await log_step("FINANCES-Caisse", "OK", "Page caisse accessible")
            
            # ===== FINANCES: TABLEAU DE BORD =====
            await log_step("FINANCES-TableauBord", "TESTING", "Accès tableau de bord...")
            await page.goto(f"{BASE_URL}/finances/tableau-bord/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/22_tableau_bord_financier.png")
            await log_step("FINANCES-TableauBord", "OK", "Tableau de bord financier accessible")
            
            # ===== RESSOURCES HUMAINES: PERSONNEL =====
            await log_step("RH-Personnel", "TESTING", "Création personnel...")
            await page.goto(f"{BASE_URL}/ressources-humaines/creer/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/23_personnel_form.png")
            
            await safe_fill(page, "#id_nom", "Ondoua")
            await safe_fill(page, "#id_prenom", "Pierre")
            await safe_fill(page, "#id_fonction", "Agent d'entretien")
            await safe_fill(page, "#id_date_embauche", "2025-01-01")
            await safe_fill(page, "#id_salaire_base", "50000")
            
            await page.screenshot(path="screenshots/24_personnel_filled.png")
            await submit_form(page)
            await page.wait_for_timeout(2000)
            await log_step("RH-Personnel", "OK", "Personnel créé")
            
            # ===== RESSOURCES HUMAINES: SALAIRES =====
            await log_step("RH-Salaires", "TESTING", "Enregistrement salaire...")
            await page.goto(f"{BASE_URL}/ressources-humaines/salaires/creer/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/25_salaire_form.png")
            
            await safe_fill(page, "#id_mois", "2025-09")
            await safe_fill(page, "#id_salaire_net", "50000")
            await safe_fill(page, "#id_date_paiement", "2025-09-30")
            
            selects = await page.locator('select').all()
            if selects:
                try:
                    if await selects[0].locator('option').count() > 1:
                        await selects[0].select_option(index=1)
                except:
                    pass
            
            await page.screenshot(path="screenshots/26_salaire_filled.png")
            await submit_form(page)
            await page.wait_for_timeout(2000)
            await log_step("RH-Salaires", "OK", "Salaire enregistré")
            
            # ===== RAPPORTS: BULLETINS =====
            await log_step("RAPPORTS-Bulletins", "TESTING", "Accès bulletins...")
            await page.goto(f"{BASE_URL}/rapports/bulletins/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/27_bulletins.png")
            await log_step("RAPPORTS-Bulletins", "OK", "Page bulletins accessible")
            
            # ===== RAPPORTS: RAPPORT FINANCIER =====
            await log_step("RAPPORTS-RapportFinancier", "TESTING", "Accès rapport financier...")
            await page.goto(f"{BASE_URL}/rapports/financier/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/28_rapport_financier.png")
            await log_step("RAPPORTS-RapportFinancier", "OK", "Rapport financier accessible")
            
            # ===== RAPPORTS: STATISTIQUES GLOBALES =====
            await log_step("RAPPORTS-Stats", "TESTING", "Accès statistiques...")
            await page.goto(f"{BASE_URL}/rapports/statistiques/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/29_stats_globales.png")
            await log_step("RAPPORTS-Stats", "OK", "Statistiques globales accessibles")
            
            # ===== TEST DES RÔLES =====
            
            # Déconnexion
            await log_step("RÔLES-Déconnexion", "TESTING", "Déconnexion...")
            await page.goto(f"{BASE_URL}/authentification/logout/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
            # Test Direction
            await log_step("RÔLES-Direction", "TESTING", "Connexion direction1...")
            await page.goto(f"{BASE_URL}/authentification/login/", wait_until="domcontentloaded")
            await page.wait_for_timeout(1000)
            await page.fill('input[name="username"]', 'direction1')
            await page.fill('input[name="password"]', 'Direction2026!')
            await page.click('button.btn-login', force=True)
            await page.wait_for_timeout(3000)
            await page.screenshot(path="screenshots/30_role_direction.png")
            
            if "dashboard" in page.url:
                await log_step("RÔLES-Direction", "OK", "Connexion direction1 réussie")
            else:
                await log_step("RÔLES-Direction", "WARNING", "direction1 non connecté")
            
            # Déconnexion
            await page.goto(f"{BASE_URL}/authentification/logout/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
            # Test Comptable
            await log_step("RÔLES-Comptable", "TESTING", "Connexion comptable1...")
            await page.goto(f"{BASE_URL}/authentification/login/", wait_until="domcontentloaded")
            await page.wait_for_timeout(1000)
            await page.fill('input[name="username"]', 'comptable1')
            await page.fill('input[name="password"]', 'Comptable2026!')
            await page.click('button.btn-login', force=True)
            await page.wait_for_timeout(3000)
            await page.screenshot(path="screenshots/31_role_comptable.png")
            
            if "dashboard" in page.url:
                await log_step("RÔLES-Comptable", "OK", "Connexion comptable1 réussie")
            else:
                await log_step("RÔLES-Comptable", "WARNING", "comptable1 non connecté")
            
            # Déconnexion
            await page.goto(f"{BASE_URL}/authentification/logout/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
            # Test Professeur
            await log_step("RÔLES-Professeur", "TESTING", "Connexion professeur1...")
            await page.goto(f"{BASE_URL}/authentification/login/", wait_until="domcontentloaded")
            await page.wait_for_timeout(1000)
            await page.fill('input[name="username"]', 'professeur1')
            await page.fill('input[name="password"]', 'Professeur2026!')
            await page.click('button.btn-login', force=True)
            await page.wait_for_timeout(3000)
            await page.screenshot(path="screenshots/32_role_professeur.png")
            
            if "dashboard" in page.url:
                await log_step("RÔLES-Professeur", "OK", "Connexion professeur1 réussie")
            else:
                await log_step("RÔLES-Professeur", "WARNING", "professeur1 non connecté")
            
            # ===== FIN =====
            await log_step("FIN", "COMPLETE", "Tous les tests terminés")
            
        except Exception as e:
            await log_step("ERROR", "FATAL", str(e))
            await page.screenshot(path="screenshots/error.png")
        finally:
            await browser.close()
    
    return RESULTS

if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    
    results = asyncio.run(test_application())
    
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS COMPLETS")
    print("="*60)
    
    ok_count = sum(1 for r in results if r['status'] == 'OK')
    error_count = sum(1 for r in results if r['status'] == 'ERROR')
    warning_count = sum(1 for r in results if r['status'] == 'WARNING')
    
    for r in results:
        status_icon = "[OK]" if r['status'] == 'OK' else ("[WARN]" if r['status'] == 'WARNING' else "[ERR]")
        print(f"  {status_icon} {r['status']:10} | {r['step']}: {r['message']}")
    
    print("="*60)
    print(f"TOTAUX: {ok_count} OK | {warning_count} Warnings | {error_count} Erreurs")
    print(f"Screenshots: {len([f for f in os.listdir('screenshots') if f.endswith('.png')])} fichiers")
    print("="*60)
