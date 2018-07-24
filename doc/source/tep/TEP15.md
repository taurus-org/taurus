    Title: fragment-based slicing support in URIs
    TEP: 15
    State: ACCEPTED
    Date: 2016-06-16
    Drivers: Carlos Pascual-Izarra <cpascual@cells.es>
    URL: http://www.taurus-scada.org/tep?TEP15.md
    License: http://www.jclark.com/xml/copying.txt
    Abstract:
     This proposal aims at defining a way for Taurus URIs to support data slicing.



Introduction & motivation
=========================

A Taurus user may use a URI to identify a source of data which, when read is
resolved into an iterable object. A common request by Taurus users is to be
able to use URI fragments to refer to a particular index (or slice) of such
iterable data values.

Note that particular schemes may already provide access to slices of data
(i.e., a reference to an object that already is a slice of an iterable).
The particulars of how a given scheme supports that are out of the scope of this
TEP. This proposal is only concerned with the use of fragments for referencing
slices when the scheme provides an iterable object.

For example, at this moment, if we define the following URI:
`uri = "tango:sys/tg_test/1/wave#rvalue"`and we run `v = taurus.Attribute(uri).read()`,
the object `v` would be a Quantity object with shape (256,). The objective of
this proposal is to define a way to reference a certain slice of `v` via a fragment.

Implementation
===============

Three alternative syntaxes were proposed (see "Considered alternatives" section below).
Of them, the first one was chosen because it is the most pythonic one:

The proposed implementation involves refactoring TaurusModel.getFragmentObj so that
the fragment name can be used in a python evaluation of the type `eval('v.fragmentName')`

See more details in the implementation PR: https://github.com/taurus-org/taurus/pull/764


Considered alternatives
======================

Consider this example:

```
v = taurus.Attribute("eval:arange(5)").read()
```

We will now discuss different ways of referring to, e.g. `v[0:2]`

(note that we leave out the possibility of demanding it to the scheme itself as in `eval:arange(5)[0:2]`)


Using  brackets (python slices notation)
------------------------------------------------------

Note: This is the notation that was finally selected for implementation

One possibility is to use `"eval:arange(5)#rvalue[0:2]"`

This seems the most natural API given the current support for fragments: just as
`"eval:arange(5)#rvalue.magnitude` returns the magnitude of the rvalue, the slice
notation would return the slice.

The main drawback is that square brackets are **not** allowed by [RFC3986][] into the
fragment (or the path) of an URI unless they are percent-encoded.

Note that this problem also affects to the currently allowed use of reserved characters
in the path of the `eval` scheme.


Use a explicit slice function
-----------------------------------------

Note: This notation was **not** selected for implementation (the brackets one was chosen)

In the process of retrieving the fragment object from a model object, we could have a
reserved name for slices (e.g. `_slice(...)`) that would return `v[slice(...)]`:

 `"eval:arange(5)#_slice(0,2)"`
 `"eval:arange(5)#rvalue._slice(0,2)"`

Note that the arguments to `_slice` would be the same as for python's `slice()` class
constructor.

This does overcome the problem of using square brackets, but feels too verbose and much
less natural.

Also, the fact of using slice-type arguments (`start, stop, step`) instead of a slice
expression (`i:j:k`) makes it less intuitive.

Use of `@(...)`
-------------------

Note: This notation was **not** selected for implementation (the brackets one was chosen)

Use the python slice notation but with parenthesis instead of square brackets and using
some allowed character for conveying this special meaning (e.g., "@", "!", "?" or "&").
Just for this example I assume that the choice is "@":

`"eval:arange(5)#@(0:2)"`
 `"eval:arange(5)#rvalue@(0:2)"`
 
The use of parenthesis allows us to delimit  the start and end of the slice so that nested
fragments could still be used, e.g.:
 
 `"eval:arange(5)#rvalue@(0:2).magnitude"`

The use of the special character is desirable to avoid ambiguities if we ever support
method calling in fragments (not yet supported but foreseen).

This overcomes the isssue of the use of a reserved square bracket and is reasonably concise,
but it certainly seems less natural than the brackets.


License
==================

The following copyright statement and license apply to SEP3 (this
document).

Copyright (c) 2015 CELLS / ALBA Synchrotron, Bellaterra, Spain

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Changes
========
2018-07-24
[cpascual][] Move CANDIDATE to ACCEPTED  after voting on PR.

2018-06-18
[cpascual][] Move DRAFT to CANDIDATE  by proposing an implementation based on using square brackets.

2016-06-16
[cpascual][] First draft triggered by a [discussion about URIs][1] in the tauruslib-devel mailing list.

2016-11-16:
[mrosanes](https://github.com/sagiss/) Adapt TEP format and URL according TEP16

[cpascual]: http://sf.net/u/cpascual/
[RFC3986]: https://tools.ietf.org/html/rfc3986
[1]: https://sourceforge.net/p/tauruslib/taurus-devel/message/35184319/

