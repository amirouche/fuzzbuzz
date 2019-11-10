# fuzzbuzz

**experimental use at your own risks**

```ascii
 _____
_/ ____\_ __________________
\   __\  |  \___   /\___   /
 |  | |  |  //    /  /    /
 |__| |____//_____ \/_____ \
                  \/      \/
___.
\_ |__  __ __________________
 | __ \|  |  \___   /\___   /
 | \_\ \  |  //    /  /    /
 |___  /____//_____ \/_____ \
     \/            \/      \/
```

fuzzy hash and distance for short strings.

```python
In [1]: import fuzzbuzz

In [2]: fuzzbuzz.hamming2(fuzzbuzz.simhash('obama'), fuzzbuzz.simhash('barack obama'))
Out[2]: 16

In [3]: fuzzbuzz.hamming2(fuzzbuzz.simhash('obama'), fuzzbuzz.simhash('trump'))
Out[3]: 30

In [4]: fuzzbuzz.hamming2(fuzzbuzz.simhash('concept'), fuzzbuzz.simhash('concpet'))
Out[4]: 22

In [5]: fuzzbuzz.hamming2(fuzzbuzz.simhash('concept'), fuzzbuzz.simhash('concept'))
Out[5]: 0

In [6]: fuzzbuzz.hamming2(fuzzbuzz.simhash('concept'), fuzzbuzz.simhash('concept car'))
Out[6]: 11

In [7]: fuzzbuzz.hamming2(fuzzbuzz.simhash('concept'), fuzzbuzz.simhash('quality'))
Out[7]: 30

In [8]: fuzzbuzz.hamming2(fuzzbuzz.simhash('quality assurance'), fuzzbuzz.simhash('quality'))
Out[8]: 17
```
