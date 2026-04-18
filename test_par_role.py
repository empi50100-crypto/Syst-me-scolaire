"""
Script de test par RÔLE pour SyGeS-AM
Teste les permissions et fonctionnalités de chaque type d'utilisateur
"""

import asyncio
from playwright.async_api import async_playwright
import json

BASE_URL = "http://127.0.0.1:8000"
RESULTS = {}

async def log_step(role, step, status, message):
    if role not in RESULTS:
        RESULTS[role] = []
    result = {"step": step, "status": status, "message": message}
    RESULTS[role].append(result)
    print(f"[{role:12}] [{status:6}] {step}: {message}")

async def login(page, username, password):
    """Connexion"""
    await page.goto(f"{BASE_URL}/authentification/login/", wait_until="domcontentloaded")
    await page.wait_for_timeout(1000)
    await page.fill('input[name="username"]', username)
    await page.fill('input[name="password"]', password)
    await page.click('button.btn-login', force=True)
    await page.wait_for_timeout(3000)
    return "dashboard" in page.url

async def logout(page):
    """Déconnexion"""
    await page.goto(f"{BASE_URL}/authentification/logout/", wait_until="domcontentloaded")
    await page.wait_for_timeout(1500)

async def test_role(role_name, username, password, pages_to_test, screenshot_prefix):
    """Teste un rôle spécifique"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()
        
        try:
            # Connexion
            await log_step(role_name, "Connexion", "TEST", f"{username}...")
            success = await login(page, username, password)
            
            if success:
                await log_step(role_name, "Connexion", "OK", f"{username} connecte")
                await page.screenshot(path=f"screenshots/{screenshot_prefix}_dashboard.png")
            else:
                await log_step(role_name, "Connexion", "ERROR", f"{username} echec connexion")
                await browser.close()
                return
            
            # Tester chaque page
            for page_name, url in pages_to_test.items():
                await log_step(role_name, page_name, "TEST", f"Acces {url}...")
                try:
                    response = await page.goto(f"{BASE_URL}{url}", wait_until="domcontentloaded", timeout=15000)
                    await page.wait_for_timeout(1500)
                    
                    # Vérifier le code de réponse
                    if response and response.status < 400:
                        # Vérifier qu'il n'y a pas d'erreur de permission
                        page_content = await page.content()
                        if "permission" not in page_content.lower() or "access" not in page_content.lower():
                            await page.screenshot(path=f"screenshots/{screenshot_prefix}_{page_name}.png")
                            await log_step(role_name, page_name, "OK", f"Accessible")
                        else:
                            await page.screenshot(path=f"screenshots/{screenshot_prefix}_{page_name}_restricted.png")
                            await log_step(role_name, page_name, "WARN", f"Page restreinte")
                    else:
                        await log_step(role_name, page_name, "ERROR", f"Erreur {response.status}")
                        
                except Exception as e:
                    await log_step(role_name, page_name, "ERROR", str(e)[:50])
            
            # Déconnexion
            await logout(page)
            await log_step(role_name, "Deconnexion", "OK", "Deconnecte")
            
        except Exception as e:
            await log_step(role_name, "FATAL", "ERROR", str(e))
        finally:
            await browser.close()

async def test_all_roles():
    """Teste tous les rôles"""
    
    # Configuration des rôles et leurs pages accessibles
    roles_config = {
        "ADMIN": {
            "username": "admin",
            "password": "admin2026",
            "prefix": "admin",
            "pages": {
                # Core
                "Core-Dashboard": "/dashboard/",
                "Core-Niveaux": "/core/niveaux/",
                "Core-Cycles": "/core/cycles/",
                "Core-Periodes": "/core/periodes/",
                # Authentification
                "Auth-Users": "/authentification/users/",
                "Auth-Notifications": "/authentification/notifications/",
                # Enseignement
                "Ens-Classses": "/enseignement/classes/",
                "Ens-Matieres": "/enseignement/matieres/",
                "Ens-Professeurs": "/enseignement/professeurs/",
                "Ens-Attributions": "/enseignement/attributions/",
                "Ens-Examens": "/enseignement/examens/",
                # Scolarité
                "Scol-Eleves": "/scolarite/",
                "Scol-Inscriptions": "/scolarite/inscriptions/",
                "Scol-Discipline": "/scolarite/discipline/",
                # Présences
                "Pres-Liste": "/presences/",
                "Pres-Stats": "/presences/statistiques/",
                # Finances
                "Fin-Frais": "/finances/frais/",
                "Fin-Paiements": "/finances/paiements/",
                "Fin-Caisse": "/finances/caisse/",
                "Fin-Factures": "/finances/factures/",
                "Fin-TableauBord": "/finances/tableau-bord/",
                # RH
                "RH-Personnel": "/ressources-humaines/",
                "RH-Salaires": "/ressources-humaines/salaires/",
                # Rapports
                "Rap-Bulletins": "/rapports/bulletins/",
                "Rap-Financier": "/rapports/financier/",
                "Rap-Stats": "/rapports/statistiques/",
            }
        },
        "DIRECTION": {
            "username": "direction1",
            "password": "Direction2026!",
            "prefix": "direction",
            "pages": {
                "Dir-Dashboard": "/dashboard/",
                "Dir-Niveaux": "/core/niveaux/",
                "Dir-Classes": "/enseignement/classes/",
                "Dir-Eleves": "/scolarite/",
                "Dir-Examens": "/enseignement/examens/",
                "Dir-Presences": "/presences/",
                "Dir-Rapports": "/rapports/bulletins/",
            }
        },
        "COMPTABLE": {
            "username": "comptable1",
            "password": "Comptable2026!",
            "prefix": "comptable",
            "pages": {
                "Cpt-Dashboard": "/dashboard/",
                "Cpt-Frais": "/finances/frais/",
                "Cpt-Paiements": "/finances/paiements/",
                "Cpt-Caisse": "/finances/caisse/",
                "Cpt-Factures": "/finances/factures/",
                "Cpt-RapportFin": "/rapports/financier/",
            }
        },
        "SECRETAIRE": {
            "username": "secretaire1",
            "password": "Secretaire2026!",
            "prefix": "secretaire",
            "pages": {
                "Sec-Dashboard": "/dashboard/",
                "Sec-Eleves": "/scolarite/",
                "Sec-Inscriptions": "/scolarite/inscriptions/",
                "Sec-Discipline": "/scolarite/discipline/",
                "Sec-Presences": "/presences/",
            }
        },
        "PROFESSEUR": {
            "username": "professeur1",
            "password": "Professeur2026!",
            "prefix": "professeur",
            "pages": {
                "Prof-Dashboard": "/dashboard/",
                "Prof-MesClasses": "/presences/mes-seances/",
                "Prof-SaisieNotes": "/enseignement/saisie-notes/",
                "Prof-Examens": "/enseignement/examens/",
            }
        }
    }
    
    # Exécuter les tests pour chaque rôle
    for role_name, config in roles_config.items():
        await test_role(
            role_name,
            config["username"],
            config["password"],
            config["pages"],
            config["prefix"]
        )

if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)
    
    asyncio.run(test_all_roles())
    
    # Résumé
    print("\n" + "="*80)
    print("RAPPORT DE TEST PAR ROLE - SyGeS-AM")
    print("="*80)
    
    for role, results in RESULTS.items():
        ok_count = sum(1 for r in results if r['status'] == 'OK')
        error_count = sum(1 for r in results if r['status'] == 'ERROR')
        warn_count = sum(1 for r in results if r['status'] == 'WARN')
        
        print(f"\n{'='*40}")
        print(f"ROLE: {role}")
        print(f"{'='*40}")
        for r in results:
            status = "OK" if r['status'] == 'OK' else ("WARN" if r['status'] == 'WARN' else "ERR")
            print(f"  [{status:4}] {r['step']}: {r['message']}")
        print(f"  --- Total: {ok_count} OK | {warn_count} WARN | {error_count} ERR")
    
    print("\n" + "="*80)
    print("Tests terminés. Screenshots disponibles dans 'screenshots/'")
    print("="*80)
