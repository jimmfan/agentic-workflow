# Accepted export design

The project owner approved these choices for the local export command.
Input is UTF-8 JSON lines from stdin, output is UTF-8 CSV on stdout with account,cents header.
Malformed input fails with exit 2 and a line number on stderr.
No partial output may escape on failure.
The command aggregates cents by account and emits accounts in ascending lexical order.
Memory buffering is accepted for at most 10000 input rows; row 10001 fails with exit 2.
No network access, configuration file or streaming-output redesign is in scope.
