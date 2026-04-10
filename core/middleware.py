class ActiveAnneeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from finances.models import AnneeScolaire
        
        request.annee_active = None
        
        try:
            selected_annee_id = request.session.get('annee_scolaire_id') if hasattr(request, 'session') else None
        except Exception:
            selected_annee_id = None
        
        if selected_annee_id:
            try:
                request.annee_active = AnneeScolaire.objects.filter(pk=selected_annee_id).first()
            except Exception:
                pass
        
        if not request.annee_active:
            try:
                request.annee_active = AnneeScolaire.objects.filter(est_active=True).first()
            except Exception:
                pass
        
        response = self.get_response(request)
        return response


class SessionTimeoutMiddleware:
    SESSION_TIMEOUT_SECONDS = 300
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            from django.utils import timezone
            from datetime import timedelta
            
            last_activity = request.session.get('last_activity')
            timeout = timedelta(seconds=self.SESSION_TIMEOUT_SECONDS)
            now = timezone.now()
            
            if last_activity:
                last_activity_dt = timezone.datetime.fromisoformat(last_activity)
                if timezone.is_naive(last_activity_dt):
                    last_activity_dt = timezone.make_aware(last_activity_dt)
                if now - last_activity_dt > timeout:
                    from django.contrib.auth import logout
                    from django.shortcuts import redirect
                    logout(request)
                    return redirect('accounts:login')
            
            request.session['last_activity'] = now.isoformat()
            request.session.modified = True
        
        response = self.get_response(request)
        return response
