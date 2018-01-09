# atriage

atriage is an extensible triage tool written in Python 3. It currently supports
afl-fuzz.

```
Usage: atriage [OPTIONS] COMMAND [ARGS]...

  A dumb afl-fuzz triage tool.

Options:
  --help  Show this message and exit.

Commands:
  asan         Capture ASAN exploitable output of latest...
  exploitable  Capture GDB exploitable output of latest...
  gather       Gather latest triaged crash files.
  info         Print information about the provided database...
  list         List latest triaged crash files.
  triage       Triage crash files from afl output directory.
```
