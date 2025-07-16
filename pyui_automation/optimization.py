import platform
import os
import multiprocessing
from typing import Optional, Dict, Any
import json
import threading
from pathlib import Path
import tempfile


class OptimizationManager:
    """Manages platform-specific optimizations and caching"""

    def __init__(self) -> None:
        """
        Initialize the OptimizationManager.

        Sets up platform-specific configurations, initializes the cache directory
        and element cache, and loads any existing cached data. Configures 
        platform-specific optimizations.
        """
        self.platform = platform.system().lower()
        self.cache_dir = self._get_cache_dir()
        self.element_cache = {}
        self.cache_lock = threading.Lock()
        self._load_cached_data()
        self._configure_platform_optimizations()

    def _get_cache_dir(self) -> Path:
        """
        Get platform-specific cache directory.

        Returns:
            Path object pointing to the cache directory
        """
        if self.platform == 'windows':
            base_dir = os.getenv('LOCALAPPDATA')
            if not base_dir:
                base_dir = os.path.expanduser('~/.cache')
        elif self.platform == 'darwin':
            base_dir = os.path.expanduser('~/Library/Caches')
        else:  # Linux
            xdg_cache = os.getenv('XDG_CACHE_HOME')
            if xdg_cache:
                base_dir = xdg_cache
            else:
                base_dir = os.path.expanduser('~/.cache')

        cache_dir = Path(base_dir) / 'pyui_automation'
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, FileNotFoundError):
            # Fallback to temp directory if we can't create in the default location
            cache_dir = Path(tempfile.gettempdir()) / 'pyui_automation'
            cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def _configure_platform_optimizations(self):
        """
        Configure platform-specific optimizations.

        This method sets up platform-specific optimization flags and
        initializes any platform-specific optimization data. The
        following optimizations are currently available:

        - `use_multiprocessing`: If the current platform has more than
          one CPU core available, enable multiprocessing in the
          automation framework.
        - `cache_enabled`: Enable the element cache.
        - `threading_enabled`: Enable threading in the automation
          framework.

        Platform-specific optimizations are also configured
        accordingly. For example, on Windows, process priority is
        enabled to reduce the chance of the automation process being
        interrupted by the system.
        """
        self.optimizations = {
            'use_multiprocessing': multiprocessing.cpu_count() > 1,
            'cache_enabled': True,
            'threading_enabled': True
        }

        if self.platform == 'windows':
            self._configure_windows_optimizations()
        elif self.platform == 'darwin':
            self._configure_macos_optimizations()
        else:  # Linux
            self._configure_linux_optimizations()

    def _configure_windows_optimizations(self):
        """Configure Windows-specific optimizations"""
        self.optimizations.update({
            'process_priority': True,
            'enable_dpi_awareness': True,
            'use_win32_hooks': True
        })

    def _configure_macos_optimizations(self):
        """Configure macOS-specific optimizations"""
        self.optimizations.update({
            'process_priority': True,
            'enable_accessibility': True
        })

    def _configure_linux_optimizations(self):
        """Configure Linux-specific optimizations"""
        self.optimizations.update({
            'process_priority': True,
            'enable_x11_integration': True
        })

    def cache_element(self, element_id: str, element_data: Dict[str, Any], ttl: Optional[int] = 300) -> None:
        """
        Cache element data with a timestamp and TTL.

        Args:
            element_id: Unique identifier for the element
            element_data: Data to cache
            ttl: Time-to-live in seconds. None means no expiration.
        """
        with self.cache_lock:
            self.element_cache[element_id] = element_data

    def get_cached_element(self, element_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached element data for the given element_id.

        Args:
            element_id: The unique identifier of the element to retrieve.

        Returns:
            The cached element data if found, or None otherwise.
        """
        with self.cache_lock:
            return self.element_cache.get(element_id)

    def clear_cache(self):
        """
        Clear all cached data

        This method clears the in-memory cache and saves the cleared cache to disk.
        """
        # Clear the cache and save in a single lock acquisition
        with self.cache_lock:
            self.element_cache.clear()
            cache_file = self.cache_dir / 'element_cache.json'
            try:
                with open(cache_file, 'w') as f:
                    json.dump(self.element_cache, f)
            except (IOError, OSError):
                pass  # Ignore write errors

    def _load_cached_data(self) -> None:
        """Load cached data from disk"""
        cache_file = self.cache_dir / 'element_cache.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.element_cache = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.element_cache = {}

    def save_cache(self) -> None:
        """Save the current element cache to disk"""
        with self.cache_lock:
            cache_file = self.cache_dir / 'element_cache.json'
            try:
                with open(cache_file, 'w') as f:
                    json.dump(self.element_cache, f)
            except (IOError, OSError):
                pass  # Ignore write errors

    def get_optimization(self, key: str) -> Any:
        """
        Get the value of a specific optimization setting.

        Args:
            key: The key representing the optimization setting to retrieve.

        Returns:
            The value associated with the specified optimization key, or None
            if the key does not exist in the optimizations dictionary.
        """
        return self.optimizations.get(key)

    def set_optimization(self, key: str, value: Any):
        """
        Set optimization setting value

        Args:
            key: The key representing the optimization setting to set.
            value: The value to set for the specified optimization setting.

        This method sets the value of the specified optimization setting.
        """
        self.optimizations[key] = value

    def optimize_process(self, process_id: Optional[int] = None) -> None:
        """
        Apply platform-specific optimizations to a process.

        Args:
            process_id: The ID of the process to optimize. If None, optimizes the current process.
        """
        try:
            import psutil
            process_id = process_id if process_id is not None else os.getpid()
            
            if self.platform == 'windows':
                try:
                    process = psutil.Process(process_id)
                    process.nice(psutil.HIGH_PRIORITY_CLASS)
                except psutil.NoSuchProcess:
                    pass
        except ImportError:
            pass

        if self.platform in ('darwin', 'linux'):
            try:
                os.nice(-10)  # Set higher priority on Unix-like systems
            except OSError:
                pass

    def configure_platform_optimizations(self, **kwargs) -> None:
        """
        Configure platform-specific optimization settings.

        Args:
            **kwargs: Optimization settings to configure. Valid keys are:
                     - use_multiprocessing (bool): Enable/disable multiprocessing
                     - cache_enabled (bool): Enable/disable element caching
                     - threading_enabled (bool): Enable/disable threading
        """
        for key, value in kwargs.items():
            if key in self.optimizations:
                self.optimizations[key] = value

        # Update platform-specific settings
        if self.platform == 'windows':
            self._configure_windows_optimizations()
        elif self.platform == 'darwin':
            self._configure_macos_optimizations()
        else:
            self._configure_linux_optimizations()

    @property
    def platform_config(self) -> Dict[str, Any]:
        """
        Get current platform optimization configuration.

        Returns:
            Dict containing current optimization settings
        """
        return {
            'platform': self.platform,
            'optimizations': self.optimizations,
            'cache_enabled': self.optimizations.get('cache_enabled', True),
            'threading_enabled': self.optimizations.get('threading_enabled', True),
            'use_multiprocessing': self.optimizations.get('use_multiprocessing', False)
        }
