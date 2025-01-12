import os
import sys

import sgtk

logger = sgtk.platform.get_logger(__name__)


def get_vendors_path():
    """
    Return the path to the vendors folder.

    The vendors folder is a way to package the dependencies of this framework
    in a "It just works" manner.

    Returns:
        str: The path to the vendors
    """

    return os.path.abspath(os.path.join(os.path.dirname(__file__), "vendor"))


def patch_environment():
    """
    This function patch the python path to add the required modules to the
    python path.
    """
    # Try to import websocket to see if we are good to go.

    vendor_path = get_vendors_path()

    logger.debug(f"Adding {vendor_path} to the python path")
    if vendor_path not in sys.path:
        sys.path.insert(0, vendor_path)

    bin_path = os.path.join(vendor_path, "bin")
    logger.debug(f"Adding {bin_path} to the path")
    if bin_path not in os.environ["PATH"]:
        sgtk.util.append_path_to_env_var("PATH", bin_path)


def unpatch_environment():
    """
    Removes the vendors path from the python path.
    """
    vendor_path = get_vendors_path()
    if vendor_path in sys.path:
        sys.path.remove(vendor_path)

    # Remove vendor_path from PATH environment variable
    bin_path = os.path.join(vendor_path, "bin")
    path_elements = os.environ["PATH"].split(os.pathsep)
    if bin_path in path_elements:
        path_elements.remove(bin_path)
        os.environ["PATH"] = os.pathsep.join(path_elements)


class FfmpegFramework(sgtk.platform.Framework):
    def init_framework(self):
        """
        Implemented by deriving classes in order to initialize the app.
        Called by the engine as it loads the framework.
        """
        self.log_debug(f"{self}: Initializing...")
        patch_environment()

    def destroy_framework(self):
        """
        Implemented by deriving classes in order to tear down the framework.
        Called by the engine as it is being destroyed.
        """
        self.log_debug(f"{self}: Destroying...")
        unpatch_environment()
