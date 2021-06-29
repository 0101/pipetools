
1.0.0
----------
2021-06-29

* Package classified as stable


0.3.6
----------
2020-10-21

* Fix import for Python >= 3.9 (#16)


0.3.5
----------
2019-12-01

* Fixed X object division in Python 3


0.3.4
----------
2018-06-13

* Fixed UnicodeDecodeError during installation


0.3.3
----------
2018-05-30

* Added take_until.including


0.3.2
----------
2018-05-26

* No crash in Python 2 when partially applying a non-standard callable
* Regex conditions ignore None instead of throwing an exception
* maybe can be inserted in the middle of a pipe without parentheses


0.3.1
----------
2018-03-23

* Added tee util
* flatten will leave dictionaries (Mappings) alone


0.3.0
----------
2016-08-03

* added Python 3 support


0.2.7
----------
2014-03-19

* fixed checking if objects are iterable


0.2.6
----------
2013-09-02

* removed pipe_exception_handler (did more harm than good most of the time)


0.2.5
----------
2013-08-13

* Maybe returns None when called with None
* not calling repr() on stuff if we don't need to


0.2.4
----------
2013-07-13

* added drop_first
* fixed unicode formatting problem


0.2.3
----------
2013-04-24

* added sort_by.descending
* group_by returns item iterator instead of a dictionary


0.2.2
----------
2013-04-16

* X objects create bound methods on classes
* added support for X division


0.2.1
----------
2013-02-10

* added automatic regex conditions
* renamed xcurry to xpartial (turns out currying is something else)


0.2.0
----------
2012-11-14

* added support for X >=, <=, - and ** operations
* fixed static item handling in ds_builder


0.1.9
----------
2012-11-05

* added xcurry
* improved XObject naming


0.1.8
----------
2012-10-31

* added as_kwargs
* added take_until
* X object implicit piping (without ~)
* fixed naming X-objects so it doesn't fail with tuples

0.1.7
----------
2012-10-25

* friendlier debugging
* added changelog
