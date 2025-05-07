import os
import sys

class PathResolver:
    @staticmethod
    def get_resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        # If not running in PyInstaller, use the user's home directory
        return os.path.join(PathResolver.get_home_dir(), relative_path)

    @staticmethod
    def get_home_dir():
        """Get the base .dockit directory path"""
        return os.path.expanduser("~/.dockit")

    @staticmethod
    def get_services_dir():
        """Get the services directory path"""
        return os.path.join(PathResolver.get_home_dir(), "services")

    @staticmethod
    def get_templates_dir():
        """Get the templates directory path"""
        return os.path.join(PathResolver.get_home_dir(), "templates")

    @staticmethod
    def get_predefined_services_path():
        """Get the path to predefined services"""
        try:
            # Try to get predefined services from PyInstaller
            return os.path.join(sys._MEIPASS, "services")
        except Exception:
            # If not running in PyInstaller, use the local services directory
            return os.path.join(os.path.dirname(os.path.dirname(__file__)), "services")

    @staticmethod
    def get_predefined_templates_path():
        """Get the path to predefined templates"""
        try:
            # Try to get predefined templates from PyInstaller
            return os.path.join(sys._MEIPASS, "templates")
        except Exception:
            # If not running in PyInstaller, use the local templates directory
            return os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates") 