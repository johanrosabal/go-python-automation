import threading

_singleton_local = threading.local()


class SingletonMeta(type):
    """
    A thread-safe implementation of the Singleton design pattern.

    Ensures that a class maintains only one active instance throughout the 
    application lifecycle per thread. This is primarily used for Page Objects to 
    maintain state consistency and prevent redundant object instantiations.

    Attributes:
        _instances (dict): A thread-local storage mapping classes to their 
            corresponding unique instances.
    """
    _instances = {}

    @classmethod
    def _get_registry(mcs) -> dict:
        if not hasattr(_singleton_local, "instances"):
            _singleton_local.instances = {}
        return _singleton_local.instances

    def __call__(cls, *args, **kwargs):
        """
        Intercepts the class instantiation call (constructor).

        If an instance of the class already exists in the registry, it is 
        returned immediately. Otherwise, a new instance is created and cached.

        Returns:
            object: The unique instance of the calling class.
        """
        registry = SingletonMeta._get_registry()
        if cls not in registry:
            instance = super().__call__(*args, **kwargs)
            registry[cls] = instance
            SingletonMeta._instances[cls] = instance
        return registry[cls]

    @classmethod
    def clear_instances(mcs):
        """
        Purges all cached Singleton instances from the registry.

        This method is critical between test iterations to ensure that 
        Page Objects are re-initialized with the current session's WebDriver context.
        """
        _singleton_local.instances = {}
        mcs._instances = {}
