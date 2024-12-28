from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):

        access_token = request.COOKIES.get('access_token')

        if not access_token:
            return None
        
        
        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
        except:
            return None
        
        return (user, validated_token)