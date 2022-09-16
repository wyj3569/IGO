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

from .utils import get_drawing_patient_position, send_from_patient_to_doctor_by_fcm


# 병원 전체 조회
# hospital/
class HospitalREADAllAPIView(APIView):
    def get(self, request):
        hospitals = Hospital.objects.all()
        serializer = HospitalREADAllSerializer(hospitals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 병원 1개 조회
# hospital/<int:hospital_id>/
class HospitalREADOneAPIView(APIView):
    def get(self, request, hospital_id):
        hospital = get_object_or_404(Hospital, pk=hospital_id)
        serializer = HospitalREADOneSerializer(hospital)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 의료진 회원가입
# register/
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


# 의료진 로그인
# login/
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data  # validate()의 리턴값인 Token을 받아옴

        user = User.objects.get(username=request.data["username"])
        return Response({"token": token.key, "id": user.id}, status=status.HTTP_200_OK)


# 의료진 프로필 조회, 의료진 프로필 수정
# doctor/<int:profile_id>/
class ProfileAPIView(APIView):
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


# 환자 1명 생성, 환자 전체 조회
# doctor/<int:profile_id>/patient/
class PatientsAPIView(APIView):
    # 환자 1명 생성
    def post(self, request, profile_id):
        profile = get_object_or_404(Profile, user_id=profile_id)
        serializer = PatientCREATESerializer(data=request.data)
        if not serializer.is_valid():  # request 유효성 검사
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        patient = Patient(profile=profile,
                          name=request.data['name'],
                          gender=request.data['gender'],
                          age=request.data['age'],
                          blood_type=request.data['blood_type'],
                          blood_rh=request.data['blood_rh'],
                          disease=request.data['disease'],
                          extra=request.data['extra'],
                          image=request.data['image']
                          )
        patient.save()

        return Response(data=request.data, status=status.HTTP_201_CREATED)

    # 환자 전체 조회
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, pk=profile_id)
        patients = profile.patient_set.all()
        serializer = PatientREADSerializer(patients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 환자 1명 조회, 환자 1명 수정, 환자 1명 삭제
# doctor/<int:profile_id>/patient/<int:patient_id>/
class PatientAPIView(APIView):
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

        patient.name = request.data['name']
        patient.gender = request.data['gender']
        patient.age = request.data['age']
        patient.blood_type = request.data['blood_type']
        patient.blood_rh = request.data['blood_rh']
        patient.disease = request.data['disease']
        patient.extra = request.data['extra']
        patient.image = request.data['image']
        patient.save()
        return Response(request.data, status=status.HTTP_200_OK)

    # 환자 1명 삭제
    def delete(self, request, profile_id, patient_id):
        profile = get_object_or_404(Profile, pk=profile_id)
        patient = get_object_or_404(Patient, pk=patient_id)
        patient.delete()
        return Response(request.data, status=status.HTTP_200_OK)


# 기지국 1에서 환자와의 거리 정보 받기 (아두이노 -> 서버)
# call/patient/<int:patient_id>/from1/
class FromStation1APIView(APIView):
    def post(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id)
        print("환자 이름 : ", patient.name)
        print("기지국 1번과의 거리 : ", request.data["real_distance1"])
        patient.real_distance1 = float(request.data["real_distance1"])
        patient.save()
        return Response(request.data, status=status.HTTP_200_OK)


# 기지국 2에서 환자와의 거리 정보 받기 (아두이노 -> 서버)
# call/patient/<int:patient_id>/from2/
class FromStation2APIView(APIView):
    def post(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id)
        print("환자 이름 : ", patient.name)
        print("기지국 2번과의 거리 : ", request.data['real_distance2'])
        patient.real_distance2 = request.data['real_distance2']
        patient.save()
        return Response(request.data, status=status.HTTP_200_OK)


# 기지국 3에서 환자와의 거리 정보 받기 (아두이노 -> 서버)
# call/patient/<int:patient_id>/from3/
class FromStation3APIView(APIView):
    def post(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id)
        print("환자 이름 : ", patient.name)
        print("기지국 3번과의 거리 : ", request.data['real_distance3'])
        patient.real_distance3 = request.data['real_distance3']
        patient.save()
        return Response(request.data, status=status.HTTP_200_OK)


# 기지국 4에서 환자와의 거리 정보 받기 (아두이노 -> 서버)
# call/patient/<int:patient_id>/from4/
class FromStation4APIView(APIView):
    def post(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id)
        print("환자 이름 : ", patient.name)
        print("기지국 4번과의 거리 : ", request.data['real_distance4'])
        patient.real_distance4 = request.data['real_distance4']
        patient.save()
        return Response(request.data, status=status.HTTP_200_OK)


# # 환자가 의료진 호출 (라즈베리파이 -> 서버)
# # call/patient/<int:patient_id>/
# class FromPatientToDoctorAPIView(APIView):
#     def get(self, request, patient_id):
#         # 환자 조회
#         patient = get_object_or_404(Patient, pk=patient_id)
#         print(f"환자 id: {patient_id}")
#         print(f"환자 이름: {patient.name}")
#         # 환자의 의료진 조회
#         profile = patient.profile
#         print(f"의료진 이름: {profile.name}")
#         # 의료진의 병원 조회
#         hospital = profile.hospital
#         print(f"병원 이름: {hospital.name}")
#
#         # 환자와 기지국 사이의 실제 거리 값 4개
#         real_distance1 = patient.real_distance1
#         real_distance2 = patient.real_distance2
#         real_distance3 = patient.real_distance3
#         real_distance4 = patient.real_distance4
#         print(f"거리1: {real_distance1}")
#         print(f"거리2: {real_distance2}")
#         print(f"거리3: {real_distance3}")
#         print(f"거리4: {real_distance4}")
#
#         # 도면 상에서 환자의 위치
#         drawing_patient_x, drawing_patient_y = get_drawing_patient_position(
#             hospital=hospital,
#             real_distance=(real_distance1, real_distance2, real_distance3, real_distance4)
#         )
#
#         # FCM에 push 메시지 요청 보내기
#         send_from_patient_to_doctor_by_fcm(
#             drawing_patient_x=drawing_patient_x,
#             drawing_patient_y=drawing_patient_y,
#             patient_info=patient,
#             doctor_info=profile
#         )
#         return Response(request.data, status=status.HTTP_200_OK)


# 환자가 의료진 호출 (라즈베리파이 -> 서버)
# call/patient/<int:patient_id>/
class FromPatientToDoctorAPIView(APIView):

    print("들어감")
    def __init__(self):
        print("생성자 실행")
        self.check_if_post = [False, False, False, False]
        self.real_distances = [0.0, 0.0, 0.0, 0.0]
        print("생성자 종료")
    print("나옴")

    def post(self, request, patient_id):  # 일단 patient_id는 1로 고정
        station = request.data["station"]
        distance = float(request.data["real_distance"])

        print("start")
        print("before")
        print(station, distance, sep="/")
        print(self.check_if_post)
        print(self.real_distances)

        if station == "A":
            self.check_if_post[0] = True
            self.real_distances[0] = distance
        elif station == "B":
            self.check_if_post[1] = True
            self.real_distances[1] = distance
        elif station == "C":
            self.check_if_post[2] = True
            self.real_distances[2] = distance
        elif station == "D":
            self.check_if_post[3] = True
            self.real_distances[3] = distance
        else:
            return Response("invalid station name", status=status.HTTP_400_BAD_REQUEST)

        print("after")
        print(self.check_if_post)
        print(self.real_distances)
        print("end")

        if self.check_if_post[0] and \
                self.check_if_post[1] and \
                self.check_if_post[2] and \
                self.check_if_post[3]:
            print("모든 기지국이 거리값을 보냄")
            print(self.check_if_post)
            print(self.real_distances)

            # 환자 조회
            patient = get_object_or_404(Patient, pk=patient_id)
            print(f"환자 id: {patient_id}")
            print(f"환자 이름: {patient.name}")
            # 환자의 의료진 조회
            profile = patient.profile
            print(f"의료진 이름: {profile.name}")
            # 의료진의 병원 조회
            hospital = profile.hospital
            print(f"병원 이름: {hospital.name}")

            # 도면 상에서 환자의 위치
            drawing_patient_x, drawing_patient_y = get_drawing_patient_position(
                hospital=hospital,
                real_distance=(
                    self.real_distances[0],
                    self.real_distances[1],
                    self.real_distances[2],
                    self.real_distances[3])
            )
            print("FCM에 넣을 값")
            print("drawing_patient_x: ", drawing_patient_x)
            print("drawing_patient_y: ", drawing_patient_y)
            # # FCM에 push 메시지 요청 보내기
            # send_from_patient_to_doctor_by_fcm(
            #     drawing_patient_x=drawing_patient_x,
            #     drawing_patient_y=drawing_patient_y,
            #     patient_info=patient,
            #     doctor_info=profile
            # )

            self.check_if_post = [False, False, False, False]
            self.real_distances = [0.0, 0.0, 0.0, 0.0]
        else:
            print("아직 모든 기지국이 값을 보내지 않음")
            return Response(request.data, status=status.HTTP_200_OK)

        return Response(request.data, status=status.HTTP_200_OK)


# 의료진이 환자 호출
# call/doctor/<int:doctor_id>/patient/<int:patient_id>/
class FromDoctorToPatientAPIView(APIView):
    # 의료진이 자신의 id값과 환자의 id값을 보냄
    def post(self, request, doctor_id, patient_id):
        print(f"의료진 id: {doctor_id}")
        print(f"환자 id: {patient_id}")
        print(f"메시지: {request.data['message']}")
        return Response(request.data, status=status.HTTP_200_OK)
