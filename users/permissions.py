# users/permissions.py
from rest_framework import permissions


class CustomReadOnly(permissions.BasePermission):
    # 프로필 전체를 건드리는 요청이 아닌
    # 각 객체에 대한 요청만 있으므로
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  # 데이터에 영향을 미치지 않는 메소드 (예를 들면 GET)
            return True
        return request.user == obj.user  # PUT, PATCH 같은 경우는 요청 유저와 객체 유저를 비교
