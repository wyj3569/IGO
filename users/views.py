# users/views.py
from django.contrib.auth.models import User

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView

from .models import Hospital, Profile, Patient

from .serializers import HospitalREADOneSerializer, HospitalREADAllSerializer
from .serializers import RegisterSerializer, LoginSerializer
from .serializers import ProfileREADSerializer, ProfileUPDATESerializer
from .serializers import PatientCREATESerializer, PatientREADSerializer, PatientUPDATESerializer

from .utils import get_drawing_patient_position
from .utils import send_from_patient_to_doctor_by_fcm_notification
from .utils import send_from_doctor_to_patient_by_fcm_notification
from .utils import send_from_patient_to_doctor_by_fcm_data

import webbrowser


class HospitalREADAllAPIView(APIView):
    """
    병원 전체 조회
    hospital/
    """
    def get(self, request):
        hospitals = Hospital.objects.all()
        serializer = HospitalREADAllSerializer(hospitals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HospitalREADOneAPIView(APIView):
    """
    병원 1개 조회
    hospital/<int:hospital_id>/
    """
    def get(self, request, hospital_id):
        hospital = get_object_or_404(Hospital, pk=hospital_id)
        serializer = HospitalREADOneSerializer(hospital)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    """
    의료진 회원가입
    register/
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class LoginView(generics.GenericAPIView):
    """
    의료진 로그인
    login/
    """
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data  # validate()의 리턴값인 Token을 받아옴

        user = User.objects.get(username=request.data["username"])
        return Response({"token": token.key, "id": user.id}, status=status.HTTP_200_OK)


class ProfileAPIView(APIView):
    """
    의료진 프로필 조회, 의료진 프로필 수정
    doctor/<int:profile_id>/
    """
    # 의료진 프로필 조회
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, pk=profile_id)
        serializer = ProfileREADSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 의료진 프로필 수정
    def put(self, request, profile_id):
        profile = get_object_or_404(Profile, pk=profile_id)
        serializer = ProfileUPDATESerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientsAPIView(APIView):
    """
    환자 1명 생성, 환자 전체 조회
    doctor/<int:profile_id>/patient/
    """
    # 환자 1명 생성
    def post(self, request, profile_id):
        profile = get_object_or_404(Profile, user_id=profile_id)
        serializer = PatientCREATESerializer(data=request.data)
        if not serializer.is_valid():  # request 유효성 검사
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        patient = Patient(profile=profile,
                          name=request.data["name"],
                          gender=request.data["gender"],
                          age=request.data["age"],
                          blood_type=request.data["blood_type"],
                          blood_rh=request.data["blood_rh"],
                          disease=request.data["disease"],
                          extra=request.data["extra"],
                          image=request.data["image"]
                          )
        patient.save()
        return Response(data=request.data, status=status.HTTP_201_CREATED)

    # 환자 전체 조회
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, pk=profile_id)
        patients = profile.patient_set.all()
        serializer = PatientREADSerializer(patients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PatientAPIView(APIView):
    """
    환자 1명 조회, 환자 1명 수정, 환자 1명 삭제
    doctor/<int:profile_id>/patient/<int:patient_id>/
    """
    # 환자 1명 조회
    def get(self, request, profile_id, patient_id):
        profile = get_object_or_404(Profile, pk=profile_id)
        patient = get_object_or_404(Patient, pk=patient_id)
        serializer = PatientREADSerializer(patient)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 환자 1명 수정
    def put(self, request, profile_id, patient_id):
        profile = get_object_or_404(Profile, pk=profile_id)
        patient = get_object_or_404(Patient, pk=patient_id)
        serializer = PatientUPDATESerializer(data=request.data)
        if not serializer.is_valid():  # request 유효성 검사
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        patient.name = request.data["name"]
        patient.gender = request.data["gender"]
        patient.age = request.data["age"]
        patient.blood_type = request.data["blood_type"]
        patient.blood_rh = request.data["blood_rh"]
        patient.disease = request.data["disease"]
        patient.extra = request.data["extra"]
        patient.image = request.data["image"]
        patient.save()
        return Response(request.data, status=status.HTTP_200_OK)

    # 환자 1명 삭제
    def delete(self, request, profile_id, patient_id):
        profile = get_object_or_404(Profile, pk=profile_id)
        patient = get_object_or_404(Patient, pk=patient_id)
        patient.delete()
        return Response(request.data, status=status.HTTP_200_OK)


class FromPatientToServerIPAddressAPIView(APIView):
    """
    환자 -> 서버 (wifi ip 주소 보내기)
    send/ip_address/<int:patient_id>/
    """
    def post(self, request, patient_id):
        ip_address = request.data["ip_address"]
        patient = get_object_or_404(Patient, pk=patient_id)
        print(f"ip_address: {ip_address}")
        print(f"환자 ID: {patient_id}")
        print(f"환자 이름: {patient.name}")

        patient.ip_address = ip_address
        patient.save()
        return Response(request.data, status=status.HTTP_200_OK)


class FromStationToServerAPIView(APIView):
    """
    기지국 -> 서버 (거리 값)
    call/station/<int:patient_id>/
    """
    def post(self, request, patient_id):
        station = request.data["station"]  # 기지국 이름
        distance = float(request.data["real_distance"])  # 거리값
        distance = distance * 10000.0  # 예를 들어, 1.2m 값이 들어오면 12000.0으로 변환

        # 환자 조회
        patient = get_object_or_404(Patient, pk=patient_id)
        print(f"환자 ID: {patient_id}")
        print(f"환자 이름: {patient.name}")

        if station == "A":
            print(f"기지국 A가 값을 보냈습니다 : {distance}")
            patient.real_distance1 = distance
            patient.save()
        elif station == "B":
            print(f"기지국 B가 값을 보냈습니다 : {distance}")
            patient.real_distance2 = distance
            patient.save()
        elif station == "C":
            print(f"기지국 C가 값을 보냈습니다 : {distance}")
            patient.real_distance3 = distance
            patient.save()
        else:
            print("invalid station name")
            return Response("invalid station name", status=status.HTTP_400_BAD_REQUEST)

        if (patient.real_distance1 > 0) and (patient.real_distance2 > 0) and (patient.real_distance3 > 0):
            print("모든 기지국이 거리값을 보냈습니다.")
            # 환자의 의료진
            profile = patient.profile
            # 의료진의 병원
            hospital = profile.hospital
            # 도면 상에서 환자의 위치 좌표를 구하고 저장
            drawing_patient_x, drawing_patient_y = get_drawing_patient_position(
                hospital=hospital,
                real_distance=(patient.real_distance1, patient.real_distance2, patient.real_distance3)
            )
            print(f"도면 상에서 환자의 x좌표 : {drawing_patient_x}")
            print(f"도면 상에서 환자의 y좌표 : {drawing_patient_y}")
            patient.drawing_patient_x = drawing_patient_x
            patient.drawing_patient_y = drawing_patient_y

            # 환자의 실제 거리값 0으로 초기화
            patient.real_distance1 = 0.0
            patient.real_distance2 = 0.0
            patient.real_distance3 = 0.0
            patient.save()
        else:
            print("아직 모든 기지국이 거리값을 보내지 않았습니다.")
            return Response(request.data, status=status.HTTP_200_OK)

        return Response(request.data, status=status.HTTP_200_OK)


class FromPatientToDoctorAPIView(APIView):
    """
    환자 -> 서버 (의료진 호출)
    call/patient/<int:patient_id>/
    """
    def get(self, request, patient_id):
        # 환자 조회
        patient = get_object_or_404(Patient, pk=patient_id)
        # 환자의 의료진
        profile = patient.profile
        # 의료진의 병원
        hospital = profile.hospital
        print(f"환자 ID: {patient_id}")
        print(f"환자 이름: {patient.name}")
        print(f"의료진 이름: {profile.name}")
        print(f"병원 이름: {hospital.name}")

        # 도면에서 환자의 위치 좌표를 의료진 스마트폰 앱에 보냄 (FCM push message)
        drawing_patient_x = patient.drawing_patient_x
        drawing_patient_y = patient.drawing_patient_y
        print("FCM에 보낼 값")
        print(f"drawing_patient_x: {drawing_patient_x}")
        print(f"drawing_patient_y: {drawing_patient_y}")

        # FCM에 push 메시지 요청 보내기
        # notification push
        send_from_patient_to_doctor_by_fcm_notification(
            patient=patient,
            doctor=profile
        )
        # data push
        send_from_patient_to_doctor_by_fcm_data(
            patient=patient,
            doctor=profile,
            drawing_patient_x=drawing_patient_x,
            drawing_patient_y=drawing_patient_y
        )
        return Response(request.data, status=status.HTTP_200_OK)


class FromDoctorToPatientAPIView(APIView):
    """
    의료진 -> 서버 (환자 호출)
    call/doctor/patient/<int:patient_id>/
    """
    # 의료진이 자신의 id값과 환자의 id값을 보냄
    def get(self, request, patient_id):
        # 환자 조회
        patient = get_object_or_404(Patient, pk=patient_id)
        # 환자의 의료진
        profile = patient.profile
        # 의료진의 병원
        hospital = profile.hospital
        print(f"환자 ID: {patient_id}")
        print(f"환자 이름: {patient.name}")
        print(f"의료진 이름: {profile.name}")
        print(f"병원 이름: {hospital.name}")

        # 도면에서 환자의 위치 좌표를 의료진 스마트폰 앱에 보냄 (FCM push message)
        drawing_patient_x = patient.drawing_patient_x
        drawing_patient_y = patient.drawing_patient_y
        print("FCM에 보낼 값")
        print(f"drawing_patient_x: {drawing_patient_x}")
        print(f"drawing_patient_y: {drawing_patient_y}")

        # FCM에 push 메시지 요청 보내기
        # notification push
        send_from_doctor_to_patient_by_fcm_notification(doctor=profile)
        # data push
        send_from_patient_to_doctor_by_fcm_data(
            patient=patient,
            doctor=profile,
            drawing_patient_x=drawing_patient_x,
            drawing_patient_y=drawing_patient_y,
        )

        # 환자 아두이노에 피드백
        # ip = patient.ip_address
        # url = f"http://{ip}/gpio1/1"
        # webbrowser.open(url)

        return Response(request.data, status=status.HTTP_200_OK)
