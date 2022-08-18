Example of configuring logging to structure log messages that are emitted from `structlog.get_logger` and `logging.getLogger` loggers the same way. Structlog documentation covers most of this at https://www.structlog.org/en/stable/standard-library.html#rendering-using-structlog-based-formatters-within-logging, but I wanted a repo to get hands-on and tweak options.

 - Implement the logging config pattern from structlog docs
 - Vanilla and Structlog loggers both get pre-processed slightly differently
 - Most logging config is handled in a shared_processors list
 - Custom logging, such as adding ddtrace span/trace ids into the event dict can go in shared_processors
 - Includes showing `extra` in vanilla logging, and kwargs in structlog logging
 - Includes showing `aiodebug` slow task warnings
 - Outputs to both console (colored, human readable) and file (json format)


 ## Use

  - `poetry install`
  - `poetry run python run.py`
  - Watch console output
  - `cat test.log` to see JSON format

## File layout
 - `run.py` is the entrypoint for the app
 - `log_test/logging_utils.py` has the configurations to make structlog and vanilla logging use the same processors
 - `log_test/add.py`, `divide.py`, and `multiply.py` have examples of functions emitting logs using different logger syntax

## Console output (uncolored)

```
og_test on  main [»+] is 📦 v0.1.0 via 🐍 v3.8.10 (.venv) 
❯ poetry run python run.py
2022-08-18 12:20:27 [info     ] ADDING 2 + 3                   [log_test.add] contextfoo=bar dd.env= dd.service= dd.span_id=8613874215176314636 dd.trace_id=10487725867832306117 dd.version= filename=add.py for=eli func_name=add lineno=12
2022-08-18 12:20:27 [warning  ] ADDING 2 + 3                   [log_test.add] contextfoo=bar dd.env= dd.service= dd.span_id=8613874215176314636 dd.trace_id=10487725867832306117 dd.version= filename=add.py func_name=add lineno=13
Adding: add(2, 3)=5
2022-08-18 12:20:27 [info     ] MULTIPLYING 2 * 3              [log_test.multiply] contextfoo=bar dd.env= dd.service= dd.span_id=8613874215176314636 dd.trace_id=10487725867832306117 dd.version= filename=multiply.py func_name=multiply lineno=12
2022-08-18 12:20:27 [warning  ] MULTIPLYING 2 * 3              [log_test.multiply] contextfoo=bar dd.env= dd.service= dd.span_id=8613874215176314636 dd.trace_id=10487725867832306117 dd.version= filename=multiply.py func_name=multiply lineno=13
2022-08-18 12:20:27 [error    ] unsupported operand type(s) for +: 'int' and 'str' [log_test.multiply] contextfoo=bar dd.env= dd.service= dd.span_id=8613874215176314636 dd.trace_id=10487725867832306117 dd.version= filename=multiply.py func_name=multiply lineno=17 x=2
Traceback (most recent call last):
  File "/home/kafonek/log_test/log_test/multiply.py", line 15, in multiply
    x + "foo"
TypeError: unsupported operand type(s) for +: 'int' and 'str'
Multiplying: multiply(2, 3)=6
2022-08-18 12:20:27 [info     ] DIVIDING 2 / 3                 [log_test.divide] contextfoo=bar dd.env= dd.service= dd.span_id=8613874215176314636 dd.trace_id=10487725867832306117 dd.version= filename=divide.py func_name=divide lineno=14
2022-08-18 12:20:27 [warning  ] DIVIDING 2 / 3                 [log_test.divide] contextfoo=bar dd.env= dd.service= dd.span_id=8613874215176314636 dd.trace_id=10487725867832306117 dd.version= filename=divide.py func_name=divide lineno=15
2022-08-18 12:20:27 [error    ] division by zero               [log_test.divide] contextfoo=bar dd.env= dd.service= dd.span_id=8613874215176314636 dd.trace_id=10487725867832306117 dd.version= filename=divide.py func_name=divide lineno=19 x=2
Traceback (most recent call last):
  File "/home/kafonek/log_test/log_test/divide.py", line 17, in divide
    x / 0
ZeroDivisionError: division by zero
Dividing: div=0.6666666666666666
2022-08-18 12:20:28 [warning  ] Task blocked async loop for too long [aiodebug.slow_tasks] dd.env= dd.service= dd.span_id=0 dd.trace_id=0 dd.version= duration=1.015958825009875 filename=logging_utils.py func_name=<lambda> lineno=36 task_name=<Task finished name='Task-1' coro=<run() done, defined at <string>:17> result=None>
```