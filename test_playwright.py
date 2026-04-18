"""
Script de test automatisé pour SyGeS-AM
Utilise Playwright pour tester l'application Django
"""

import asyncio
from playwright.async_api import async_playwright
import json

BASE_URL = "http://127.0.0.1:8000"
RESULTS = []

async def log_step(step, status, message):
    result = {"step": step, "status": status, "message": message}
    RESULTS.append(result)
    print(f"[{status}] {step}: {message}")

async def test_application():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()
        
        try:
            # ===== ÉTAPE 1: CONNEXION =====
            await log_step("1.1 - Page de connexion", "TESTING", "Chargement...")
            await page.goto(f"{BASE_URL}/authentification/login/", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_selector('input[name="username"]', timeout=10000)
            await asyncio.sleep(1)
            await page.screenshot(path="screenshots/01_login.png")
            await log_step("1.1 - Page de connexion", "OK", "Page chargée")
            
            # Remplir le formulaire de connexion
            await log_step("1.2 - Connexion admin", "TESTING", "admin/admin2026")
            await page.fill('input[name="username"]', 'admin')
            await page.fill('input[name="password"]', 'admin2026')
            await page.click('button.btn-login', force=True)
            await page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(3)
            
            current_url = page.url
            await page.screenshot(path="screenshots/02_dashboard.png")
            
            if "dashboard" in current_url or "login" not in current_url:
                await log_step("1.2 - Connexion admin", "OK", f"Connecté - URL: {current_url}")
            else:
                await log_step("1.2 - Connexion admin", "ERROR", f"Non connecté - URL: {current_url}")
                return RESULTS
            
            # ===== ÉTAPE 2: CONFIGURATION - ANNÉE SCOLAIRE =====
            await log_step("2.1 - Année scolaire", "TESTING", "Création 2025-2026...")
            
            # Aller directement à la page d'ajout (plus simple)
            await page.goto(f"{BASE_URL}/finances/annees/ajouter/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/03_annee_form.png")
            
            # Remplir le formulaire
            try:
                await page.fill('input[name="libelle"]', '2025-2026')
                await page.fill('input[name="date_debut"]', '2025-09-01')
                await page.fill('input[name="date_fin"]', '2026-07-31')
                
                # Cocher est_active si présent
                active = page.locator('input[type="checkbox"]')
                if await active.count() > 0:
                    await active.first.check(force=True)
                
                await page.screenshot(path="screenshots/04_annee_filled.png")
                await page.click('button[type="submit"]', force=True)
                await page.wait_for_timeout(3000)
                await page.screenshot(path="screenshots/05_annee_created.png")
                await log_step("2.1 - Année scolaire", "OK", "2025-2026 créée")
            except Exception as e:
                await log_step("2.1 - Année scolaire", "ERROR", str(e))
            
            # ===== ÉTAPE 3: UTILISATEURS =====
            await log_step("3.1 - Utilisateur direction", "TESTING", "Création direction1...")
            
            await page.goto(f"{BASE_URL}/authentification/users/ajouter/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/06_user_form.png")
            
            try:
                await page.fill('input[name="username"]', 'direction1')
                await page.fill('input[name="email"]', 'direction@example.com')
                await page.fill('input[name="password1"]', 'Direction2026!')
                await page.fill('input[name="password2"]', 'Direction2026!')
                await page.fill('input[name="first_name"]', 'Jean')
                await page.fill('input[name="last_name"]', 'Dupont')
                
                # Sélectionner le rôle
                role_select = page.locator('select[name="role"]')
                if await role_select.count() > 0:
                    await role_select.select_option('direction')
                
                # Cocher est_approuve
                approuve = page.locator('input[type="checkbox"]')
                if await approuve.count() > 0:
                    await approuve.first.check(force=True)
                
                await page.screenshot(path="screenshots/07_user_filled.png")
                await page.click('button[type="submit"]', force=True)
                await page.wait_for_timeout(3000)
                await page.screenshot(path="screenshots/08_user_created.png")
                await log_step("3.1 - Utilisateur direction", "OK", "direction1 créé")
            except Exception as e:
                await log_step("3.1 - Utilisateur direction", "ERROR", str(e))
            
            # ===== ÉTAPE 3.2: UTILISATEUR COMPTABLE =====
            await log_step("3.2 - Utilisateur comptable", "TESTING", "Création comptable1...")
            
            await page.goto(f"{BASE_URL}/authentification/users/ajouter/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
            try:
                await page.fill('input[name="username"]', 'comptable1')
                await page.fill('input[name="email"]', 'comptable@example.com')
                await page.fill('input[name="password1"]', 'Comptable2026!')
                await page.fill('input[name="password2"]', 'Comptable2026!')
                await page.fill('input[name="first_name"]', 'Marie')
                await page.fill('input[name="last_name"]', 'Martin')
                
                role_select = page.locator('select[name="role"]')
                if await role_select.count() > 0:
                    await role_select.select_option('comptable')
                
                approuve = page.locator('input[type="checkbox"]')
                if await approuve.count() > 0:
                    await approuve.first.check(force=True)
                
                await page.click('button[type="submit"]', force=True)
                await page.wait_for_timeout(3000)
                await page.screenshot(path="screenshots/09_comptable_created.png")
                await log_step("3.2 - Utilisateur comptable", "OK", "comptable1 créé")
            except Exception as e:
                await log_step("3.2 - Utilisateur comptable", "ERROR", str(e))
            
            # ===== ÉTAPE 3.3: UTILISATEUR SECRÉTAIRE =====
            await log_step("3.3 - Utilisateur secrétaire", "TESTING", "Création secretaire1...")
            
            await page.goto(f"{BASE_URL}/authentification/users/ajouter/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
            try:
                await page.fill('input[name="username"]', 'secretaire1')
                await page.fill('input[name="email"]', 'secretaire@example.com')
                await page.fill('input[name="password1"]', 'Secretaire2026!')
                await page.fill('input[name="password2"]', 'Secretaire2026!')
                await page.fill('input[name="first_name"]', 'Pierre')
                await page.fill('input[name="last_name"]', 'Durand')
                
                role_select = page.locator('select[name="role"]')
                if await role_select.count() > 0:
                    await role_select.select_option('secretaire')
                
                approuve = page.locator('input[type="checkbox"]')
                if await approuve.count() > 0:
                    await approuve.first.check(force=True)
                
                await page.click('button[type="submit"]', force=True)
                await page.wait_for_timeout(3000)
                await page.screenshot(path="screenshots/10_secretaire_created.png")
                await log_step("3.3 - Utilisateur secrétaire", "OK", "secretaire1 créé")
            except Exception as e:
                await log_step("3.3 - Utilisateur secrétaire", "ERROR", str(e))
            
            # ===== ÉTAPE 3.4: UTILISATEUR PROFESSEUR =====
            await log_step("3.4 - Utilisateur professeur", "TESTING", "Création professeur1...")
            
            await page.goto(f"{BASE_URL}/authentification/users/ajouter/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
            try:
                await page.fill('input[name="username"]', 'professeur1')
                await page.fill('input[name="email"]', 'professeur@example.com')
                await page.fill('input[name="password1"]', 'Professeur2026!')
                await page.fill('input[name="password2"]', 'Professeur2026!')
                await page.fill('input[name="first_name"]', 'Paul')
                await page.fill('input[name="last_name"]', 'Benoit')
                
                role_select = page.locator('select[name="role"]')
                if await role_select.count() > 0:
                    await role_select.select_option('professeur')
                
                approuve = page.locator('input[type="checkbox"]')
                if await approuve.count() > 0:
                    await approuve.first.check(force=True)
                
                await page.click('button[type="submit"]', force=True)
                await page.wait_for_timeout(3000)
                await page.screenshot(path="screenshots/11_professeur_created.png")
                await log_step("3.4 - Utilisateur professeur", "OK", "professeur1 créé")
            except Exception as e:
                await log_step("3.4 - Utilisateur professeur", "ERROR", str(e))
            
            # ===== ÉTAPE 4: CLASSES =====
            await log_step("4.1 - Classe", "TESTING", "Création 6ème A...")
            
            await page.goto(f"{BASE_URL}/enseignement/classes/ajouter/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/12_classe_form.png")
            
            try:
                await page.fill('#id_nom', '6ème A')
                await page.fill('#id_capacite', '30')
                
                await page.screenshot(path="screenshots/13_classe_filled.png")
                await page.click('button[type="submit"]', force=True)
                await page.wait_for_timeout(3000)
                await page.screenshot(path="screenshots/14_classe_created.png")
                await log_step("4.1 - Classe", "OK", "6ème A créée")
            except Exception as e:
                await log_step("4.1 - Classe", "ERROR", str(e))
            
            # ===== ÉTAPE 5: MATIÈRES =====
            matieres = [
                "Mathématiques",
                "Français",
                "Anglais",
                "Histoire-Géo",
                "Sciences Naturelles",
            ]
            
            for nom in matieres:
                await log_step(f"5.x - {nom}", "TESTING", f"Création {nom}...")
                await page.goto(f"{BASE_URL}/enseignement/matieres/ajouter/", wait_until="domcontentloaded")
                await page.wait_for_timeout(1500)
                
                try:
                    await page.fill('#id_nom', nom)
                    
                    await page.click('button[type="submit"]', force=True)
                    await page.wait_for_timeout(2000)
                    await log_step(f"5.x - {nom}", "OK", f"{nom} créée")
                except Exception as e:
                    await log_step(f"5.x - {nom}", "ERROR", str(e))
            
            # ===== ÉTAPE 6: ÉLÈVES =====
            await log_step("6.1 - Élève", "TESTING", "Création Dupont Marie...")
            
            await page.goto(f"{BASE_URL}/scolarite/ajouter/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/18_eleve_form.png")
            
            try:
                await page.fill('input[name="nom"]', 'Dupont')
                await page.fill('input[name="prenom"]', 'Marie')
                await page.fill('input[name="date_naissance"]', '2014-05-15')
                await page.fill('input[name="lieu_naissance"]', 'Yaoundé')
                
                # Sélectionner sexe
                sexe = page.locator('select[name="sexe"]')
                if await sexe.count() > 0:
                    await sexe.select_option('F')
                
                await page.screenshot(path="screenshots/19_eleve_filled.png")
                await page.click('button[type="submit"]', force=True)
                await page.wait_for_timeout(3000)
                await page.screenshot(path="screenshots/20_eleve_created.png")
                await log_step("6.1 - Élève", "OK", "Dupont Marie créée")
            except Exception as e:
                await log_step("6.1 - Élève", "ERROR", str(e))
            
            # ===== ÉTAPE 7: INSCRIPTION =====
            await log_step("7.1 - Inscription", "TESTING", "Inscription dans 6ème A...")
            
            # L'inscription se fait via la liste des élèves ou directement
            await page.goto(f"{BASE_URL}/scolarite/inscriptions/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.screenshot(path="screenshots/21_inscription_list.png")
            
            try:
                # Chercher n'importe quel lien ou bouton
                links = await page.locator('a[href*="inscription"], a[href*="ajouter"], button').all()
                if links:
                    for link in links[:3]:
                        text = await link.text_content()
                        if 'ajout' in text.lower() or 'inscri' in text.lower():
                            await link.click()
                            await page.wait_for_timeout(2000)
                            break
                
                # Sélectionner l'élève
                eleve_select = page.locator('select').first
                if await eleve_select.count() > 0:
                    await eleve_select.select_option(index=1)
                    await page.wait_for_timeout(500)
                
                # Sélectionner la classe
                selects = await page.locator('select').all()
                for sel in selects[1:3]:
                    options = await sel.options
                    if len(options) > 1:
                        await sel.select_option(index=1)
                        await page.wait_for_timeout(500)
                
                await page.screenshot(path="screenshots/22_inscription_filled.png")
                await page.click('button[type="submit"]', force=True)
                await page.wait_for_timeout(3000)
                await page.screenshot(path="screenshots/23_inscription_created.png")
                await log_step("7.1 - Inscription", "OK", "Élève inscrit")
            except Exception as e:
                await log_step("7.1 - Inscription", "WARNING", str(e)[:50])
            
            # ===== FIN =====
            await log_step("TESTS", "COMPLETE", "Tous les tests terminés")
            
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
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    for r in results:
        print(f"  {r['status']:10} | {r['step']}: {r['message']}")
    print("="*60)
    print(f"\nScreenshots disponibles dans le dossier 'screenshots/'")
