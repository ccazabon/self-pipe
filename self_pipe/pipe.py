"""
Copyright / License

This software is Copyright ©2024 by Charles Cazabon <charlesc-software-selfpipe@pyropus.ca>.
It is open-source/Free Software under the GNU General Public License version 2 (only).
See the file COPYING for details.
"""

__all__ = ["SelfPipe"]

import os
import select
import signal
from typing import Any


class SelfPipe:
    """A Python implementation of djb's `self-pipe trick`, focussed on simplicity and usability.

    Briefly: handling Unix signals in a long-lived process, while commonly used, is fraught
    with difficulties.  They're racy, the code used in the handler has many restrictions which
    aren't enforced by the compiler or platform C library but which can cause catastrophic
    errors which are essentially impossible to debug.  Handling them in a program with an event
    loop is particularly tricky.

    This class encapsulates all the difficulty and implements the One True Safe signal handling
    technique invented by djb (Daniel J. Bernstein) around 1990.

    To use:
        1. Create a single instance of this class and keep a reference to it in your program
           or main object.  Pass it a list of 1 or more signals you want to catch.
        2. In your event loop, call `.poll()` on this instance.  If a signal has been received
           since the previous call to poll(), it will be returned in the format of a
           signal.Signals enum instance.  Otherwise, the result is None.
        3. If multiple signals are received, polling will return them one at a time, in the
           order they were received.
        4. You can supply an optional timeout value to poll() to cause the process to sleep
           and await a signal rather than immediately returning None.

    If you're using multiple threads, all calls to create or use this object must be done from
    the main thread.
    """

    def __init__(self, sigs: list[signal.Signals]) -> None:
        """Constructor.  Create the pipe and register signals of interest to the caller.

        :param sigs: list of 1 or more signals to be caught and handled.  Values should be an
            instance of the signal.Signals enum class, e.g. signal.Signals.SIGTERM

        Note that not all signals can be caught and handled, and some that can nevertheless
        do not make sense to catch.  The Python interpreter also installs default signal
        handlers for some signals (particularly SIGINT and SIGPIPE).  See the stdlib
        documentation for the signal module, and `man 7 signal` for details on individual
        signals.
        """
        if not sigs:
            raise ValueError("no signals specified")

        self.pipe_fd_r, self.pipe_fd_w = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)

        for sig in sigs:
            signal.signal(sig, self.handle_signal)

    def handle_signal(self, signum: int, stack_frame: Any) -> None:
        """Signal handler method which uses the self-pipe trick to safely handle signals by
        doing as little as possible, only notifying the program that a signal was received.
        """
        assert signum
        written = os.write(self.pipe_fd_w, bytes([signum]))
        if written != 1:
            # Shouldn't happen.  If you're receiving so many signals that they queue up enough
            # to cause a nonblocking single-byte write to the pipe to fail, something is
            # wrong with your system, or you shouldn't be using signals for it at all.
            raise ValueError(f"wrote {written} bytes instead of 1")

    def poll(self, timeout: float | int = 0) -> signal.Signals | None:
        """Check to see if a signal was received since last check.  If timeout is supplied,
        wait up to that long for a signal if none is immediately available.

        This should be called from without your event loop.  It will return a maximum of one
        signal per call, in the order that the signals were received.

        :param timeout: How long to wait for a signal if none already received, or 0 for
            no wait.
        :returns signal.Signals enum instance for the signal that was received, or None if
            no signal has been received.
        """
        readable, _, _ = select.select([self.pipe_fd_r], [], [], timeout)
        if not readable:
            return None

        data = os.read(self.pipe_fd_r, 1)
        assert len(data) == 1, data

        signum = data[0]
        sig = signal.Signals(signum)

        return sig
