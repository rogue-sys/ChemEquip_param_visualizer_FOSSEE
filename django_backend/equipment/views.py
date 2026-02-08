from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import User

from .models import Dataset
from .utils import analyze_csv
from .serializers import DatasetSerializer


# ---------- USER REGISTRATION ----------
@api_view(['POST'])
@permission_classes([AllowAny])   # 👈 THIS IS THE FIX
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {"error": "Username and password required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    User.objects.create_user(
        username=username,
        password=password
    )

    return Response(
        {"message": "User created successfully"},
        status=status.HTTP_201_CREATED
    )


# ---------- CSV UPLOAD ----------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    file = request.FILES.get('file')

    if not file:
        return Response({"error": "No file uploaded"}, status=400)

    summary = analyze_csv(file)

    Dataset.objects.create(
        user=request.user,
        filename=file.name,
        summary=summary
    )

    # Keep only last 5 datasets for this user
    datasets = Dataset.objects.filter(user=request.user).order_by('-uploaded_at')
    if datasets.count() > 5:
        for ds in datasets[5:]:
            ds.delete()

    return Response(summary)


# ---------- HISTORY ----------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def history(request):
    datasets = Dataset.objects.filter(user=request.user).order_by('-uploaded_at')[:5]
    serializer = DatasetSerializer(datasets, many=True)
    return Response(serializer.data)

# ---------- CHECK USERNAME EXISTS ----------
@api_view(['GET'])
@permission_classes([AllowAny])
def check_username(request):
    username = request.GET.get('username', '').strip()

    if not username:
        return Response(
            {"exists": False},
            status=status.HTTP_200_OK
        )

    exists = User.objects.filter(username=username).exists()

    return Response(
        {"exists": exists},
        status=status.HTTP_200_OK
    )
