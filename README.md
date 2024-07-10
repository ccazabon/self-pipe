# The Unix Self-Pipe Trick

This tiny package implements djb's "self-pipe trick" [^1].

Catching ("handling") Unix signals as a means of receiving asynchronous
notifications of events in a long-lived process, while commonly used, is fraught
with difficulties.  Signal handling is racy, the code used in the handler has
many restrictions which aren't enforced by the compiler or platform C library
but which can cause catastrophic errors which are essentially impossible to
debug.  Handling them in a program with an event loop is particularly tricky.

The "trick" is is a simple way to safely catch Unix signals and be notified that
they have been received, without running into any of the complex issues that
surround signals and signal handlers - things like how you can't safely call
most other code from within a signal handler, and how the rest of your code,
particularly event loops, can break badly as a result.

[^1]: See https://cr.yp.to/docs/selfpipe.html for the inventor's very brief
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
See https://cr.yp.to/export.html for additional information.

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
