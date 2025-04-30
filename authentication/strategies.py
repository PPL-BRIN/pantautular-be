from rest_framework.response import Response
from rest_framework import status

class LoginResponseStrategy:
    def handle_response(self, tokens):
        pass

class SuccessfulLoginStrategy(LoginResponseStrategy):
    def handle_response(self, tokens):
        return Response(
            {
                "detail": "Login successful",
                "access_token": tokens["access_token"]
            },
            status=status.HTTP_200_OK
        )

class LockedAccountStrategy(LoginResponseStrategy):
    def handle_response(self, tokens):
        return Response(
            {"detail": tokens['message']},
            status=status.HTTP_423_LOCKED
        )

class InvalidCredentialsStrategy(LoginResponseStrategy):
    def handle_response(self, tokens):
        return Response(
            {"detail": "Invalid email or password"},
            status=status.HTTP_401_UNAUTHORIZED
        )