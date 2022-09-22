# users/utils.py
from firebase_admin import messaging
from .models import Patient, Profile, Hospital
from math import pow


def get_drawing_patient_position(hospital: Hospital, real_distance: tuple) -> tuple:
    """
    :param hospital: 병원
    :param real_distance: 환자와 기지국 사이의 거리값 3개
    :return: 도면 상에서 환자의 좌표
    """
    # 병원 도면 정보
    drawing_x, drawing_y = hospital.drawing_x, hospital.drawing_y
    # 실제 병원 정보
    real_x, real_y = hospital.real_x, hospital.real_y
    # 실제 병원에서 기지국의 위치
    real_station1_x, real_station1_y = hospital.real_station1_x, hospital.real_station1_y
    real_station2_x, real_station2_y = hospital.real_station2_x, hospital.real_station2_y
    real_station3_x, real_station3_y = hospital.real_station3_x, hospital.real_station3_y

    # 실제 병원에서 환자의 위치 (polypoint 알고리즘)
    real_patient_x, real_patient_y = polypoint(
        real_x=real_x,
        real_y=real_y,
        real_distance=real_distance,
        real_station1=(real_station1_x, real_station1_y),
        real_station2=(real_station2_x, real_station2_y),
        real_station3=(real_station3_x, real_station3_y),
    )
    # 병원 도면에서 환자의 위치 (비례식)
    try:
        drawing_patient_x = (drawing_x * real_patient_x) / real_x
        drawing_patient_y = (drawing_y * real_patient_y) / real_y
    except ZeroDivisionError as error:
        print(error)
        drawing_patient_x, drawing_patient_y = 0, 0

    return drawing_patient_x, drawing_patient_y


def polypoint(real_x, real_y, real_distance: tuple, real_station1: tuple, real_station2: tuple,
              real_station3: tuple) -> tuple:
    """
    :param real_distance: 환자와 기지국 사이의 실제 거리값 3개
    :param real_station1: 실제 기지국 A의 좌표
    :param real_station2: 실제 기지국 B의 좌표
    :param real_station3: 실제 기지국 C의 좌표
    :return: 실제 환자의 좌표
    """
    # 환자와 기지국 사이의 실제 거리값 3개
    r1, r2, r3 = real_distance
    # 실제 기지국 A, B, C의 좌표
    x1, y1 = real_station1
    x2, y2 = real_station2
    x3, y3 = real_station3

    A = float(2 * (x2 - x1))
    B = float(2 * (y2 - y1))
    C = float(pow(r1, 2.0) - pow(r2, 2.0) - pow(x1, 2.0) + pow(x2, 2.0) - pow(y1, 2.0) + pow(y2, 2.0))
    D = float(2 * (x3 - x2))
    E = float(2 * (y3 - y2))
    F = float(pow(r2, 2.0) - pow(r3, 2.0) - pow(x2, 2.0) + pow(x3, 2.0) - pow(y2, 2.0) + pow(y3, 2.0))

    try:
        x = (F * B - E * C) / (B * D - E * A)
        y = (F * A - D * C) / (A * E - D * B)
    except ZeroDivisionError as error:
        print(error)
        x, y = 0, 0

    if x <= 0:
        x = 0
    if x >= real_x:
        x = real_x
    if y <= 0:
        y = 0
    if x >= real_y:
        y = real_y

    return x, y


def send_from_patient_to_doctor_by_fcm_notification(patient: Patient, doctor: Profile):
    """
    FCM 서버에 notification message 요청을 보내는 함수
    환자 -> 의료진 호출
    :param patient: 환자
    :param doctor: 의료진
    :return: none
    """
    registration_token = f'{doctor.token}'
    print(f"registration_token : {registration_token}")

    message = messaging.Message(
        notification=messaging.Notification(
            title='환자의 호출',
            body=f'{patient.name} 선생님, {doctor.name} 환자가 호출했습니다',
        ),
        token=registration_token,
    )
    response = messaging.send(message)
    print('Successfully sent notification message (환자->의료진) : ', response)


def send_from_doctor_to_patient_by_fcm_notification(doctor: Profile):
    """
    FCM 서버에 notification message 요청을 보내는 함수
    의료진 -> 환자 호출 시
    :return: none
    """
    registration_token = f'{doctor.token}'
    print(f"registration_token : {registration_token}")

    message_noti = messaging.Message(
        notification=messaging.Notification(
            title='호출한 환자의 위치 정보',
            body='호출한 환자의 위치 정보를 보려면 클릭하세요',
        ),
        token=registration_token,
    )
    response = messaging.send(message_noti)
    print('Successfully sent notification message (의료진->환자) : ', response)


def send_from_patient_to_doctor_by_fcm_data(patient: Patient, doctor: Profile, drawing_patient_x, drawing_patient_y):
    """
    FCM 서버에 data message 요청을 보내는 함수
    :param drawing_patient_x: 도면 상에서 환자의 x좌표
    :param drawing_patient_y: 도면 상에서 환자의 y좌표
    :param patient: 환자
    :return: none
    """
    registration_token = f'{doctor.token}'
    print(f"registration_token : {registration_token}")

    message_data = messaging.Message(
        data={
            "id": f"{patient.id}",
            "name": f"{patient.name}",
            "image": f"{patient.image}",
            "x": f"{drawing_patient_x}",
            "y": f"{drawing_patient_y}"
        },
        token=registration_token,
    )
    response = messaging.send(message_data)
    print('Successfully sent data message : ', response)
