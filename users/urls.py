# users/urls.py
from django.urls import path

from .views import RegisterView, LoginView, ProfileAPIView
from .views import PatientsAPIView, PatientAPIView
from .views import HospitalREADAllAPIView, HospitalREADOneAPIView
from .views import FromPatientToServerIPAddressAPIView, FromStationToServerAPIView
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

    # 환자 -> 서버 (wifi ip 주소 보내기)
    path('send/ip_address/<int:patient_id>/', FromPatientToServerIPAddressAPIView.as_view()),
    # 기지국 -> 서버 (거리 값)
    path('send/station/<int:patient_id>/', FromStationToServerAPIView.as_view()),

    # 환자 -> 서버 (의료진 호출)
    path('call/patient/<int:patient_id>/', FromPatientToDoctorAPIView.as_view()),
    # 의료진 -> 서버 (환자 호출)
    path('call/doctor/patient/<int:patient_id>/', FromDoctorToPatientAPIView.as_view()),
]
