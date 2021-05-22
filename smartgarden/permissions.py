from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsCircuitOwnerOnUnsafeOperations(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return view.circuit.owner.pk == request.user.pk

    def has_object_permission(self, request, view, obj):
        return view.circuit.owner.pk == obj.pk


class IsCircuitCollaboratorOnUnsafeOperations(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return view.circuit.collaborators.filter(pk=request.user.pk).exists()

    def has_object_permission(self, request, view, obj):
        return view.circuit.owner.pk == obj.pk
