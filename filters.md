# How do we even filter?

It's a tree, let's explore it:

* Is the operation of this filter "NOOP"?
  * Is the simple_filter defined?
    * Evaluate the simple filter with its evaluation function
    * Return the result of the simple filter
  * else
    * Throw exception, cancelling the filtering
* else
  * Evaluate left and right subtrees
  * Return the LEFT OP RIGHT
