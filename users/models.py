# users/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# 병원 모델
class Hospital(models.Model):
    # 병원 이름
    name = models.CharField(max_length=100, default="")
    # 병원 도면 사진
    drawing = models.URLField(max_length=1000, default="")
    # 병원 도면 사진 크기
    drawing_x = models.IntegerField(default=0)
    drawing_y = models.IntegerField(default=0)
    # 병원 도면 사진 위에서 기지국의 위치
    # 기지국 1
    drawing_station1_x = models.IntegerField(default=0)
    drawing_station1_y = models.IntegerField(default=0)
    # 기지국 2
    drawing_station2_x = models.IntegerField(default=0)
    drawing_station2_y = models.IntegerField(default=0)
    # 기지국 3
    drawing_station3_x = models.IntegerField(default=0)
    drawing_station3_y = models.IntegerField(default=0)
    # 기지국 4
    drawing_station4_x = models.IntegerField(default=0)
    drawing_station4_y = models.IntegerField(default=0)

    # 병원 실제 크기
    real_x = models.IntegerField(default=0)
    real_y = models.IntegerField(default=0)
    # 병원 실제 기지국의 위치
    # 기지국 1
    real_station1_x = models.IntegerField(default=0)
    real_station1_y = models.IntegerField(default=0)
    # 기지국 2
    real_station2_x = models.IntegerField(default=0)
    real_station2_y = models.IntegerField(default=0)
    # 기지국 3
    real_station3_x = models.IntegerField(default=0)
    real_station3_y = models.IntegerField(default=0)
    # 기지국 4
    real_station4_x = models.IntegerField(default=0)
    real_station4_y = models.IntegerField(default=0)

    def __str__(self):
        return f'병원 이름 : {self.name}'


# 의료진 프로필 모델
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # 소속 병원
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, default=1)
    # 의료진 이름
    name = models.CharField(max_length=100, default="")
    # 의료진 전공
    subjects = models.CharField(max_length=100, default="")

    def __str__(self):
        return f'의료진 이름 : {self.name} / 전공 : {self.subjects} / 소속 병원 : {self.hospital.name}'


# User 모델이 post_save 이벤트를 발생시켰을 때, 해당 이벤트가 일어났다는 사실을 받아서
# 해당 유저 인스턴스와 연결되는 프로필 데이터를 생성
# @receiver 덕분에 프로필을 생성하는 코드를 직접 작성하지 않아도
# 알아서 유저 생성 이벤트를 감지해서 프로필을 자동으로 생성할 수 있다.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# 환자 모델
class Patient(models.Model):
    # 의료진 환자 일대다 관계, 의료진
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True)
    # 환자 이름
    name = models.CharField(max_length=50, default="")
    # 환자 성별 (True: 남성, False: 여성)
    gender = models.BooleanField(default=True)
    # 환자 나이
    age = models.IntegerField(default=0)
    # 환자 혈액형 (0: A형, 1: B형, 2: O형, 3: AB형)
    blood_type = models.IntegerField(default=0)
    # Rh+,- (True: Rh+, False: Rh-)
    blood_rh = models.BooleanField(default=True)
    # 질병
    disease = models.TextField(default="")
    # 기타 정보
    extra = models.TextField(default="")
    # 환자 사진 (1부터 5까지의 정수 중 하나)
    image = models.IntegerField(default=0)

    # 기지국 1과의 거리 값
    real_distance1 = models.FloatField(default=0.0)
    # 기지국 2와의 거리 값
    real_distance2 = models.FloatField(default=0.0)
    # 기지국 3과의 거리 값
    real_distance3 = models.FloatField(default=0.0)
    # 기지국 4와의 거리 값
    real_distance4 = models.FloatField(default=0.0)

    def __str__(self):
        return f'환자 이름 : {self.name} / 담당 의료진 : {self.profile.name}'
