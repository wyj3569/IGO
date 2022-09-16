# users/urls.py
from django.urls import path
from .views import RegisterView, LoginView, ProfileAPIView
from .views import PatientsAPIView, PatientAPIView
from .views import HospitalREADAllAPIView, HospitalREADOneAPIView
from .views import FromStation1APIView, FromStation2APIView, FromStation3APIView, FromStation4APIView
from .views import FromPatientToDoctorAPIView, FromDoctorToPatientAPIView

urlpatterns = [
    # 병원 전체 조회
    path('hospital/', HospitalREADAllAPIView.as_view()),
    # 병원 1개 조회
    path('hospital/<int:hospital_id>/', HospitalREADOneAPIView.as_view()),

    # 의료진 회원가입
    path('register/', RegisterView.as_view()),
    # 의료진 로그인
    path('login/', LoginView.as_view()),
    # 의료진 프로필 조회, 의료진 프로필 수정
    path('doctor/<int:profile_id>/', ProfileAPIView.as_view()),

    # 환자 1명 생성, 환자 전체 조회
    path('doctor/<int:profile_id>/patient/', PatientsAPIView.as_view()),
    # 환자 1명 조회, 환자 1명 수정, 환자 1명 삭제
    path('doctor/<int:profile_id>/patient/<int:patient_id>/', PatientAPIView.as_view()),

    # 기지국 1에서 환자와의 거리 정보 받기
    path('call/patient/<int:patient_id>/from1/', FromStation1APIView.as_view()),
    # 기지국 2에서 환자와의 거리 정보 받기
    path('call/patient/<int:patient_id>/from2/', FromStation2APIView.as_view()),
    # 기지국 3에서 환자와의 거리 정보 받기
    path('call/patient/<int:patient_id>/from3/', FromStation3APIView.as_view()),
    # 기지국 4에서 환자와의 거리 정보 받기
    path('call/patient/<int:patient_id>/from4/', FromStation4APIView.as_view()),

    # 환자가 의료진 호출
    path('call/patient/<int:patient_id>/', FromPatientToDoctorAPIView.as_view()),
    # 의료진이 환자 호출
    path('call/doctor/<int:doctor_id>/patient/<int:patient_id>/', FromDoctorToPatientAPIView.as_view()),
]
