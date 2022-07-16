import time
import threading
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is
    available.
    """
    def __init__(self):
        self.events = {}

    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        ident = get_ident()
        if ident not in self.events:
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Invoked by the camera thread when a new frame is available."""
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                event[0].set()
                event[1] = now
            else:
                if now - event[1] > 15:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        self.events[get_ident()][0].clear()


class BaseCamera(object):
    thread = {}  # background thread that reads frames from camera
    frame = {}  # current frame is stored here by background thread
    last_access = {}  # time of last client access to the camera
    event = {}

    def __init__(self, camera_type=None, device=None):
        """Start the background camera thread if it isn't running yet."""
        self.unique_name = "{cam}_{dev}".format(cam=camera_type, dev=device)
        BaseCamera.event[self.unique_name] = CameraEvent()
        if self.unique_name not in BaseCamera.thread:
            BaseCamera.thread[self.unique_name] = None
        if BaseCamera.thread[self.unique_name] is None:
            BaseCamera.last_access[self.unique_name] = time.time()

            # start background frame thread
            BaseCamera.thread[self.unique_name] = threading.Thread(target=self._thread, args=(self.unique_name,))
            BaseCamera.thread[self.unique_name].start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        """Return the current camera frame."""
        BaseCamera.last_access[self.unique_name] = time.time()

        # wait for a signal from the camera thread
        BaseCamera.event[self.unique_name].wait()
        BaseCamera.event[self.unique_name].clear()

        return BaseCamera.frame[self.unique_name]

    @staticmethod
    def frames():
        """"Generator that returns frames from the camera."""
        raise RuntimeError('Must be implemented by subclasses')

    @classmethod
    def _thread(cls, unique_name):
        """Camera background thread."""
        print('Starting camera thread')
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            BaseCamera.frame[unique_name] = frame
            BaseCamera.event[unique_name].set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 5 seconds then stop the thread
            if time.time() - BaseCamera.last_access[unique_name] > 30:
                frames_iterator.close()
                print('Stopping camera thread due to inactivity')
                break
        BaseCamera.thread[unique_name] = None
