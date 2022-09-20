# users/utils.py
from firebase_admin import messaging
from .models import Patient, Profile, Hospital


# hospital : 병원 정보
# real_distance : 환자와 기지국 사이의 거리 값 3개 tuple
def get_drawing_patient_position(hospital: Hospital, real_distance: tuple) -> tuple:
    # 병원 도면 정보
    drawing_x, drawing_y = hospital.drawing_x, hospital.drawing_y  # 병원 도면 크기
    # 실제 병원 정보
    real_x, real_y = hospital.real_x, hospital.real_y  # 실제 병원 크기
    # 실제 병원에서 기지국의 위치
    real_station1_x, real_station1_y = hospital.real_station1_x, hospital.real_station1_y
    real_station2_x, real_station2_y = hospital.real_station2_x, hospital.real_station2_y
    real_station3_x, real_station3_y = hospital.real_station3_x, hospital.real_station3_y

    # 실제 병원에서 환자의 위치 (polypoint 알고리즘으로 구해야 함)
    real_patient_x, real_patient_y = polypoint(
        real_distance=real_distance,
        real_station1=(real_station1_x, real_station1_y),
        real_station2=(real_station2_x, real_station2_y),
        real_station3=(real_station3_x, real_station3_y),
    )
    print("실제 환자의 위치")
    print("x 좌표 : ", real_patient_x)
    print("y 좌표 : ", real_patient_y)

    # 병원 도면에서 환자의 위치 (비례식으로 구함, return value)
    drawing_patient_x = (drawing_x * real_patient_x) / real_x
    drawing_patient_y = (drawing_y * real_patient_y) / real_y
    print("도면 상에서 환자의 위치")
    print("x 좌표 : ", drawing_patient_x)
    print("y 좌표 : ", drawing_patient_y)

    return drawing_patient_x, drawing_patient_y


# 삼변측량을 이용해서 real_patient_x, real_patient_y 값을 구한다
# real_distance : 환자와 기지국 사이의 거리 값 3개 tuple
# real_stationN : 실제 병원에서 N번째 기지국의 좌표 tuple
def polypoint(real_distance: tuple,
              real_station1: tuple,
              real_station2: tuple,
              real_station3: tuple,) -> tuple:
    # 환자와 기지국 사이의 실제 거리들 r1, r2, r3, r4
    real_distance1, real_distance2, real_distance3 = real_distance
    # 실제 병원에서 기지국 위치
    real_station1_x, real_station1_y = real_station1  # (x1, y1)
    real_station2_x, real_station2_y = real_station2  # (x2, y2)
    real_station3_x, real_station3_y = real_station3  # (x3, y3)

    A = float(2 * (real_station2_x - real_station1_x))
    B = float(2 * (real_station2_y - real_station1_y))
    C = float(real_distance1**2 - real_distance2**2 - real_station1_x**2 + real_station2_x**2 - real_station1_y**2 + real_station2_y**2)

    D = float(2 * (real_station3_x - real_station2_x))
    E = float(2 * (real_station3_y - real_station2_y))
    F = float(real_distance2**2 - real_distance3**2 - real_station2_x**2 + real_station3_x**2 - real_station2_y**2 + real_station3_y**2)

    real_patient_x = (F*B - E*C) / (B*D - E*A)
    real_patient_y = (F*A - D*C) / (A*E - D*B)

    return real_patient_x, real_patient_y


# FCM 서버에 notification message 요청을 보내는 함수
# 환자 -> 의료진 호출 시
def send_from_patient_to_doctor_by_fcm_notification(patient_info: Patient, doctor_info: Profile):
    registration_token = 'd4e1AepQQBOZ6Vt17XLYBI:APA91bEv8cKSjS-2uBBqPco17SK1jg5R_3RnAAmCukEDljBWpiXK231kwwk3_9upUKUtQZJOUwtIRRtu504F-glNe20Fe11Q2mW-_TfoLhv4vvcFMwlHiJgRaDuIANnDsADnjmpgUOFU'

    # notification message sending
    message_noti = messaging.Message(
        notification=messaging.Notification(
            title='환자의 호출',
            body=f'{doctor_info.name} 선생님, {patient_info.name} 환자가 호출했습니다',
        ),
        token=registration_token,
    )
    response = messaging.send(message_noti)
    print('Successfully sent notification message(환자->의료진):', response)


# FCM 서버에 notification message 요청을 보내는 함수
# 의료진 -> 환자 호출 시
def send_from_doctor_to_patient_by_fcm_notification():
    registration_token = 'd4e1AepQQBOZ6Vt17XLYBI:APA91bEv8cKSjS-2uBBqPco17SK1jg5R_3RnAAmCukEDljBWpiXK231kwwk3_9upUKUtQZJOUwtIRRtu504F-glNe20Fe11Q2mW-_TfoLhv4vvcFMwlHiJgRaDuIANnDsADnjmpgUOFU'

    # notification message sending
    message_noti = messaging.Message(
        notification=messaging.Notification(
            title='호출한 환자의 위치 정보',
            body='호출한 환자의 위치 정보를 보려면 클릭하세요',
        ),
        token=registration_token,
    )
    response = messaging.send(message_noti)
    print('Successfully sent notification message(의료진->환자):', response)

# FCM 서버에 data message 요청을 보내는 함수
def send_from_patient_to_doctor_by_fcm_data(drawing_patient_x, drawing_patient_y, patient_info: Patient):
    registration_token = 'd4e1AepQQBOZ6Vt17XLYBI:APA91bEv8cKSjS-2uBBqPco17SK1jg5R_3RnAAmCukEDljBWpiXK231kwwk3_9upUKUtQZJOUwtIRRtu504F-glNe20Fe11Q2mW-_TfoLhv4vvcFMwlHiJgRaDuIANnDsADnjmpgUOFU'

    # data message sending
    message_data = messaging.Message(
        data={
            "id": f"{patient_info.id}",
            "image": f"{patient_info.image}",
            "x": f"{drawing_patient_x}",
            "y": f"{drawing_patient_y}"
        },
        token=registration_token,
    )
    response = messaging.send(message_data)
    print('Successfully sent data message:', response)
