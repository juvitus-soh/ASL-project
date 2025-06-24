# app/utils/permissions.py
"""
Mobile permissions management
"""

from kivy.utils import platform


class PermissionManager:
    """Manages mobile app permissions"""

    @staticmethod
    def request_camera_permission():
        """Request camera permission on mobile devices"""
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.CAMERA])
                return True
            except ImportError:
                print("Android permissions not available (running on desktop?)")
                return False
        else:
            # On desktop, camera permission is automatic
            return True

    @staticmethod
    def check_camera_permission():
        """Check if camera permission is granted"""
        if platform == 'android':
            try:
                from android.permissions import check_permission, Permission
                return check_permission(Permission.CAMERA)
            except ImportError:
                return True  # Assume granted on desktop
        else:
            return True

    @staticmethod
    def request_storage_permission():
        """Request storage permission for saving data"""
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE
                ])
                return True
            except ImportError:
                print("Android permissions not available")
                return False
        else:
            return True