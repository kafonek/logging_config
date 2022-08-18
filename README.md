Example of configuring logging to structure log messages that are emitted from `structlog.get_logger` and `logging.getLogger` loggers the same way. Structlog documentation covers most of this at https://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging, but I wanted a repo to get hands-on and tweak options.

 - Implement the logging config pattern from structlog docs
 - Vanilla and Structlog loggers both get pre-processed slightly differently
 - Most logging config is handled in a shared_processors list
 - Custom logging, such as adding ddtrace span/trace ids into the event dict can go in shared_processors
 - Includes showing `extra` in vanilla logging, and kwargs in structlog logging
 - Includes showing `aiodebug` slow task warnings
 - Outputs to both console (colored, human readable) and file (json format)


 ## Use

  - `python run.py`
  - Watch console output
  - `cat test.log` to see JSON format

## Console output (uncolored)

```
❯ python run.py
2022-08-18 12:06:54 [debug    ] ADDING 2 + 3                   [log_test.log_stuff] contextfoo=bar dd.env= dd.service= dd.span_id=13555137062073999976 dd.trace_id=14280659572874161413 dd.version= filename=log_stuff.py func_name=add lineno=11
2022-08-18 12:06:54 [info     ] ADDING 2 + 3                   [log_test.log_stuff] contextfoo=bar dd.env= dd.service= dd.span_id=13555137062073999976 dd.trace_id=14280659572874161413 dd.version= filename=log_stuff.py for=eli func_name=add lineno=12
2022-08-18 12:06:54 [warning  ] ADDING 2 + 3                   [log_test.log_stuff] contextfoo=bar dd.env= dd.service= dd.span_id=13555137062073999976 dd.trace_id=14280659572874161413 dd.version= filename=log_stuff.py func_name=add lineno=13
Adding: add(2, 3)=5
2022-08-18 12:06:54 [info     ] MULTIPLYING 2 * 3              [log_test.structlog_stuff] contextfoo=bar dd.env= dd.service= dd.span_id=13555137062073999976 dd.trace_id=14280659572874161413 dd.version= filename=structlog_stuff.py func_name=multiply lineno=11
2022-08-18 12:06:54 [warning  ] MULTIPLYING 2 * 3              [log_test.structlog_stuff] contextfoo=bar dd.env= dd.service= dd.span_id=13555137062073999976 dd.trace_id=14280659572874161413 dd.version= filename=structlog_stuff.py func_name=multiply lineno=12
2022-08-18 12:06:54 [error    ] unsupported operand type(s) for +: 'int' and 'str' [log_test.structlog_stuff] contextfoo=bar dd.env= dd.service= dd.span_id=13555137062073999976 dd.trace_id=14280659572874161413 dd.version= filename=structlog_stuff.py func_name=multiply lineno=16 x=2
Traceback (most recent call last):
  File "/home/kafonek/log_test/log_test/structlog_stuff.py", line 14, in multiply
    x + "foo"
TypeError: unsupported operand type(s) for +: 'int' and 'str'
Multiplying: multiply(2, 3)=6
2022-08-18 12:06:54 [info     ] DIVIDING 2 / 3                 [log_test.structlog_stdlib] contextfoo=bar dd.env= dd.service= dd.span_id=13555137062073999976 dd.trace_id=14280659572874161413 dd.version= filename=structlog_stdlib.py func_name=divide lineno=14
2022-08-18 12:06:54 [warning  ] DIVIDING 2 / 3                 [log_test.structlog_stdlib] contextfoo=bar dd.env= dd.service= dd.span_id=13555137062073999976 dd.trace_id=14280659572874161413 dd.version= filename=structlog_stdlib.py func_name=divide lineno=15
2022-08-18 12:06:54 [error    ] division by zero               [log_test.structlog_stdlib] contextfoo=bar dd.env= dd.service= dd.span_id=13555137062073999976 dd.trace_id=14280659572874161413 dd.version= filename=structlog_stdlib.py func_name=divide lineno=19 x=2
Traceback (most recent call last):
  File "/home/kafonek/log_test/log_test/structlog_stdlib.py", line 17, in divide
    x / 0
ZeroDivisionError: division by zero
Dividing: div=0.6666666666666666
2022-08-18 12:06:55 [warning  ] Task blocked async loop for too long [aiodebug.slow_tasks] dd.env= dd.service= dd.span_id=0 dd.trace_id=0 dd.version= duration=1.0198359040077776 filename=logging_utils.py func_name=<lambda> lineno=36 task_name=<Task finished name='Task-1' coro=<run() done, defined at <string>:17> result=None>
```