# The Unix Self-Pipe Trick

This tiny package implements the Unix "self-pipe trick" [^1], as popularized
by djb.

Catching ("handling") Unix signals as a means of receiving asynchronous
notifications of events in a long-lived process, while commonly used, is fraught
with difficulties.  Signal handling is racy, the code used in the handler has
many restrictions which aren't enforced by the compiler or platform C library
but which can cause catastrophic errors which are essentially impossible to
debug.  Handling them in a program with an event loop is particularly tricky.

As an example, a signal handler can be called in the middle of any other code,
such as a library function, interrupting its execution.  If anything in the 
signal handler calls that function - or calls something which calls that 
function, ad infinitum - then that function must be fully re-entrant, or else
it will corrupt the internal state of that interrupted call to it.  When the
signal handler returns and the interrupted function resumes, you're likely to
get a crash or corrupted data that is extremely non-obvious to diagnose.

Quick, do you know every platform / C library function, where all their callers
are, and whether each one is fully re-entrant or not?  Me, neither.  But it
eliminates a huge swathe of them, such as memory allocation.

The "trick" is is a simple way to safely catch Unix signals and be notified that
they have been received, without running into any of the complex issues that
surround signals and signal handlers - things like the above.

[^1]: See https://cr.yp.to/docs/selfpipe.html for the djb's very brief
description, and 
https://skarnet.org/software/skalibs/libstddjb/selfpipe.html
for a little more discussion of the issues involved.

## Use

To use the self-pipe trick in your long-lived program's event loop, do the
following.

1. Create a single instance of the `self_pipe.SelfPipe` class and keep a
   reference to it in your program or main object.  Construct it by passing a
   list of 1 or more signals you want your program to catch.
2. In your event loop, call `SelfPipe.poll()` on this instance.  If a signal has
   been received since the previous call to `poll()`, it will be returned in the
   format of a `signal.Signals` enum instance.  Otherwise, the result is `None`.
3. If multiple signals are received, polling will return them one at a time, in
   the order they were received.
4. You can supply an optional timeout value to `poll()` to cause the process to
   sleep and await a signal rather than immediately returning `None`.

If you're using multiple threads, all calls to create or use this object must be
done from the main thread.

Note that not all signals can be caught and handled, and some do not make sense
to catch.  See the Python standard library documentation for the signal module,
and `man 7 signal` for details on individual signals.

## Example code

Here's an example of using `SelfPipe` in the event loop of a Python
application, catching 3 signals and performing different actions based on
which one was received.

```python

import signal

from self_pipe import SelfPipe


class Server:
    def __init__(self, ...):
        self.exit_asap = False
        self.self_pipe = SelfPipe([
            # Signals we want to catch and be notified of
            signal.Signals.SIGTERM,
            signal.Signals.SIGQUIT,
            signal.Signals.SIGALRM,
        ])
        
    def process_signal(self, sig: signal.Signals) -> None:
        if sig is signal.Signals.SIGTERM:
            # Cause an orderly exit
            self.exit_asap = True
        elif sig is signal.Signals.SIGQUIT:
            # Cause an immediate exit
            self.kill_child_processes()
            raise SystemExit("received SIGQUIT")
        elif sig is signal.Signals.SIGALRM:
            # Log current status
            self.log_status()
        else:
            # This isn't necessary, but belt-and-braces ...
            raise ValueError(f"unexpected signal {sig}")

    def main(self):
        "Main event loop."
        while True:
            # See if we caught a signal since last time through the loop
            if sig := self.self_pipe.poll():
                self.process_signal(sig)
            if self.exit_asap:
                self.do_orderly_exit()
            #else:
            self.do_work()  # whatever your program does

            # sleep a bit or whatever before next loop iteration
```

That's all.

## Who is this "djb" guy, anyway?

Daniel J. Bernstein, a professor of mathematics and computer science at the 
University of Illinois at Chicago, among many other math, number theory,
cryptography, software, and other accomplishments.

Even if you are not active in these academic or scientific fields yourself, his 
work has affected your life; he is the Bernstein in the US Supreme Court case
Bernstein v. United States.  He's responsible for your web browser having
strong encryption, to protect your banking, shopping, personal communications,
reading, privacy, and other critical tasks.  He's also largely responsible for 
open-source software being able to include strong encryption, so everything
used in implementing the other end of those browser sessions, and much else,
also owes its secure communications to him.

See https://cr.yp.to/export.html 
and https://en.wikipedia.org/wiki/Bernstein_v._United_States
for additional information on Bernstein v. United States.

He's a respected cryptography researcher, and responsible for the Curve25519
elliptic-curve used in much modern cryptography (including SSH and other uses).
He has also published extremely fast software implementations of this curve
and others.

In addition, he has published a large quantity of extremely secure, performant
system software, including qmail, djbdns/dnscache, daemontools, ezmlm, mess822,
USCPI/ucspi-tcp, and others.

## Copyright / License

Copyright ©2024 by Charles Cazabon <charlesc-software-selfpipe@pyropus.ca>.

This is open-source/Free Software under the GNU General Public License version 2
(only).

See the file COPYING for details.
