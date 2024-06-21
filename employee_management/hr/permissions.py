# hr/permissions.py

from rest_framework.permissions import BasePermission

class IsHR(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'HR'

class IsProjectManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'ProjectManager'

class IsSelfOrHR(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and (request.user.role == 'HR' or obj.user == request.user)

class IsEmployeeSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user and obj == request.user
