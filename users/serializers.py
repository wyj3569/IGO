# users/serializers.py
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

from .models import Hospital, Profile, Patient


# 의료진 회원가입
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email')

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],  # 이메일에 대한 중복 검증
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],  # 비밀번호에 대한 검증
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )

    def validate(self, data):  # 추가적으로 비밀번호 일치 여부 확인
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):  # CREATE 요청에 대해 create 메소드를 오버라이딩, 유저를 생성하고 토큰을 생성
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
        )

        user.set_password(validated_data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return user


# 의료진 로그인
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user:
            token = Token.objects.get(user=user)  # 토큰에서 유저 찾아 응답
            return token
        raise serializers.ValidationError({"error": "Unable to log in with provided credentials."})


# 병원 전체 조회
class HospitalREADAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ('id', 'name')


# 병원 1개 조회
class HospitalREADOneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = (
            'id',
            'name',
            'drawing',
            'drawing_x',
            'drawing_y',
            'drawing_station1_x',
            'drawing_station1_y',
            'drawing_station2_x',
            'drawing_station2_y',
            'drawing_station3_x',
            'drawing_station3_y',
            'real_x',
            'real_y',
            'real_station1_x',
            'real_station1_y',
            'real_station2_x',
            'real_station2_x',
            'real_station3_x',
            'real_station3_x',
        )


# 의료진 프로필 조회
class ProfileREADSerializer(serializers.ModelSerializer):
    hospital = HospitalREADAllSerializer(read_only=True)  # 병원 정보는 id와 이름만 보여주면 된다

    class Meta:
        model = Profile
        fields = ('user', 'hospital', 'name', 'subjects')


# 의료진 프로필 수정
class ProfileUPDATESerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('name', 'subjects', 'hospital')


# 환자 1명 생성
class PatientCREATESerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('profile', 'name', 'gender', 'age', 'blood_type', 'blood_rh', 'disease', 'extra', 'image')


# 환자 전체 조회, 환자 1명 조회
class PatientREADSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'name', 'gender', 'age', 'blood_type', 'blood_rh', 'disease', 'extra', 'image')


# 환자 1명 수정
class PatientUPDATESerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('name', 'gender', 'age', 'blood_type', 'blood_rh', 'disease', 'extra', 'image')
