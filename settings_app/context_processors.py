"""
Context processor qui rend les préférences utilisateur disponibles
dans tous les templates (thème, police, couleur d'accent).
"""

from settings_app.models import UserPreference


def user_preferences(request):
    """Injecte les préférences de l'utilisateur dans le contexte."""
    if request.user.is_authenticated:
        try:
            prefs = request.user.preferences
        except UserPreference.DoesNotExist:
            prefs = UserPreference.objects.create(user=request.user)
        return {
            'user_theme': prefs.theme,
            'user_font': prefs.font,
            'user_accent': prefs.accent_hex,
            'user_accent_h': prefs.accent_hover_hex,
        }
    return {
        'user_theme': 'light',
        'user_font': 'Inter',
        'user_accent': '#6B8F71',
        'user_accent_h': '#5A7D60',
    }
